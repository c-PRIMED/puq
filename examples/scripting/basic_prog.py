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

f = x
g = y
h = x*x+y

dump_hdf5('f', f)
dump_hdf5('g', g)
dump_hdf5('h', h)


