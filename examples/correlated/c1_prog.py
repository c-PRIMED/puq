#!/usr/bin/env python

import optparse
from puqutil import dump_hdf5
import time

usage = "usage: %prog --x x --y y"
parser = optparse.OptionParser(usage)
parser.add_option("--x", type=float)
parser.add_option("--y", type=float)

(options, args) = parser.parse_args()
x = options.x
y = options.y

# need to produce two correlated output variables, f and g

f = x
g = x + y
z = f * g

dump_hdf5('f', f, "$f(x,y)=x+y$")
dump_hdf5('g', g, "$g(x,y)=x+y$")
dump_hdf5('z', z, "$z(x,y)=x(x+y)$")
