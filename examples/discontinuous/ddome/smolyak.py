from puq import *

"""
Use Smolyak on a dome
cut in half along the diagonal.
This will not work well.
"""

def run():
    x = UniformParameter('x', 'x', min=0, max=1)
    y = UniformParameter('y', 'y', min=0, max=1)

    host = InteractiveHost()
    prog = TestProgram('./sin_prog.py')
    uq = Smolyak([x,y], level=6)
    return Sweep(uq, host, prog)




