#!/usr/bin/env python

import optparse
from puqutil import dump_hdf5

parser = optparse.OptionParser()
parser.add_option("--a", type=float)
parser.add_option("--b", type=float)
(options, args) = parser.parse_args()
a = options.a
b = options.b

p = 2*a+b
dump_hdf5('p', p, "$p=2*a+b$")




