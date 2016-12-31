from puq import *
import numpy as np

# test case with just a single point
def run():
    # Declare our parameters here. Both are uniform on [-2, 2]
    x = UniformParameter('x', 'x', min=-2, max=2)

    # Create a host
    host = InteractiveHost()

    # Use any of the following
    # valarray = np.array([1,2,3,4,5])
    valarray = [1,2,3,4,5]

    uq = SimpleSweep([x], valarray)

    prog = TestProgram('python poly_prog.py')
    return Sweep(uq, host, prog)
