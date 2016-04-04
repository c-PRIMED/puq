from puq import *

def run():
    # Declare our parameters here.
    x = UniformParameter('x', 'x', min=0, max=10)
    y = NormalParameter('y', 'y', mean=10, dev=2)

    # Create a host
    host = InteractiveHost()

    # Declare a UQ method.
    uq = Smolyak([x,y], level=1)

    # Our test program
    prog = TestProgram('python basic_prog.py', desc='Basic identity function')

    return Sweep(uq, host, prog)
