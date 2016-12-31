"""
This file is part of PUQ
Copyright (c) 2013 PUQ Authors
See LICENSE file for terms.
"""
from __future__ import absolute_import, division, print_function

import time, os, re, h5py, sys, string
import numpy as np
from puq.testprogram import TestProgram
from numpy import ndarray
from puq.hdf import get_output_names
from logging import debug
from puq.util import vprint
from puq.options import options
from puq.jpickle import pickle, unpickle
from socket import gethostname
from puq.parameter import get_psamples
import getpass
from puq.calibrate import calibrate

# for python3
if sys.version[0] == "3":
    raw_input = input
    py3 = True
else:
    py3 = False

_vcache = {}
_dcache = {}


class Sweep(object):
    """
    Creates an object that contains all the information about
    a parameter sweep.

    Args:
      psweep: Parameter Sweep object. See :class:`PSweep`.
      host: Host object.  See :class:`Host`.
      prog: TestProgram object: See :class:`TestProgram`.
      caldata(array: Experimental data for calibration. Optional.
      calerr(float): Measurement error in the experimental data.
      description(string): Optional description of this run.
    """

    def __init__(self, psweep, host, prog, caldata=None, calerr=None, description=''):
        self.host = host
        self._reinit = False

        if isinstance(prog, TestProgram):
            self.prog = prog
        else:
            self.prog = TestProgram(prog)

        if description == '':
            description = self.prog.desc
        self.description = description

        # optional calibration data
        self.caldata = caldata
        self.err = calerr

        # trying to get 10Hz resolution, 1 year clock
        secperyear = 365*24*60*60
        self.fname = 'sweep_%s' % int((time.time() % secperyear) * 10)
        self.psweep = psweep
        self.host.prog = self.prog
        self.input_script = os.path.abspath(sys.argv[0])

    def _save_hdf5(self):
        debug('')
        h5 = h5py.File(self.fname + '.hdf5')

        # write HDF5 header information, once only
        if 'version' not in h5.attrs:
            h5.attrs['MEMOSA_UQ'] = b'MEMOSA'
            h5.attrs['version'] = 201
            # h5.attrs['id'] = self.id
            h5.attrs['date'] = time.strftime("%b %d %H:%M %Z %Y", time.localtime())
            h5.attrs['hostname'] = gethostname()
            h5.attrs['username'] = getpass.getuser()
            h5.attrs['UQtype'] = self.psweep.__class__.__name__.lower()
            h5.attrs['description'] = self.description

        # overwrite previous
        if 'input' in h5:
            del h5['input']
        if 'private' in h5:
            del h5['private']

        hp = h5.require_group('private')
        hp['sweep'] = pickle(self)

        # in /input write the input params in json and regular arrays
        h = h5.require_group('input')

        # basic parameter table for non-python reading of the hdf5 file
        h['param_array'] = np.column_stack([p.values for p in self.psweep.params])
        if py3:
            h['param_array'].attrs['name'] = [bytes(p.name, 'UTF-8') for p in self.psweep.params]
            h['param_array'].attrs['description'] = [bytes(p.description, 'UTF-8') for p in self.psweep.params]

        else:
            h['param_array'].attrs['name'] = [str(p.name) for p in self.psweep.params]
            h['param_array'].attrs['description'] = [str(p.description) for p in self.psweep.params]

        # json-pickled parameters
        h = h.require_group('params')
        for p in self.psweep.params:
            h[p.name] = pickle(p)
            h[p.name].attrs['description'] = p.description
            h[p.name].attrs['label'] = p.label

        if hasattr(self.psweep, 'kde'):
            h5['input/kde'] = pickle(self.psweep.kde)

        # input script
        if hasattr(self, 'input_script'):
            h5['input/scriptname'] = str(self.input_script)
            try:
                h5['input/script'] = open(self.input_script).read()
            except:
                h5['input/script'] = "Source was unavailable."
            h5.close()

    def _save_and_run(self):
        self._save_hdf5()
        res = self.host.run()
        if res:
            self._save_hdf5()
        return res

    def run(self, fn=None, overwrite=False):
        """
        Calls PSweep.run() to run all the jobs in the Sweep.  Collect the data
        from the outputs and call the PSweep analyze method.  If the PSweep method
        has an iterative callback defined, call it, otherwise return.

        Args:
          fn(string): HDF5 filename for output. '.hdf5' will be
            appended to the filename if necessary. If fn is None,
            a filename will be generated starting with "sweep\_"
            followed by a timestamp.
          overwrite(boolean): If True and fn is not None, will
            silently overwrite any previous files of the same name.
        Returns:
          True on success.
        """

        if fn is not None:
            self.fname = os.path.splitext(fn)[0]
            fn = self.fname + '.hdf5'
            if os.path.exists(fn):
                if not overwrite:
                    done = False
                    while 1:
                        ans = raw_input('%s already exists.  Replace (Y/N):' % fn)
                        try:
                            if ans.upper() == 'N':
                                done = True
                                break
                            elif ans.upper() == 'Y':
                                break
                        except:
                            pass
                        print("Please answer with 'Y' or 'N'\n")
                    if done:
                        sys.exit(-1)
                os.remove(fn)
        vprint(1, 'Saving run to %s.hdf5' % self.fname)
        return self.psweep.run(self)

    def extend(self, num=None):
        return self.psweep.extend(num)

    def collect_data(self, hf=None):
        """ Collects data from captured stdout files and puts it in arrays
        in 'output/data'. Returns True on success.
        """

        need_to_close = False
        if hf is None:
            hf = h5py.File(self.fname + '.hdf5')
            need_to_close = True

        finished_jobs = self.host.collect(hf)
        self._extract_hdf5(hf, finished_jobs)

        has_data = 'data' in hf['output']
        if has_data:
            outd = hf['output/data']
            data = dict([(x, outd[x].value) for x in outd])
            params = dict([(p.name, p.values) for p in self.psweep.params])

        if need_to_close:
            hf.close()

        if not has_data and not self._reinit:
            print("WARNING: There is no data in the output section!")
            print("Check that your runs completed successfully.")
            return False
        return params, data

    def analyze_errors(self, hf):
        p = re.compile('Command exited with non-zero status \d+')
        for job in hf['output/jobs']:
            if job == 'time':
                continue
            err = hf['output/jobs/%s/stderr' % job].value
            res = p.findall(err)
            if res:
                print("Job %s: %s" % (job, res[0]))
                for line in err.split('\n'):
                    if line != res[0] and not line.startswith('HDF5:{'):
                        print(line)
            elif len(err) == 0:
                print("Job %s never completed. Walltime exceeded?" % job)

            results = False
            out = hf['output/jobs/%s/stdout' % job].value
            for line in out.split('\n'):
                if line.startswith('HDF5:{'):
                    results = True
                    break
            if not results:
                print("ERROR: Job %s has no output data in stdout." % job)

    def analyze(self, verbose=False):
        """
        Collects the output from all the jobs into an HDF5 file.
        Parses any tagged data in the output and puts it in
        the /data group in the HDF5 file.
        """
        debug('')
        hf = h5py.File(self.fname + '.hdf5')
        if not self.host.status(quiet=1)[1]:
            print("Cannot collect data or perform analysis until all jobs are completed.")
            print("You should do 'puq resume' to resume jobs.")
            sys.exit(-1)

        # collect the data if it has not already been collected.
        has_data = 'output' in hf and 'data' in hf['output']
        if not has_data:
            self.collect_data(hf)
            try:
                self.psweep.analyze(hf)
            except:
                print('Warning: analysis failed.')
                errors = 1

        # quick error check
        if 'data' in hf['output']:
            errors = 0
            try:
                options[self.psweep.__class__.__name__]['verbose'] = verbose
            except KeyError:
                options[self.psweep.__class__.__name__] = {'verbose': verbose}

            for var in hf['output/data']:
                if not isinstance(hf['output/data/%s' % var], h5py.Group):
                    tlen = len(hf['output/data/%s' % var].value)
                    num_jobs = len(hf['output/jobs'])
                    if 'time' in hf['output/jobs']:
                        num_jobs -= 1
                    if tlen != num_jobs:
                        errors += 1
                        print("Expected %s data points for variable %s, but got %s." % (num_jobs, var, tlen))
                        self.analyze_errors(hf)
                        return errors

        if 'psamples' not in hf:
            s = get_psamples(self.psweep.params)
            if s is not None:
                hf['psamples'] = s

        # FIXME check for correlation if multiple outputs

        # calibrate
        if hasattr(self, 'caldata') and self.caldata is not None:
            self._calibrate(hf)

        hf.close()
        self._save_hdf5()
        return errors

    # Bayesian Calibration
    def _calibrate(self, hf):
        ovar = get_output_names(hf)[0]
        method = hf.attrs['UQtype']
        rs = unpickle(hf["/%s/%s/response" % (method, ovar)].value)

        # print "Calling calibrate from sweep"
        self.psweep.params, self.psweep.kde = calibrate(self.psweep.params, self.caldata, self.err, rs.eval)

    def _dump_hdf5_cache(self, hf, d):
        global _vcache, _dcache
        if len(_vcache):
            if d:
                dgrp = hf.require_group('output/data')
            else:
                dgrp = hf.require_group('output/jobs')
            for n in _vcache:
                if n in dgrp:
                    del dgrp[n]
                adata = _vcache[n]
                if d and len(adata.shape) > 1:
                    # Data is a multidimensional array and we want to do analysis
                    # on each array element individually.  So we write them
                    # individually to /output/data
                    numvals = np.prod(adata.shape[1:])
                    for i, index in enumerate(np.ndindex(adata.shape[1:])):
                        name = '%s%s' % (n, [ind for ind in index])
                        data = adata.flatten()[i::numvals]
                        ds = dgrp.create_dataset(name, data=data)
                        ds.attrs["description"] = _dcache[n]
                else:
                    ds = dgrp.create_dataset(n, data=adata)
                    ds.attrs["description"] = str(_dcache[n])
            _vcache = {}
            _dcache = {}

    def _dump_hdf5(self, grp, line, job, mjob):
        debug("Dump %s : %s" % (job, line))
        global _vcache, _dcache

        # old format used single quotes.
        if line.startswith("{'"):
            line = line.replace("'", '"')

        x = unpickle(line)
        v = x['value']
        n = x['name']

        if n not in _vcache:
            if isinstance(v, ndarray):
                _vcache[n] = np.empty([mjob] + list(v.shape))
            else:
                _vcache[n] = np.empty((mjob))
            _vcache[n].fill(np.nan)
            _dcache[n] = x['desc']

        _vcache[n][job] = v

    # Extract tagged data to hdf5
    def _extract_hdf5(self, hf, jobs):
        debug("Extract")
        mjob = np.max(jobs) + 1
        run_grp = hf.require_group('output/jobs')
        for ext in ['out', 'err']:
            for j in jobs:
                grp = run_grp.require_group(str(j))
                if not 'std%s' % ext in grp:
                    continue
                f = grp['std%s' % ext].value
                cont = False
                for line in f.splitlines():
                    if cont:
                        line = line.strip()
                        cline += line
                        if line.endswith(':5FDH'):
                            cont = False
                            cline = cline[:-5]
                            self._dump_hdf5(grp, cline, j, mjob)
                    elif line.startswith('HDF5:'):
                        line = line[5:].strip()
                        if line.endswith(':5FDH'):
                            line = line[:-5]
                            self._dump_hdf5(grp, line, j, mjob)
                        else:
                            cont = True
                            cline = line
                    elif ext == 'err':
                        print('STDERR[job %d]: %s' % (j, line))
            self._dump_hdf5_cache(hf, ext == 'out')

    def resume(self):
        if hasattr(self.host, 'jobs'):
            self.host.run()
            self._save_hdf5()
            self.analyze()
        else:
            print("All jobs finished.")
