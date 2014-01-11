from puq import *

"""
Use adaptive colllocation on a dome
cut in half along the diagonal.
"""

def run():
    x = UniformParameter('x', 'x', min=0, max=1)
    y = UniformParameter('y', 'y', min=0, max=1)

    host = InteractiveHost()
    prog = TestProgram('./sin_prog.py')
    uq = AdapStocColl([x,y], tol=.01)
    return Sweep(uq, host, prog)




