#!/usr/bin/env python

# python wrapper script for sim.py

from subprocess import Popen, PIPE
from puqutil import dump_hdf5
from sys import argv, exit

cmd = "./sim.py %s" % ' '.join(argv[1:])
p = Popen(cmd, shell=True, stdout=PIPE)
out = p.communicate()[0]
if p.wait() == 0:
    # out is a string containing the output
    dump_hdf5('z', float(out), 'Output of the quadratic.')
else:
    exit(1)
