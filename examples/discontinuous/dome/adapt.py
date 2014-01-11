from puq import *

# Example using Adaptive Collocation on a half-dome

def run():
    x = UniformParameter('x', 'x', min=0, max=1)
    y = UniformParameter('y', 'y', min=0, max=1)

    host = InteractiveHost()
    prog = TestProgram('./dome_prog.py')
    uq = AdapStocColl([x,y], tol=.01)
    return Sweep(uq, host, prog)




