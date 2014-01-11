from puq import *

def run():
    # Declare our parameters here
    x = Parameter('x', 'x', min=-2, max=2)
    y = Parameter('y', 'y', min=-2, max=2)

    # Create a host
    host = InteractiveHost()

    # Declare a UQ method.
    uq = Smolyak([x,y], level=4)

    prog = TestProgram('rosen_cprog', desc='Rosenbrock Function (C)',
                       exe="./rosen_cprog -x %1 -y %2")

    return Sweep(uq, host, prog)


