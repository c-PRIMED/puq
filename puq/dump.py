"""
This file is part of PUQ
Copyright (c) 2013-2016 PUQ Authors
See LICENSE file for terms.
"""
from __future__ import absolute_import, division, print_function

import numpy as np
import csv
import os.path


def dump(h5, fname):
    """
    Dumps all parameters and output value[s] to a single csv file.
    There is a two line header on the file.
    Example:

    v,m,energy,kinetic_energy
    ----------------------------------------
    5.0,5.0,60.0,62.5
    2.1218382609,5.0,28.3402208699,11.2554940135
    7.8781617391,5.0,91.6597791301,155.163580969
    5.0,2.1218382609,28.3402208699,26.5229782613
    ...
    """
    pnames = h5['/input/param_array'].attrs['name']
    data = h5['/input/param_array'].value
    outvars = h5['/output/data'].keys()
    for var in outvars:
        d = h5['/output/data/%s' % var].value
        if len(d.shape) != 1:
            print("ERROR: Cannot dump multidimensional data to CSV file.")
            print("Output data '%s' has dimensions %s" % (var, d.shape))
            return
        data = np.column_stack((data, d))
    fname = os.path.splitext(fname)[0] + '.csv'
    print('Dumping CSV data to %s' % fname)
    w = csv.writer(open(fname, 'wb'))
    w.writerow([p for p in pnames] + outvars)
    w.writerow([40*'-'])
    w.writerows(data)
