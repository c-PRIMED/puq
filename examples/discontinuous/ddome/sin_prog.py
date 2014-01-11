#!/usr/bin/env python

"""
Function to create a dome on [0,1]
split along the diagonal. This is
more challenging for the adaptive
collocation to handle because it uses
square grids.
"""

import optparse
from puqutil import dump_hdf5
import time
import numpy as np

usage = "usage: %prog --x x --y y"
parser = optparse.OptionParser(usage)
parser.add_option("--x", type=float)
parser.add_option("--y", type=float)
(options, args) = parser.parse_args()
x = options.x
y = options.y

if x+y >= 1.0:
    z = 0.0
else:
    z = np.sin(np.pi*x) * np.sin(np.pi*y)

dump_hdf5('z', z)

