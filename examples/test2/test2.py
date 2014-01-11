#!/usr/bin/env python
"""
Example of using a UQ method with a sweep.

Usage: test2.py
"""
from puq import *

def run():
    # Declare our parameters here
    mass = Parameter('m', 'mass', mean=100, dev=5)

    # Which host to use
    host = InteractiveHost()
    #host = PBSHost(env='/scratch/prism/memosa/env.sh', cpus_per_node=8, walltime='2:00')

    # select a parameter sweep method
    # These control the parameters sent to the test program
    # Currently the choices include Smolyak, and PSweep
    # For Smolyak, first arg is a list of parameters and second is the level
    uq = Smolyak([mass], 2)

    # If we create a TestProgram object, we can add a description
    # and the plots will use it.
    prog = TestProgram('./test2_prog.py', desc='Test Program Two.')

    # Create a Sweep object
    return Sweep(uq, host, prog)

def datafilter(hf):
    print "NOW IN DATA FILTER"

    # read the old data for 'x'
    x = hf['output/data/x'].value

    # delete old data
    del hf['output/data/x']

    hf['output/data/x'] = 2 * x
    # Optionally, give it a description    
    hf['output/data/x'].attrs['description'] = 'x fixed'
