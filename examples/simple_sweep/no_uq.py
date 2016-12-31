from puq import *
import numpy as np

# example using no UQ.

def run():

    # Create a host
    host = InteractiveHost()

    # either should work
    #valarray = [[-1,0,1],[-1,0,1]]
    #v1 = DParameter('x', 'x description')
    #v2 = DParameter('y', 'y description')
    #uq = SimpleSweep([v1,v2], valarray)

    #
    v1 = DParameter('x', 'x description', np.array([-1,0,1]))
    v2 = DParameter('y', 'y description', [-1,0,1])
    uq = SimpleSweep([v1,v2])

    prog = TestProgram('rosen', exe='python rosen_prog.py --x=$x --y=$y')
    return Sweep(uq, host, prog)
