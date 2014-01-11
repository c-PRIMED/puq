#!/usr/bin/env python
"""
Example of doing a scaling run with MPM

Usage: mpm_scale.py [-v]
"""
from puq import *
import numpy, re

def run():
    # Declare our parameters here
    np = Parameter('np', 'Number of Processors', values=[2,4,8,16])

    # Which host to use
    host = InteractiveHost()
    #host = PBSHost(env='~/memosa/env.sh', cpus_per_node=8, walltime='45:00')

    # select a parameter sweep method
    # We'll use the Scaling sweep
    psweep = Scaling(np)

    # MPM is difficult because it takes no arguments and
    # reads and writes to fixed name files. So you must
    # tell it to create directories for each run and copy
    # the input files into each.

    prog = TestProgram('PM2', newdir=True, desc='MPM Scaling',
        infiles=['pm2geometry', 'pm2input', 'pmgrid_geom.nc', 'pmpart_geom.nc'])

    # Finally, create a Sweep object. Tell it to keep
    # track of execution time for us.
    return Sweep(psweep, host, prog)


