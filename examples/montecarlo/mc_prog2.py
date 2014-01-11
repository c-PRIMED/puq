#!/usr/bin/env python
''' This is just a test program for the UQ framework'''

import optparse
import numpy as np

## this is our random  parameter
usage = "usage: %prog --v velocity --m mass"
parser = optparse.OptionParser(usage)
parser.add_option("--v", type=float)
parser.add_option("--m", type=float)
(options, args) = parser.parse_args()
v = options.v
m = options.m
both = v + m
from puqutil import dump_hdf5
#dump_hdf5('velocity', v, 'Velocity')
#dump_hdf5('mass', m, 'Mass')
dump_hdf5('both', both, 'M + V')
