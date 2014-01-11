#!/usr/bin/env python
"""
Example of using a UQ method with a sweep.

Usage: test1.py
"""
from puq import *

def run():
    # Declare our parameters here
    v0 = Parameter('v', 'velocity', mean=11.0, dev=1.0)
    mass = Parameter('m', 'mass', mean=105, dev=5)

    # Which host to use
    host = InteractiveHost()
    #host = PBSHost(env='/scratch/prism/memosa/env.sh', cpus_per_node=8, walltime='2:00')

    # select a parameter sweep method
    # These control the parameters sent to the test program
    # Currently the choices include Smolyak, and PSweep
    # For Smolyak, first arg is a list of parameters and second is the level
    uq = Smolyak([v0, mass], 3)

    # If we create a TestProgram object, we can add a description
    # and the plots will use it.
    prog = TestProgram('./test1_prog.py', desc='Test Program One.')

    # Create a Sweep object
    return Sweep(uq, host, prog)
