"""
This file is part of PUQ
Copyright (c) 2013 PUQ Authors
See LICENSE file for terms.
"""
from __future__ import absolute_import, division, print_function

from logging import debug
from .hdf import get_output_names
import h5py


class PSweep(object):
    def __init__(self, iteration_cb=None):
        self.run_num = 0
        self.iteration_cb = iteration_cb

    def reinit(self):
        # for compatibility
        if not hasattr(self, 'iteration_cb'):
            self.iteration_cb = None

    def run(self, sweep):
        """
        Gets the parameters then adds the command plus parameters to
        the host object job list. Then tells the host to run.  After
        all jobs have completed, collect the data and call analyze().
        If iteration_cb is defined, call it.

        Returns True on success.
        """
        while True:
            sweep.host.add_jobs(sweep.fname, self.get_args())
            ok = sweep._save_and_run()
            if not ok:
                return False

            hf = h5py.File(sweep.fname + '.hdf5')
            sweep.collect_data(hf)
            sweep.psweep.analyze(hf)
            hf.close()

            if self.iteration_cb is not None:
                hf = h5py.File(sweep.fname + '.hdf5')
                if self.iteration_cb(sweep, hf):
                    hf.close()
                    sweep._save_hdf5()
                    return True
                hf.close()
            else:
                return True


class APSweep(object):
    """
    Adaptive Parameter Sweep
    """

    def __init__(self):
        self.iteration_num = 0
        self.run_num = 0
        self.cache = {}
        self.outvarname = ''
        self.outvardesc = ''

    def reinit(self):
        self.iteration_num = 0
        # self.run_num = 0

    def do_cache(self, sweep, plist_full, plist):
        debug("do_cache: iter=%s" % self.iteration_num)
        try:
            z = sweep.get_result(iteration=self.iteration_num)
        except:
            z = []

        # save results in local cache
        assert len(plist) == len(z)
        for args, res in zip(plist, z):
            self.cache[args] = res

        # get full set of results
        out = []
        for args in plist_full:
            out.append(self.cache[tuple(args)])

        hf = h5py.File(sweep.fname + '.hdf5')
        if not self.outvarname:
            self.outvarname = get_output_names(hf)[0]
            self.outvardesc = hf['output/data/%s' % self.outvarname].attrs['description']
        # hdf5_set_result(hf, self.outvarname, np.array(out), self.iteration_num, self.outvardesc)
        hf.close()

    def run(self, sweep):
        """
        Gets the parameters from the parameter sweep object,
        then adds the command plus parameters to the host
        object job list. Finally tells the host to run.

        If the parameter sweep is an optimization sweep,
        jobs are run one-at-a-time, with the output of the job
        determining the next parameters.

        Returns True on success. False on errors, or if interrupted.
        """
        while True:
            result = self._run(sweep)
            sweep._save_hdf5()
            if result == 'err':
                return False
            if result == 'done':
                return True
            if hasattr(self, 'iteration_cb') and self.iteration_cb is not None:
                if self.iteration_cb(sweep, self.iteration_num):
                    self.iteration_num += 1
                    sweep._save_hdf5()
                    return True
            self.iteration_num += 1

    def _run(self, sweep):
        plist = []
        plist_full = []
        for args in self.get_args():
            args = tuple(args)
            plist_full.append(args)
            if args not in self.cache:
                plist.append(args)
                output = '%s_%s' % (sweep.fname, self.run_num)
                cmd = sweep.prog.cmd(args)
                dir = sweep.prog.setup(output)
                sweep.host.add_job(cmd, dir, 0, output)
                self.run_num += 1

        if plist_full == []:
            return 'done'
        if sweep._save_and_run():
            self._num_jobs = len(plist_full)
            self._num_jobs_cached = len(plist_full) - len(plist)
            sweep.collect_data(iterations=True)
            self.do_cache(sweep, plist_full, plist)
            return 'ok'
        return 'err'

    """
    def _run_scale(self):
        pnum = 0
        for cpus in self.psweep.get_args():
            cpus = cpus[0][1]
            output = 'sweep_%s_%s' % (self.id, pnum)
            dir = self.prog.setup(output)
            self.host.add_job(self.prog.name, dir, cpus, output)
            pnum += 1
        return self._save_and_run()
    """
