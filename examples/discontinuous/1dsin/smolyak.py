from puq import *

def run():
    x = UniformParameter('x', 'x', min=0, max=2)
    host = InteractiveHost()
    uq = Smolyak([x], level=8)
    prog = TestProgram('./sin.py', desc='Sine Function')
    return Sweep(uq, host, prog)
