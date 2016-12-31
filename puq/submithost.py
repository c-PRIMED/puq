"""
This file is part of PUQ
Copyright (c) 2013 PUQ Authors
See LICENSE file for terms.
"""
from __future__ import absolute_import, division, print_function

import os, time, sys
from .monitor import TextMonitor
from subprocess import Popen, PIPE
import numpy as np
from logging import debug
from .hosts import Host
from shutil import rmtree
from stat import S_ISDIR
from glob import glob
from threading import Thread, Event


class SubmitHost(Host):
    """
    Create a host object that uses the hub submit command.

    Args:
      cpus: Number of cpus each process uses. Default=1.
      cpus_per_node: How many cpus to use on each node.  Default=1.
    """
    def __init__(self, venue=None, cpus=1, cpus_per_node=1, walltime=60):
        Host.__init__(self)
        self.cpus = cpus
        self.cpus_per_node = cpus_per_node
        self.hostname = venue
        self.jobs = []

    # Creates a CSV file compatible with the HubZero submit command
    def add_jobs(self, fname, args):
        import shlex
        self.fname = fname
        first = True
        try:
            os.mkdir(fname)
        except:
            pass
        f = open(os.path.join(fname, 'input.csv'), 'w')
        for a in args:
            if first:
                first = False
                print(', '.join(['@@'+b[0] for b in a]), file=f)
                cmds = [(x[0], '@@'+x[0]) for x in a]
            print(','.join([str(b[1]) for b in a]), file=f)
        f.close()
        scmd = "submit --runName=puq -d input.csv %s" % self.prog.cmd(cmds)
        self.add_job(shlex.split(scmd), '', 0, '')

    # run, monitor and status return
    # True (1) is successful
    # False (0) for errors or unfinished
    def run(self):
        """ Run all the jobs in the queue """
        self._running = []
        self._monitor = TextMonitor()
        cwd = os.path.abspath(os.getcwd())
        os.chdir(self.fname)
        err = self._run()
        os.chdir(cwd)
        if err == False:
            rmtree(self.fname, ignore_errors=True)
            try:
                os.remove(self.fname+'.hdf5')
            except:
                pass
            return False
        return True

    def peg_parse(self):
        # parse the contents of the pegasusstatus.txt file
        done = 0
        filename = 'pegasusstatus.txt'
        with open(filename) as f:
            for line in f:
                if line.startswith('%DONE'):
                    done = float(line.split()[1])
                    break
        return done

    def status_monitor(self):
        # Watch pegasusstatus.txt for status changes.
        # This could possibly be done more efficiently
        # using filesystem notification but in practice
        # this turned out to be more reliable across
        # different OS versions.
        found = False
        while not found and not self.stop.is_set():
            try:
                os.chdir('puq/work')
                found = True
            except:
                self.stop.wait(10)

        done = -1
        while not self.stop.is_set():
            try:
                d = self.peg_parse()
            except:
                d = done
            if d > done:
                print('=RAPPTURE-PROGRESS=>%d Running' % (int(d)))
                sys.stdout.flush()
                done = d
            if int(d) >= 100:
                self.stop.set()
            else:
                self.stop.wait(10)

    def _run(self):
        j = self.jobs[0]
        print('=RAPPTURE-PROGRESS=>0 Starting')
        sys.stdout.flush()

        try:
            myprocess = Popen(j['cmd'], bufsize=0)
        except Exception as e:
            print('Command %s failed: %s' % (' '.join(j['cmd']), e))
            sys.stdout.flush()

        self.stop = Event()
        p2 = Thread(target=self.status_monitor)
        p2.daemon = True
        p2.start()

        # wait for command to finish
        err = True
        try:
            ret = myprocess.wait()
            if ret:
                err = False
                print('Submit failed with error %s' % ret)
                whocares = os.listdir(os.getcwd())
                if os.path.exists('puq'):
                    fn = glob('puq/*.stderr')
                    if fn:
                        with open(fn[0]) as f:
                            print(f.read())
                sys.stdout.flush()
        except KeyboardInterrupt:
            print('\nPUQ interrupted. Cleaning up. Please wait...\n')
            err = False
            myprocess.kill()

        j['status'] = 'F'

        self.stop.set()
        if p2 and p2.is_alive():
            p2.join()

        return err

    # Collect the data from individual stdout and stderr files into
    # the HDF5 file. Remove files when finished.
    def collect(self, hf):
        # Collect results from output files
        debug("Collecting")

        cwd = os.path.abspath(os.getcwd())
        os.chdir(self.fname)

        hf.require_group('output')
        jobs_grp = hf.require_group('output/jobs')

        # find the jobs that are completed and, if the stdout/stderr files are there,
        # move them to hdf5
        finished_jobs = []
        os.chdir('puq')

        # Get the job stats. Do this in a loop because it looks like
        # sometimes this code gets run before pegasus generates the file.
        tries = 2
        while tries > 0:
            try:
                data = np.genfromtxt('pegasusjobstats.csv', usecols=(2,3,4,7,15,16), dtype='string',
                    skip_header=26, comments='#', delimiter=',')
                tries = 0
            except:
                tries -= 1
                if tries > 0:
                    time.sleep(30)

        job = {}
        for j, _try, site, _time, exitcode, host in data:
            if site == 'local':
                continue
            j = j[j.rfind('_')+1:]
            job[j] = (int(_try), site, float(_time), int(exitcode), host)

        times = np.empty((len(job)))
        for j in job:
            jobnum = int(j)-1
            times[jobnum] =  job[j][2]
            finished_jobs.append(jobnum)
            if not S_ISDIR(os.stat(j).st_mode):
                print("ERROR: job %s directory not found" % j)
                continue
            os.chdir(j)
            grp = jobs_grp.require_group(str(jobnum))
            for ext in ['out', 'err']:
                outfile = glob('*.std%s' % ext)
                if outfile:
                    f = open(outfile[0], 'r')
                    fdata = f.read()
                    grp.create_dataset('std%s' % ext, data=fdata)
                    if job[j][3] != 0:
                        # error code was set
                        print("ERROR: Job %s failed: %s" % (j, fdata))
                    f.close()
            for fn in self.prog.outfiles:
                try:
                    f = open(fn, 'r')
                    grp.create_dataset(fn, data=f.read())
                    f.close()
                except:
                    pass
            os.chdir('..')
        if 'time' in jobs_grp:
            del jobs_grp['time']
        jobs_grp['time'] = times

        os.chdir(cwd)
        rmtree(self.fname)

        return finished_jobs

