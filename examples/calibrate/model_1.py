#!/usr/bin/env python

import optparse
from puqutil import dump_hdf5
import numpy as np

usage = "usage: %prog --x x --y y --z z"
parser = optparse.OptionParser(usage)
parser.add_option("--x", type=float)
parser.add_option("--y", type=float)
parser.add_option("--z", type=float)
(options, args) = parser.parse_args()
x = options.x
y = options.y
z = options.z

f = x**2 + 0.75 * y**2 + 2*y + x*y - 7*z + 2

dump_hdf5('f', f)


