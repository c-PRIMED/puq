from puq import *

def run():
    x1 = UniformParameter('x1', 'x1', min=0, max=1)
    x2 = UniformParameter('x2', 'x2', min=0, max=1)
    x3 = UniformParameter('x3', 'x3', min=0, max=1)
    x4 = UniformParameter('x4', 'x4', min=0, max=1)
    x5 = UniformParameter('x5', 'x5', min=0, max=1)
    x6 = UniformParameter('x6', 'x6', min=0, max=1)


    host = InteractiveHost()
    uq = Smolyak([x1,x2,x3,x4,x5,x6], level=1)
    prog = TestProgram('./sobol_prog.py', desc='Sobol G-function')

    return Sweep(uq, host, prog)
