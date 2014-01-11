#!/usr/bin/env python
''' Example of dumping multiple output variables.'''

import optparse
from numpy import sin
from puqutil import dump_hdf5

## this is our random  parameter
usage = "usage: %prog --v velocity --m mass"
parser = optparse.OptionParser(usage)
parser.add_option("--v", type=float)
parser.add_option("--m", type=float)
(options, args) = parser.parse_args()
v = options.v
m = options.m

ke = m * v * v * 0.5
e =  m + v + 2*m*v

#f = sin(v) + sin(m)
#g = sin(v) * sin(m)

dump_hdf5('kinetic_energy', ke, 'The Kinetic Energy of the moving object.')
dump_hdf5('energy', e, 'A random energy equation.')
#dump_hdf5('f', f, 'sin + sin')
#dump_hdf5('g', g, 'sin * sin')
