#!/usr/bin/env python
"""
Example of using a UQ method with a sweep.

Usage: test_uq.py [-v]
"""
from puq import *

def run():
    # Declare our parameters here
    t = Parameter('t', 'thickness', mean=1.0, dev=.15)
    freq = Parameter('freq', 'frequency', mean=1.33862e5, dev= .05*1.33862e5)

    # Which host to use
    host = InteractiveHost()
    #host = PBSHost(env='~/memosa/env.sh', qname='prism', walltime='2:00:00')

    # select a parameter sweep method
    # These control the parameters sent to the test program
    # Currently the choices include Smolyak, PSweep, and MonteCarlo
    uq = Smolyak([t, freq], level=2)

    prog = TestProgram('./tsolver.py', desc='Damping Coefficient')

    # Create a Sweep object
    return Sweep(uq, host, prog)


