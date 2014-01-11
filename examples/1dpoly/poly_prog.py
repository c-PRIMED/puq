#!/usr/bin/env python

# 1d 2nd degree polymial function

import optparse
from puqutil import dump_hdf5
import math

usage = "usage: %prog --x x"
parser = optparse.OptionParser(usage)
parser.add_option("--x", type=float)
(options, args) = parser.parse_args()
x = options.x
f = 2*x*x - 7*x + 12
dump_hdf5('f', f, 'foobar')


