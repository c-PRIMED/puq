"""
This file is part of PUQ
Copyright (c) 2013-2016 PUQ Authors
See LICENSE file for terms.
"""
from __future__ import absolute_import, division, print_function

import socket
import os, re, signal, logging
from logging import debug
from .monitor import TextMonitor
from .jobqueue import JobQueue
from subprocess import PIPE
import numpy as np
from puq.options import options
from shutil import rmtree

# Need to handle some things differently on Windows
import sys
if sys.platform.startswith("win"):
    windows = True
    from psutil import Popen, wait_procs
else:
    windows = False
    from subprocess import Popen


class Host(object):

    def __init__(self):

        # Need to find GNU time.  If /usr/bin/time is not GNU time
        # then PUQ expects it to be in the path and called 'gtime'
        tstr = 'gtime'
        try:
            ver = Popen("/usr/bin/time --version", shell=True, stderr=PIPE).stderr.read()
            if ver.startswith(b"GNU"):
                tstr = '/usr/bin/time'
        except:
            pass

        self.timestr = tstr + " -f \"HDF5:{'name':'time','value':%e,'desc':''}:5FDH\""
        self.run_num = 0

    def reinit(self):
        self.jobs = []

    def add_jobs(self, fname, args):
        self.fname = fname
        for a in args:
            output = '%s_%s' % (fname, self.run_num)
            cmd = self.prog.cmd(a)
            _dir = self.prog.setup(output)
            self.add_job(cmd, _dir, 0, output)
            self.run_num += 1

    def add_job(self, cmd, dir, cpu, outfile):
        """
        Adds jobs to the queue.

        - *cmd* : Command to execute.
        - *dir* : Directory to run the command in. '' is the default.
        - *cpu* : CPUs to allocate for the job. Don't set this. Only used by scaling method.
        - *outfile* : Output file basename.
        """

        if cpu == 0:
            cpu = self.cpus
        if dir:
            dir = os.path.abspath(dir)
        self.jobs.append({'cmd': cmd,
                          'dir': dir,
                          'cpu': cpu,
                          'outfile': outfile,
                          'status': 0})

    def run(self):
        """
        Run all the jobs in the queue. Returns True on successful completion.
        """
        raise NotImplementedError('This method should have been implemented.')

    # Collect the data from individual stdout and stderr files into
    # the HDF5 file. Remove files when finished.
    def collect(self, hf):
        # Collect results from output files
        debug("Collecting")
        hf.require_group('output')
        run_grp = hf.require_group('output/jobs')

        old_jobs = sorted(map(int, [x for x in hf['/output/jobs'].keys() if x.isdigit()]))

        # find the jobs that are completed and, if the stdout/stderr files are there,
        # move them to hdf5
        finished_jobs = self.status(quiet=True)[0]
        for j in finished_jobs:
            if j in old_jobs:
                continue

            grp = run_grp.require_group(str(j))

            for ext in ['out', 'err']:
                fname = '%s_%s.%s' % (self.fname, j, ext)
                f = open(fname, 'r')
                grp.create_dataset('std%s' % ext, data=f.read())
                f.close()
                if not options['keep']:
                    os.remove(fname)

            if self.prog.newdir:
                os.chdir('%s_%s' % (self.fname, j))

            for fn in self.prog.outfiles:
                try:
                    f = open(fn, 'r')
                    grp.create_dataset(fn, data=f.read())
                    f.close()
                except:
                    pass

            if self.prog.newdir:
                os.chdir('..')
                # now delete temporary directory
                if not options['keep']:
                    dname = '%s_%s' % (self.fname, j)
                    try:
                        rmtree(dname)
                    except:
                        pass
        return finished_jobs

    @staticmethod
    def walltime_to_secs(str):
        secs = 0
        a = str.split(':')
        la = len(a)
        if la < 1 or la > 3:
            raise ValueError
        if la == 3:
            secs += 3600 * int(a[-3])
        if la > 1:
            secs += 60 * int(a[-2])
        if la:
            secs += int(a[-1])
        return secs

    @staticmethod
    def secs_to_walltime(secs):
        secs = int(secs)
        hours = int(secs / 3600)
        secs -= (3600 * hours)
        mins = int(secs / 60)
        secs -= (60 * mins)
        return "%s:%02d:%02d" % (hours, mins, secs)

    def cmdline(self, j):
        cmd = '%s %s > %s.out 2> %s.err' % (self.timestr, j['cmd'], j['outfile'], j['outfile'])
        if j['dir']:
            cmd = 'cd %s;%s' % (j['dir'], cmd)
        return cmd

    def status(self, quiet=0):
        """
        Returns all the jobs in the job queue which have completed.
        """
        total = len(self.jobs)
        finished = []
        errors = []
        for num, j in enumerate(self.jobs):
            if j['status'] == 'F':
                finished.append(num)
            elif j['status'] == 'X':
                finished.append(num)
                errors.append(num)
            elif j['status'] == 0:
                fname = '%s_%s.err' % (self.fname, num)
                try:
                    f = open(fname, 'r')
                except IOError:
                    if hasattr(self, 'prog') and self.prog.newdir:
                        try:
                            fname = os.path.join('%s_%s' % (self.fname, j))
                            f = open(fname, 'r')
                        except:
                            continue
                    else:
                        continue
                for line in f:
                    if line.startswith('HDF5:'):
                        finished.append(num)
                        print('Marking job %s as Finished' % num)
                        j['status'] = 'F'
                        break
                f.close()

        if not quiet:
            print("Finished %s out of %s jobs." % (len(finished), total))

        if errors:
            print("%s jobs had errors." % len(errors))

        return finished, len(finished) == total


class InteractiveHost(Host):
    """
    Create a host object that runs all jobs on the local CPU.

    Args:
      cpus: Number of cpus each process uses. Default=1.
      cpus_per_node: How many cpus to use on each node.
        Default=all cpus.
    """
    def __init__(self, cpus=1, cpus_per_node=0):
        Host.__init__(self)
        from multiprocessing import cpu_count
        if cpus <= 0:
            cpus = 1
        self.cpus = cpus
        if cpus_per_node:
            self.cpus_per_node = cpus_per_node
        else:
            self.cpus_per_node = cpu_count()
        self.hostname = socket.gethostname()
        self.jobs = []

    # run, monitor and status return
    # True (1) is successful
    # False (0) for errors or unfinished
    def run(self):
        """ Run all the jobs in the queue """
        self._cpus_free = self.cpus_per_node
        self._running = []
        self._monitor = TextMonitor()
        try:
            self._run()
            return True
        except KeyboardInterrupt:
            print('***INTERRUPT***\n')
            print("If you wish to resume, use 'puq resume'\n")
            for p, j in self._running:
                os.kill(p.pid, signal.SIGKILL)
                j['status'] = 0
            return False

    def _run(self):

        # fix for some broken saved jobs
        for i, j in enumerate(self.jobs):
            if type(j) == str or type(j) == np.string_:
                self.jobs[i] = eval(j)

        errors = len([j for j in self.jobs if j['status'] == 'X'])
        if errors:
            print("Previous run had %d errors. Retrying." % errors)

        for j in self.jobs:
            if j['status'] == 0 or j['status'] == 'X':
                cmd = j['cmd']
                cpus = min(j['cpu'], self.cpus)
                if cpus > self._cpus_free:
                    self.wait(cpus)
                self._cpus_free -= cpus
                sout = open(j['outfile']+'.out', 'w')
                serr = open(j['outfile']+'.err', 'w')
                if not windows:
                    cmd = self.timestr + ' ' + cmd
                if j['dir']:
                    cmd = 'cd %s;%s' % (j['dir'], cmd)
                # We are going to wait for each process, so we must keep the Popen object
                # around, otherwise it will quietly wait for the process and exit,
                # leaving our wait function waiting for nonexistent processes.
                p = Popen(cmd, shell=True, stdout=sout, stderr=serr)
                j['status'] = 'R'
                self._running.append((p, j))
                self._monitor.start_job(j['cmd'], p.pid)
        self.wait(0)

    def handle_error(self, exitcode, j):
        print(40*'*')
        print("ERROR: %s returned %s" % (j['cmd'], exitcode))
        try:
            for line in open(j['outfile']+'.err', 'r'):
                if not re.match("HDF5:{'name':'time','value':([0-9.]+)", line):
                    print(line,)
        except:
            pass
        print("Stdout is in %s.out and stderr is in %s.err." % (j['outfile'], j['outfile']))
        print(40*'*')

    def wait(self, cpus):
        while len(self._running):
            if windows:
                waitlist = [p for p, j in self._running]
                gone, alive = wait_procs(waitlist, timeout=1)
                for g in gone:
                    for p, j in self._running:
                        if p == g:
                            self._running.remove((p, j))
                            if g.returncode:
                                self.handle_error(g.returncode, j)
                                j['status'] = 'X'
                            else:
                                j['status'] = 'F'
                            self._cpus_free += j['cpu']
                            break
            else:
                w = os.waitpid(-1, 0)
                for p, j in self._running:
                    if p.pid == w[0]:
                        self._running.remove((p, j))
                        exitcode = os.WEXITSTATUS(w[1])
                        if exitcode:
                            self.handle_error(exitcode, j)
                            j['status'] = 'X'
                        else:
                            j['status'] = 'F'
                        self._cpus_free += j['cpu']
                        break

            if cpus and self._cpus_free >= cpus:
                return
        return
