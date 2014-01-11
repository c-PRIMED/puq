#!/usr/bin/env python

"""
python wrapper script for sim_file.py

~/memosa/src/puq/examples/wrappers> ./sim_file_wrap.py 1 2 3 4
HDF5:{'name': 'z', 'value': 'Output of the quadratic.', 'desc': 27.0}:5FDH
"""

from puqutil import dump_hdf5
from sys import argv, exit
import os, re

# create the input file
f = open('input.txt', 'w')
print >> f, "a=%s" % argv[1]
print >> f, "b=%s" % argv[2]
print >> f, "c=%s" % argv[3]
print >> f, "x=%s" % argv[4]
f.close()

# Note about paths.  If your simulation is installed on your
# PATH, then everything works fine.  I used ".." for a relative path
# to the simulation.  I have to use ".." because this will be executed
# in a subdirectory because quad_file uses the newdir option.
cmd = "../sim_file.py input.txt"
if os.system(cmd) == 0:
    out = open('output.txt', 'r').read()
    z = re.findall(r'The answer is ([-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)', out)[0][0]
    dump_hdf5('z', float(z), 'Output of the quadratic.')
else:
    exit(1)
