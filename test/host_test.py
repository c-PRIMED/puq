from __future__ import absolute_import, division, print_function
from puq.hosts import Host
from puq.jobqueue import JobQueue
from logging import debug


class TestHost(Host):
    def __init__(self, cpus=0, cpus_per_node=0, walltime='1:00:00', pack=1):
        Host.__init__(self)
        if cpus <= 0:
            print("You must specify cpus when creating a PBSHost object.")
            raise ValueError()
        if cpus_per_node <= 0:
            print("You must specify cpus_per_node when creating a PBSHost object.")
            raise ValueError()
        self.cpus = cpus
        self.cpus_per_node = cpus_per_node
        self.walltime = walltime
        self.jobs = []
        self.wqueue = []
        self.wlist = []
        self.pack = pack
        self.scaling = False
        self.jnum = 0

    @staticmethod
    def job_status(j):
        j['status'] = 'F'

    def add_job(self, cmd, dir, cpu, outfile):
        if cpu == 0:
            cpu = self.cpus
        else:
            self.scaling = True
        num = len(self.jobs)
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
        Returns the status of PBS jobs.
        'F' = Finished
        'Q' = Queued
        'R' = Running
        'U' = Unknown
        """
        pbsjob['job_state'] = 'F'

    def submit(self, cmd, joblist, walltime):
        global output
        cpu = joblist[0]['cpu']
        cpn = self.cpus_per_node
        nodes = int((cpu + cpn - 1) / cpn)
        walltime = self.secs_to_walltime(walltime)
        output.append({'job': self.jnum,
                       'cpu': cpu,
                       'cpu': cpn,
                       'nodes': nodes,
                       'walltime': walltime,
                       'cmd': cmd})

        job = joblist[0]['num']+100
        for j in joblist:
            j['job'] = job
            j['status'] = 'Q'
        d = {'jnum': self.jnum, 'joblist': joblist, 'jobid': job}
        self.jnum += 1
        return d

    def run(self):
        jobq = JobQueue(self, limit=10, polltime=1)
        for j in self.jobs:
            if j['status'] == 0 or j['status'] == 'Q':
                debug("adding job %s" % j['num'])
                jobq.add(j)
        jobq.start()
        return jobq.join() == []


def test_Host0():
    global output
    output = []
    th = TestHost(cpus=1, cpus_per_node=1, walltime='10:00', pack=1)
    th.add_job('foobar', '', 0, 'xxx')
    th.run()
    assert len(output) == 1
    assert output[0]['walltime'] == '0:10:00'

def test_Host1():
    global output
    output = []
    th = TestHost(cpus=1, cpus_per_node=1, walltime='10:00', pack=1)
    th.add_job('foobar -1', '', 0, 'xxx')
    th.add_job('foobar -2', '', 0, 'xxx')
    th.add_job('foobar -3', '', 0, 'xxx')
    th.add_job('foobar -4', '', 0, 'xxx')
    th.run()
    assert len(output) == 4
    assert output[0]['walltime'] == '0:10:00'

def test_Host2():
    global output
    output = []
    th = TestHost(cpus=1, cpus_per_node=1, walltime='10:00', pack=4)
    th.add_job('foobar -1', '', 0, 'xxx')
    th.add_job('foobar -2', '', 0, 'xxx')
    th.add_job('foobar -3', '', 0, 'xxx')
    th.add_job('foobar -4', '', 0, 'xxx')
    th.run()
    assert len(output) == 1
    assert output[0]['walltime'] == '0:40:00'

def test_Host3():
    global output
    output = []
    th = TestHost(cpus=2, cpus_per_node=4, walltime='10:00', pack=1)
    for i in range(11):
        th.add_job('foobar', '', 0, 'xxx')
    th.run()
    assert len(output) == 6
    assert output[0]['walltime'] == '0:10:00'

def test_Host4():
    global output
    output = []
    th = TestHost(cpus=2, cpus_per_node=4, walltime='10:00', pack=3)
    for i in range(11):
        th.add_job('foobar', '', 0, 'xxx')
    th.run()
    assert len(output) == 2
    assert output[0]['walltime'] == '0:30:00'

def test_Host5():
    global output
    output = []
    th = TestHost(cpus=22, cpus_per_node=4, walltime='10:00', pack=1)
    th.add_job('foobar', '', 0, 'xxx')
    th.add_job('foobar', '', 0, 'xxx')
    th.run()
    assert len(output) == 2
    assert output[0]['walltime'] == '0:10:00'
    assert output[1]['walltime'] == '0:10:00'
    assert output[0]['nodes'] == 6
    assert output[1]['nodes'] == 6
    assert output[0]['cpu'] == 4
    assert output[1]['cpu'] == 4

def test_HostMultiRun():
    global output
    output = []
    th = TestHost(cpus=1, cpus_per_node=1, walltime='10:00', pack=1)
    th.add_job('foobar -1', '', 0, 'xxx')
    th.add_job('foobar -2', '', 0, 'xxx')
    th.add_job('foobar -3', '', 0, 'xxx')
    th.add_job('foobar -4', '', 0, 'xxx')
    th.run()
    print('-' * 80)
    th.add_job('foobar -5', '', 0, 'xxx')
    th.add_job('foobar -6', '', 0, 'xxx')
    th.add_job('foobar -7', '', 0, 'xxx')
    th.add_job('foobar -8', '', 0, 'xxx')
    th.run()
    print(output)
