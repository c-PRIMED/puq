#!/usr/bin/env python
''' This is just a test program for the UQ framework'''

import optparse
import numpy as np
from puqutil import dump_hdf5

## this is our random  parameter
usage = "usage: %prog --v velocity --m mass"
parser = optparse.OptionParser(usage)
parser.add_option("--v", type=float)
parser.add_option("--m", type=float)
(options, args) = parser.parse_args()
v = options.v
m = options.m

ke = 0.5 * m * v * v
dump_hdf5('kinetic_energy', ke, 'The Kinetic Energy of the moving object.')

