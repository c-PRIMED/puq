#!/usr/bin/env python

# discontinuous sine function

import optparse
from puqutil import dump_hdf5
from numpy import sin, pi

usage = "usage: %prog --x x"
parser = optparse.OptionParser(usage)
parser.add_option("--x", type=float)
(options, args) = parser.parse_args()
x = options.x
f = sin(x % (pi/2))
dump_hdf5('f', f, "$f(x)= sin(x\ mod\ \\frac{\pi}{2})$")


