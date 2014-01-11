#!/usr/bin/env python
''' This is just a test program for the UQ framework'''

import optparse
from puqutil import dump_hdf5

usage = "usage: %prog --m mass"
parser = optparse.OptionParser(usage)
parser.add_option("--m", type=float)
(options, args) = parser.parse_args()
x = options.m**2
dump_hdf5('x', x, '')

