from puq import *

def run():
    x = UniformParameter('x', 'x', min=0, max=10)
    host = InteractiveHost()
    uq = LHS([x], 100, True)
    prog = TestProgram('python poly_prog.py', desc='1D Polynomial')
    return Sweep(uq, host, prog)
