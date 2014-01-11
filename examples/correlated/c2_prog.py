#!/usr/bin/env python

import optparse
from puqutil import dump_hdf5
import time

usage = "usage: %prog --f f --g g"
parser = optparse.OptionParser(usage)
parser.add_option("--g", type=float)
parser.add_option("--f", type=float)

(options, args) = parser.parse_args()
f = options.f
g = options.g

k = f * g
dump_hdf5('k', k, "$k(f,g)=f*g$")
