#!/usr/bin/env python
"""
Example of using a UQ method with a sweep.

Usage: test1.py
"""
from puq import *
from numpy import array

def run():
    # Declare our parameters here

    # gaussian
    x = Parameter('x', 'x value', min=-2, max=2)
    # uniform
    y = Parameter('y', 'y value', min=-2, max=2)

    # Which host to use
    host = InteractiveHost()
    #host = PBSHost(env='/scratch/prism/memosa/env.sh', cpus_per_node=8, walltime='2:00')

    # select a parameter sweep method
    # These control the parameters sent to the test program
    # Currently the choices include Smolyak, and PSweep
    # For Smolyak, first arg is a list of parameters and second is the level
    uq = Smolyak([x,y], 5)

    # If we create a TestProgram object, we can add a description
    # and the plots will use it.
    prog = TestProgram('fortran_test',
                       desc='Example Fortran Program.',
                       exe='./fortran_test -x %1 -y %2')

    # Create a Sweep object
    return Sweep(uq, host, prog)
