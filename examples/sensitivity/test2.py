from puq import *

def run():
    a = UniformParameter('a', 'a', min=-5, max=5)
    b = UniformParameter('b', 'b', min=0, max=1)

    host = InteractiveHost()
    uq = Smolyak([a,b], level=4)
    prog = TestProgram('./prog2.py', desc='Simple Polynomial')

    return Sweep(uq, host, prog)
