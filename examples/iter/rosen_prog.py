#!/usr/bin/env python

import optparse
from puqutil import dump_hdf5

usage = "usage: %prog --x x --y y"
parser = optparse.OptionParser(usage)
parser.add_option("--x", type=float)
parser.add_option("--y", type=float)
(options, args) = parser.parse_args()
x = options.x
y = options.y

z = 100*(y-x**2)**2 + (1-x)**2

dump_hdf5('z', z)


