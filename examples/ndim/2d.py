#!/usr/bin/env python
"""
Example of 2d output

Usage: puq start ndim2
"""
from puq import *


def run():
    # Declare our parameters here

    a = UniformParameter('alpha', 'alpha', min=1, max=5)

    # Which host to use
    host = InteractiveHost()

    uq = Smolyak([a], 2)

    prog = TestProgram('./n2_prog.py')

    # Create a Sweep object
    return Sweep(uq, host, prog)
