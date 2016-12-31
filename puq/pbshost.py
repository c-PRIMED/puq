"""
This file is part of PUQ
Copyright (c) 2013-2016 PUQ Authors
See LICENSE file for terms.
"""

from __future__ import absolute_import, division, print_function

from logging import debug
from .hosts import Host
from .jobqueue import JobQueue
import time
import re, os, sys, subprocess
import numpy as np


class PBSHost(Host):
    """
    Queues jobs using the PBS batch scheduler.
    Supports Torque and PBSPro.

    Args:
      env(str): Bash environment script (.sh) to be sourced. Optional.
      cpus(int): Number of cpus each process uses. Required.
      cpus_per_node(int): How many cpus to use on each node.  Required.
      qname(str): The name of the queue to use.
      walltime(str): How much time to allow for the process to complete. Format
        is HH:MM:SS.  Default is 1 hour.
      modules(list): Additional required modules. Default is none.
      pack(int): Number of sequential jobs to run in each PBS script. Default is 1.
      qlimit(int): Max number of PBS jobs to submit at once. Default is 200.
    """

    def __init__(self, env='',  cpus=0, cpus_per_node=0,
                 qname='standby', walltime='1:00:00', modules='', pack=1, qlimit=200):
        Host.__init__(self)
        if cpus <= 0:
            print("You must specify cpus when creating a PBSHost object.")
            raise ValueError
        if cpus_per_node <= 0:
            print("You must specify cpus_per_node when creating a PBSHost object.")
            raise ValueError
        if env:
            try:
                fd = open(env, 'r')
                fd.close()
            except IOError as e:
                print()
                print("Trying to read environment script '%s'" % env)
                print("I/O error(%s): %s" % (e.errno, e.strerror))
                print()
                sys.exit(1)
        self.env = env
        self.cpus = cpus
        self.cpus_per_node = cpus_per_node
        self.qname = qname
        self.walltime = walltime
        self.jobs = []
        self.wqueue = []
        self.wlist = []
        self.modules = modules
        self.pack = pack
        self.scaling = False
        self.jnum = 0
        self.qlimit = qlimit
        # checkjob on Carter is frequently broken
        # self.has_checkjob = (os.system("/bin/bash -c 'checkjob --version 2> /dev/null'") >> 8) == 0
        self.has_checkjob = False
        self.has_torque = os.path.isdir('/var/spool/torque')

    @staticmethod
    def job_status(j):
        j['status'] = 'F'

    @staticmethod
    def checkjob(d):
        quiet = False

        cmd = "checkjob -A %s" % d['jobid']
        print('cmd=%s' % cmd)
        so = file('/dev/null')
        st = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=so).stdout
        so.close()

        str = st.read().rstrip().rstrip(';')
        if not str:
            return

        d = dict(x.split('=') for x in str.split(';'))

        if not quiet:
            etime = int(d['STARTTIME'])
            if etime:
                etime = int(time.time()) - int(etime)
            etime = Host.secs_to_walltime(etime)
            wtime = Host.secs_to_walltime(d['WCLIMIT'])
            print("%s %8s %10s %10s %10s" % (d['NAME'], d['RCLASS'], d['STATE'], wtime, etime))

        # Idle, Started, Running, Completed, or Removed
        _state = d['STATE']
        if _state == 'Idle' or _state == 'Starting':
            state = 'Q'
        elif _state == 'Running':
            state = 'R'
        elif _state == 'Completed':
            state = 'F'
        else:
            state = 'O'
        d['job_state'] = state
        st.close()

    @staticmethod
    def pbs_stat(d):
        # Updates a dictionary of pbs job status information
        cmd = "qstat -f %s" % d['jobid']
        print('cmd=', cmd)
        st = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        errline = st.stderr.read()
        if errline.startswith('qstat: Unknown Job Id'):
            d['job_state'] = 'F'
            return

        saved_line = ''
        savelist = ['comment',  # Gives time run and host name
                    'job_state',  # 'F', 'Q' , 'R' , 'X' for finished with errors
                    'Exit_status',  # 0 = normal, 271 for resources exceeded
                    # resources used
                    'resources_used.mem',  # string '280864kb'
                    'resources_used.vmem',  # string '280864kb'
                    'resources_used.walltime',  # string HH:MM:SS
                    # resources requested
                    'queue',  # queue name
                    'Resource_List.walltime',  # string HH:MM:SS
                    'Submit_arguments',  # PBS file name. Useful for resubmitting
                    ]

        for line in st.stdout:
            if line.startswith('Job Id:'):
                continue

            if line.startswith('\t'):
                saved_line += line[1:-1]
                continue

            if saved_line:
                k, v = re.findall(r'(\S+)\s*=\s*(.*)', saved_line)[0]
                if k in savelist:
                    d[k] = v

            if line.startswith('    '):
                line = line[4:-1]

            saved_line = line

        try:
            if d and d['Exit_status'] != '0':
                d['job_state'] = 'X'
        except:
            pass

    def add_job(self, cmd, dir, cpu, outfile):
        if cpu == 0:
            cpu = self.cpus
        else:
            self.scaling = True
        num = len(self.jobs)
        if dir:
            dir = os.path.abspath(dir)
            outfile = os.path.join("..", outfile)
        self.jobs.append({'num': num,
                          'cmd': cmd,
                          'cpu': cpu,
                          'dir': dir,
                          'outfile': outfile,
                          'status': 0,
                          'job': '',
                          'secs': 0,
                          'walltime': self.walltime})

    def check(self, pbsjob):
        """
        Updates the status of PBS jobs. (This should not be confused with the
        PUQ job status in self.jobs.)
        'F' = Finished
        'Q' = Queued
        'R' = Running
        'X' = Finished with errors
        """
        if self.has_checkjob:
            self.checkjob(pbsjob)
        else:
            self.pbs_stat(pbsjob)
        # hack?  qstat is behaving badly on coates
        time.sleep(2)

    def submit(self, cmd, joblist, walltime):
        cpu = joblist[0]['cpu']
        cpn = self.cpus_per_node
        mcpu = min(cpu, cpn)
        nodes = int((cpu + cpn - 1) / cpn)
        walltime = self.secs_to_walltime(walltime)
        fname = '%s_%s' % (self.fname, self.jnum)
        f = open('%s.pbs' % fname, 'w')
        f.write('#!/bin/bash -l\n')
        f.write('#PBS -q %s\n' % self.qname)
        if self.has_torque:
            f.write('#PBS -l nodes=%s:ppn=%s\n' % (nodes, cpn))
        else:
            f.write('#PBS -l select=%s:ncpus=%s:mpiprocs=%s\n' % (nodes, cpn, mcpu))
        f.write('#PBS -l walltime=%s\n' % walltime)
        # f.write('#PBS -l place=excl:scatter\n')
        f.write('#PBS -o %s.pbsout\n' % fname)
        f.write('#PBS -e %s.pbserr\n' % fname)
        if self.env:
            f.write('source %s\n' % self.env)
        for m in self.modules:
            f.write('module load %s\n' % m)
        f.write('cd  $PBS_O_WORKDIR\n')
        f.write('%s\n' % cmd)
        f.close()
        while True:
            res = os.popen("qsub %s.pbs" % fname).readline()
            debug('job=%s' % res)
            try:
                job = int(res.split('.')[0])
                break
            except:
                print('WARNING: Bad response from qsub: %s' % res)
                print('Retrying...')
                continue
        for j in joblist:
            j['job'] = job
            j['status'] = 'Q'
            d = {'jnum': self.jnum,
                 'joblist': joblist,
                 'job_state': 'Q',
                 'queue': self.qname,
                 'Submit_arguments': '%s.pbs' % fname,
                 'jobid': job}
        self.jnum += 1
        return d

    def run(self):
        debug('RUN')

        # fix for some broken saved jobs
        for i, j in enumerate(self.jobs):
            if type(j) == str or type(j) == np.string_:
                self.jobs[i] = eval(j)

        # check to see if anything is left to do
        work_to_do = False
        for j in self.jobs:
            if j['status'] == 0 or j['status'] == 'Q':
                work_to_do = True
                break
        debug("WTD=%s" % work_to_do)
        if not work_to_do:
            return True

        # There is work to be done. Create a JobQueue and send stuff to it
        jobq = JobQueue(self, limit=self.qlimit)
        for j in self.jobs:
            if j['status'] == 0:
                debug("adding job %s" % j['num'])
                jobq.add(j)

        # Tell the JobQueue to start running jobs
        jobq.start()

        # join returns when JobQueue has run all the jobs
        res = jobq.join()
        if res == []:
            return True
        self.wqueue = res
        return False
