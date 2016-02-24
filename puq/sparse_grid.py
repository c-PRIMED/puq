"""
This file is part of PUQ
Copyright (c) 2016 PUQ Authors
See LICENSE file for terms.
"""

import os
import numpy as np
import h5py


def sgrid(dim, level):
    """
    sgrid(dims, level)

    Returns a multidimensional sparse grid based on the Clenshaw Curtis rule.
    The grid will have **dims**+1 columns, with the last column containing the weights.

    This version uses a HDF5 file containing precomputed grids up to 50,000 points.
    """

    dname = os.path.dirname(__file__)
    fname = os.path.join(dname, 'spgrid_cache.hdf5')
    h = h5py.File(fname, 'r')
    try:
        val = h["%s/%s" % (dim, level)].value
    except:
        val = None
        h.close()
        raise
    h.close()
    return val

