"""
Utility functions for UQ

This file is part of PUQ
Copyright (c) 2013-2016 PUQ Authors
See LICENSE file for terms.
"""
from __future__ import absolute_import, division, print_function

import os
import h5py
import numpy as np
from logging import info, debug, exception, warning, critical
from puq.options import options
from puq.hdf import get_result


def dump_hdf5(name, v, desc=''):
    np.set_printoptions(threshold=np.nan)
    line = pickle({'name': name, 'desc': desc, 'value': v})
    print('HDF5:%s:5FDH' % line)


def vprint(level, str):
    if options['verbose'] >= level:
        print(str)


# read psamples from a csv file and return a dictionary
def get_psamples_from_csv(sw, h5, sname):
    samples = {}
    f = open(sname, 'r').readlines()
    header = f[0].strip().split(',')
    header = map(str.strip, header)
    data = np.empty((len(f[1:]), len(header)))
    for i, line in enumerate(f[1:]):
        data[i-1] = map(float, line.split(','))

    for i, h in enumerate(header):
        if h not in [p.name for p in sw.psweep.params]:
            print("Warning: CSV variable '%s' not a parameter for this model." % h)
        else:
            samples[h] = data[:, i]

    if samples == {}:
        print("Warning: No valid variable names found in CSV header.")
        print("Header is '%s'" % header)
        return None
    return samples


class Callback:
    """
    This class provides a convenient class to use with callback functions.
    """
    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.callback(*self.args, **self.kwargs)


def process_data(hf, grpname, callback):
    debug(grpname)
    grp = hf.require_group(grpname)
    for var in hf['output/data']:
        debug("VAR=%s" % var)
        # get the variable
        d = hf['output/data/%s' % var]
        try:
            vdesc = d.attrs['description']
        except:
            vdesc = var
        try:
            vlab = d.attrs['label']
        except:
            vlab = var

        # create HDF5 group for it
        if var in grp:
            del grp[var]
        vgrp = grp.require_group(var)
        vgrp.attrs['description'] = str(vdesc)
        vgrp.attrs['label'] = str(vlab)

        vprint(1, "\nProcessing %s" % d)
        d = get_result(hf, var)
        vlist = callback(vgrp, d)
        for v in vlist:
            try:
                vgrp[v[0]] = v[1]
            except TypeError:
                vgrp[v[0]] = repr(v[1])


def strip(fname):
    tmpname = fname + '_strip'
    os.rename(fname, tmpname)
    with h5py.File(tmpname, 'r+') as h5:
        for job in h5['output/jobs']:
            if job == 'time':
                continue
            txt = h5['output/jobs/%s/stdout' % job].value
            cont = False
            sout = []
            for line in txt.splitlines():
                if cont:
                    sout.append(line)
                    if line.endswith(':5FDH'):
                        cont = False
                elif line.startswith('HDF5:'):
                    sout.append(line)
                    if not line.endswith(':5FDH'):
                        cont = True
            del h5['output/jobs/%s/stdout' % job]
            h5['output/jobs/%s/stdout' % job] = '\n'.join(sout)
        h5.close()
    ret = os.system('h5repack %s %s' % (tmpname, fname))
    if os.WEXITSTATUS(ret) == 0:
        os.unlink(tmpname)
    else:
        print('h5repack failed.')
        os.rename(tmpname, fname)
