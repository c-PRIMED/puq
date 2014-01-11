from puq import *

def run():
    x = UniformParameter('x', 'x', min=0, max=1)
    y = UniformParameter('y', 'y', min=0, max=1)

    host = InteractiveHost()
    prog = TestProgram('./dome_prog.py')
    uq = LHS([x,y], 500)
    return Sweep(uq, host, prog)




