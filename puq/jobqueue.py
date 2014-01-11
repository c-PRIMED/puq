"""
This file is part of PUQ
Copyright (c) 2013 PUQ Authors
See LICENSE file for terms.
"""

from collections import deque
from threading import Thread, Condition, Event
from logging import info, debug, exception, warning, critical

class JobQueue():
    def __init__(self, host, limit=200, polltime=300):
        self.host = host
        self.limit = limit
        self.stop = Event()
        self.polltime = polltime

        self.jq = deque()
        self.jqc = Condition()
        self.jqcount = 0

        self.wq = self.host.wqueue
        self.wlist = self.host.wlist
        self.wqc = Condition()

        self.t = Thread(target=self.submit_thread)
        self.t.daemon = True
        self.monitor = Thread(target=self.monitor_thread)
        self.monitor.daemon = True
        self.monitorc = Condition()

    def cleanup(self):
        debug('Cleaning up. Please wait')
        self.stop.set()
        with self.jqc:
            self.jqc.notify_all()
        with self.wqc:
            self.wqc.notify()
        with self.monitorc:
            self.monitorc.notify()
        self.t.join()
        self.monitor.join()

    def start(self):
        debug('WQ=%s' % self.wq)
        self.t.start()
        self.monitor.start()

    def join(self):
        while True:
            try:
                with self.jqc:
                    if self.jqcount:
                        self.jqc.wait(300)
                    if self.jqcount == 0:
                        break
            except KeyboardInterrupt:
                break
        self.cleanup()
        return self.wq

    def add(self, j):
        self.jqc.acquire()
        self.jq.append(j)
        self.jqcount += 1
        self.jqc.notify()
        self.jqc.release()

    def _submit(self, j):
        joblist = [j]
        wt = self.host.walltime_to_secs(j['walltime'])
        cmd = self.host.cmdline(j)
        if self.host.scaling:
            self.host.submit(cmd, joblist, wt)
            return
        cpu = self.host.cpus
        cpn = self.host.cpus_per_node
        cpu_left = cpn - cpu
        pack = self.host.pack
        walltime = 0
        next_cmd = False
        while pack > 0:
            while cpu_left == cpn or cpu_left >= cpu:
                try:
                    j = self.jq.pop()
                except IndexError:
                    pack = 0
                    break
                cpu_left -= cpu
                if next_cmd:
                    cmd += "\n" + self.host.cmdline(j)
                    next_cmd = False
                else:
                    cmd += "&\n" + self.host.cmdline(j)
                wt = max(wt, self.host.walltime_to_secs(j['walltime']))
                joblist.append(j)
            cmd += '&\nwait\n'
            walltime += wt
            next_cmd = True
            pack -= 1
            cpu_left = cpn
        job = self.host.submit(cmd, joblist, walltime)
        #print 'appending', job
        self.wq.append(job)

    # This thread gets jobs off the job queue and submits
    # them.
    def submit_thread(self):
        debug('starting submit_thread')
        while not self.stop.isSet():
            with self.jqc:
                while True:
                    try:
                        if self.stop.isSet():
                            return
                        j = self.jq.pop()
                        break
                    except IndexError:
                        self.jqc.wait()
                        continue
                    except:
                        return
            finished = False
            with self.wqc:
                while not finished and not self.stop.isSet():

                    if len(self.wq) < self.limit:
                        self._submit(j)
                        finished = True
                    else:
                        self.wqc.wait()
        debug('Exiting submit_thread')

    # This thread monitors the status of all submitted jobs.
    def monitor_thread(self):
        debug('starting monitor_thread')
        while not self.stop.isSet():
            # periodically check the status of all jobs on the queue
            finished = []
            with self.wqc:
                for jd in self.wq:
                    self.host.check(jd)
                    stat = jd['job_state']
                    if stat == 'F' or stat == 'X':
                        debug("Done with %s" % jd['jobid'])
                        finished.append(jd)
                if finished:
                    self.wqc.notify()
                for jd in finished:
                    self.wq.remove(jd)
                    self.wlist.append(jd)
                    # remove all tasks associated with this job
                    with self.jqc:
                        for j in jd['joblist']:
                            self.host.job_status(j)
                            self.jqcount -= 1
                            if self.jqcount == 0:
                                self.jqc.notify_all()
            with self.monitorc:
                self.monitorc.wait(self.polltime)
        debug('Exiting monitor_thread')
