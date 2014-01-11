#!/usr/bin/env python
"""
This is a simple simulation that implements a quadratic equation.

We are going to pretend it is a black box that we cannot modify.
It might have been written in any language and might implement
very complex calculations. PUQ assumes nothing.  It just needs
a way to pass inputs parameters to the simulation, and a way
to get the output.  Because we are pretending we cannot modify
this program, we will have to create a wrapper script for it.

This example expects a command line with a filename.
Input parameters are in a file formatted like this:
a=num
b=num
c=num
x=num

It prints the result in a file called 'output.txt' formatted like this:
The answer is num.

~/memosa/src/puq/examples/wrappers> cat input.txt
a=1
b=2.0
c=3
x=4
~/memosa/src/puq/examples/wrappers> ./sim_file.py input.txt
~/memosa/src/puq/examples/wrappers> cat output.txt
The answer is 2.700000e+01.
"""

import sys, re
try:
    # parse the input file
    filename = sys.argv[1]
    for line in open(filename, 'r'):
        exec(line)

    # now write the result to 'output.txt'
    out = open('output.txt', 'w')
    print >> out, "The answer is %s." % format(a*x**2 + b*x + c, "e")
    out.close()

except:
    # Something went wrong. Set errorcode on exit.
    raise
    sys.exit(1)
