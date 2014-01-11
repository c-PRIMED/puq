#!/usr/bin/env python

import optparse
from puqutil import dump_hdf5
import numpy as np

usage = "usage: %prog --x x --y y"
parser = optparse.OptionParser(usage)
parser.add_option("--x", type=float)
parser.add_option("--y", type=float)
(options, args) = parser.parse_args()
x = options.x
y = options.y

if x > 0.5:
    z = 0.0
else:
    z = np.sin(np.pi*x) * np.sin(np.pi*y)

dump_hdf5('z', z, "$f(x,y)\/=\/0\/for\/x>0.5\/else\/sin(x\pi)*sin(y\pi)$")


