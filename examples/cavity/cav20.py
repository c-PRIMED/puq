#!/usr/bin/env python
"""
Example of using a UQ method with a sweep.

Usage: cav20.py [-v]
"""
from puq import *

def run():
    # Declare our parameters here
    t = Parameter('v', 'viscosity', mean=1.0, dev=0.1)

    # Which host to use
    host = InteractiveHost()
    #host = PBSHost(env='/scratch/prism/memosa/env.sh', cpus_per_node=8, walltime='2:00')

    # select a parameter sweep method
    # These control the parameters sent to the test program
    # Currently the choices include Smolyak, and PSweep
    # For Smolyak, first arg is a list of parameters and second is the level
    uq = Smolyak([t], 2)

    # Create a Sweep object
    return Sweep(uq, host, './cavityCollocation.py')
