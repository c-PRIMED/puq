#!/usr/bin/env python
"""
Example of using a UQ method with matlab

Usage: switch_dynamics.py [-v]
"""
from puq import *

def run():
    # Gaussian parameters
    gap = Parameter('gap', 'Gap Size (microns)', mean=3.49, dev=0.22)
    th = Parameter('th', 'Thickness (microns)', mean=4.0, dev=0.35)
    E = Parameter('e', 'Youngs Modulus (GPa)', mean=89.27, dev=14.73)

    # Which host to use
    host = InteractiveHost()
    #host = PBSHost(env='/scratch/prism/memosa/env.sh', qname='prism', cpus_per_node=8, walltime='1:00', modules=['matlab'], )

    # select a parameter sweep method
    # These control the parameters sent to the test program
    # Currently the choices include Smolyak, and PSweep
    # For Smolyak, first arg is a list of parameters and second is the level
    uq = Smolyak([th, gap, E], 2)

    prog = TestProgram(exe="octave --no-window-system --eval 'springmassdamperl($th, $gap, $e, 1.0)'")

    # Create a Sweep object
    return Sweep(uq, host, prog)
