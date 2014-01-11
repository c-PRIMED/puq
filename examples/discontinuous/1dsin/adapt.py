from puq import *

def run():
    x = UniformParameter('x', 'x', min=0, max=2)
    host = InteractiveHost()
    uq = AdapStocColl([x], tol=.01)
    prog = TestProgram('./sin.py', desc='Sine Function')
    return Sweep(uq, host, prog)
