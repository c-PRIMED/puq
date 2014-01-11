from puq import *

def run():
    x = NormalParameter('x', 'x', mean=0, dev=5)
    y = NormalParameter('y', 'y', mean=0, dev=5)
    z = NormalParameter('z', 'z', mean=0, dev=5)

    host = InteractiveHost()
    uq = LHS([x,y,z], 500, True)
    prog = TestProgram('./3d_prog.py', desc='Example 3D Polynomial')

    return Sweep(uq, host, prog)
