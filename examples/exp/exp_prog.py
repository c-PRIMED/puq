#!/usr/bin/env python

import optparse
from puqutil import dump_hdf5
import numpy as np
usage = "usage: %prog --k k --t t"
parser = optparse.OptionParser(usage)
parser.add_option("--k", type=float)
parser.add_option("--t", type=float)
(options, args) = parser.parse_args()
t = options.t
k = options.k

z = np.exp(-k*t)
dump_hdf5('z', z)


