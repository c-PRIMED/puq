from puq import *

def run():
    x = UniformParameter('x', 'x', min=-5, max=5)
    y = UniformParameter('y', 'y', min=-5, max=5)

    host = InteractiveHost()
    uq = Smolyak([x,y], level=2)
    prog = TestProgram('./c1_prog.py')
    return Sweep(uq, host, prog)
