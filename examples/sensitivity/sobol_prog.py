#!/usr/bin/env python

# Example from
# http://publications.jrc.ec.europa.eu/repository/handle/111111111/8571

import optparse
from puqutil import dump_hdf5
import numpy as np
parser = optparse.OptionParser()
parser.add_option("--x1", type=float)
parser.add_option("--x2", type=float)
parser.add_option("--x3", type=float)
parser.add_option("--x4", type=float)
parser.add_option("--x5", type=float)
parser.add_option("--x6", type=float)
(options, args) = parser.parse_args()

x1 = options.x1
x2 = options.x2
x3 = options.x3
x4 = options.x4
x5 = options.x5
x6 = options.x6

def sobol ( x, a ):
    g = (np.abs(4*x - 2 ) + a) / (1. + a)
    return g.prod()

a = np.array([78., 12., 0.5, 2., 97, 33])
g = sobol(np.array([x1,x2,x3,x4,x5,x6]), a)

dump_hdf5('sobol', g, "sobol g-function")
