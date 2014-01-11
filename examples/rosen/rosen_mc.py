from puq import *

def run(num=20):
    # Declare our parameters here. Both are uniform on [-2, 2]
    x = UniformParameter('x', 'x', min=-2, max=2)
    y = UniformParameter('y', 'y', min=-2, max=2)

    # Create a host
    host = InteractiveHost()

    # Declare a UQ method.
    uq = MonteCarlo([x,y], num=num)

    # Our test program
    prog = TestProgram('./rosen_prog.py', desc='Rosenbrock Function (python)')

    return Sweep(uq, host, prog)
