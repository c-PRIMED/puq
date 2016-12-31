from puq import *
import numpy as np

# test case with just a single point

def run():
    # Declare our parameters here. Both are uniform on [-2, 2]
    x = UniformParameter('x', 'x', min=-2, max=2)
    y = UniformParameter('y', 'y', min=-2, max=2)

    # Create a host
    host = InteractiveHost()

    # any of these should work
    # valarray = np.array([[1],[0]])
    valarray = [[-1,0,1], [0,0,0]]

    uq = SimpleSweep([x,y], valarray)

    prog = TestProgram('python rosen_prog.py')
    return Sweep(uq, host, prog)
