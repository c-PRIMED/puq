from puq import *

def run(lev=2):
    # Declare our parameters here
    p1 = Parameter('x', 'x', min=-2, max=2)
    p2 = Parameter('y', 'y', min=-2, max=2)

    # Create a host
    host = InteractiveHost()

    # Declare a UQ method.
    uq = Smolyak([p1, p2], level=lev)

    prog = TestProgram(desc='Rosenbrock Function (C)',
        exe="./rosen_cprog -x $x -y $y")

    return Sweep(uq, host, prog)


