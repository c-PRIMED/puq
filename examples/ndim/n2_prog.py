#!/usr/bin/env python
''' Example of dumping 2d output variables.

> ./n2_prog.py --alpha=1

HDF5:{"name": "f", "value": {"py/object": "numpy.ndarray", "dtype": "float64",
      "value": [[1.0, 4.0, 9.0, 16.0], [4.0, 16.0, 36.0, 64.0],
      [9.0, 36.0, 81.0, 144.0], [16.0, 64.0, 144.0, 256.0]]},
      "desc": ""}:5FDH

'''

import optparse
import numpy as np
from puq import dump_hdf5

# this is our random  parameter
usage = "usage: %prog --alpha a"
parser = optparse.OptionParser(usage)
parser.add_option("--alpha", type=float)
(options, args) = parser.parse_args()
a = options.alpha

# create a 4x4 array
m = np.arange(1, 5)
m = np.outer(m, m)

# evaluate function over array
f = (m/a)**2

dump_hdf5('f', f)
