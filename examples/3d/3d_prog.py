#!/usr/bin/env python

import optparse
from puqutil import dump_hdf5

usage = "usage: %prog --x x --y y --z z"
parser = optparse.OptionParser(usage)
parser.add_option("--x", type=float)
parser.add_option("--y", type=float)
parser.add_option("--z", type=float)
(options, args) = parser.parse_args()
x = options.x
y = options.y
z = options.z

f = x + y*2 - z
g = x**4 + z**2
dump_hdf5('f', f, "f(x,y,z)=x+y^2+z^3")

# We could do multiple outputs at once for
# non-adaptive methods
dump_hdf5('g', g, "g(x,y,z)=x^4+z^2")



