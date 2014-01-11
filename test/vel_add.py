#!/usr/bin/env python
''' This is just a test program for the UQ framework'''

import optparse
import numpy as np
from puqutil import dump_hdf5

## this is our random  parameter
usage = "usage: %prog --v velocity --m mass"
parser = optparse.OptionParser(usage)
parser.add_option("--v1", type=float)
parser.add_option("--v2", type=float)
(options, args) = parser.parse_args()
v1 = options.v1
v2 = options.v2

v = v1 + v2

dump_hdf5('v1', v1)
dump_hdf5('v2', v2)
dump_hdf5('total_velocity', v, 'The velocities added together.')

