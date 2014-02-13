#!/usr/bin/env python
"""
Example of using a UQ method with a sweep.

Usage: test1.py
"""
from puq import *
from numpy import array

def run():
    # Declare our parameters here

    p1 = UniformParameter('x', 'x value', min=-2, max=2)
    p2 = UniformParameter('y', 'y value', min=-2, max=2)

    # Which host to use
    host = InteractiveHost()
    #host = PBSHost(env='/scratch/prism/memosa/env.sh', cpus_per_node=8, walltime='2:00')

    uq = Smolyak([p1,p2], 4)

    # If we create a TestProgram object, we can add a description
    # and the plots will use it.
    prog = TestProgram(desc='Example Fortran Program.',
                       exe='./fortran_test -x $x -y $y')

    # Create a Sweep object
    return Sweep(uq, host, prog)
