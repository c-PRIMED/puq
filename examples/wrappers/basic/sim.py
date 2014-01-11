#!/usr/bin/env python
"""
This is a simple simulation that implements a quadratic equation.

We are going to pretend it is a black box that we cannot modify.
It might have been written in any language and might implement 
very complex calculations. PUQ assumes nothing.  It just needs 
a way to pass inputs parameters to the simulation, and a way 
to get the output.  Because we are pretending we cannot modify
this program, we will have to create a wrapper script for it.

This example expects a,b,c, and x, in that order, on the
command line.  It prints the result as a single float to stdout.

> ~/memosa/src/puq/examples/wrappers> ./sim.py  1 1 1 5
> 31.0
"""

import sys
try:
    a,b,c,x = map(float, sys.argv[1:])
    print a*x**2 + b*x + c
except:
    # Something went wrong. Set errorcode on exit.
    sys.exit(1)
