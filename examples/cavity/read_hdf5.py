#!/usr/bin/env python
"""
This is an example of reading an hdf5 file.

Usage: read_hdf5 file
"""

import sys, h5py
import numpy as np

def usage():
    print __doc__
    sys.exit(-1)

if len(sys.argv) != 2:
    usage()

f = h5py.File(sys.argv[1], 'r')

v_x_mean = f['/smolyak/v_x_eq_0_5/mean'].value
v_x_dev =  f['/smolyak/v_x_eq_0_5/dev'].value

v_y_mean = f['/smolyak/v_y_eq_0_5/mean'].value
v_y_dev =  f['/smolyak/v_y_eq_0_5/dev'].value

u_x_mean = f['/smolyak/u_x_eq_0_5/mean'].value
u_x_dev =  f['/smolyak/u_x_eq_0_5/dev'].value

u_y_mean = f['/smolyak/u_y_eq_0_5/mean'].value
u_y_dev =  f['/smolyak/u_y_eq_0_5/dev'].value

print "U"
for m, d in zip(u_x_mean, u_x_dev):
    print "0.5 0.0 %f %e" % (m,d)
for m, d in zip(u_y_mean, u_y_dev):
    print "0.0 0.5 %f %e" % (m,d)
print "\nV"
for m, d in zip(v_x_mean, v_x_dev):
    print "0.5 0.0 %f %e" % (m,d)
for m, d in zip(v_y_mean, v_y_dev):
    print "0.0 0.5 %f %e" % (m,d)

f.close()