from puq import *

def run():
    x = UniformParameter('x', 'x', min=0, max=2)
    host = InteractiveHost()
    uq = LHS([x], 500, True)
    prog = TestProgram('./sin.py', desc='Sine Function')
    return Sweep(uq, host, prog)
