from puq import *
import numpy as np

def run():
    # Declare our parameters here. Both are uniform on [-2, 2]
    x = UniformParameter('x', 'x', min=-2, max=2)
    y = UniformParameter('y', 'y', min=-2, max=2)

    # Create a host
    host = InteractiveHost()

    # Declare a UQ method.
    _x,_y = np.meshgrid(np.arange(-2,2,.1),np.arange(-2,2,.1))
    valarray = np.vstack((np.ravel(_x), np.ravel(_y)))
    uq = SimpleSweep([x,y], valarray)

    prog = TestProgram('./rosen_prog.py')
    return Sweep(uq, host, prog)
