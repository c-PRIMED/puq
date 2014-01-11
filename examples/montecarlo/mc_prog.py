#!/usr/bin/env python
''' This is just a test program for the UQ framework'''

import optparse
import numpy as np

## this is our random  parameter
usage = "usage: %prog --v velocity"
parser = optparse.OptionParser(usage)
parser.add_option("--v", type=float)
(options, args) = parser.parse_args()
v = options.v

from puqutil import dump_hdf5
dump_hdf5('velocity', v, 'Velocity')
