from puq import *

def run(num=20):
    # Declare our parameters here. Both are uniform on [-2, 2]
    x = NormalParameter('x', 'x', mean=0, dev=1, min=-2)
    y = NormalParameter('y', 'y', mean=0, dev=1, max=2)

    # Create a host
    host = InteractiveHost()

    # Declare a UQ method.
    uq = LHS([x,y], num=num, ds=True)

    # Our test program
    prog = TestProgram('./rosen_prog.py', desc='Rosenbrock Function (python)')

    return Sweep(uq, host, prog)
