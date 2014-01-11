from puq import *

def run():
    a = UniformParameter('a', 'a', min=0, max=10)
    b = UniformParameter('b', 'b', min=0, max=10)

    host = InteractiveHost()
    uq = Smolyak([a,b], level=2)
    prog = TestProgram('./prog1.py', desc='A+B sensitivity')

    return Sweep(uq, host, prog)
