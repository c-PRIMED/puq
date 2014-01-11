from puq import *

def run():
    f = Parameter('f', 'f', pdf=LoadObj('f.json'), use_samples=True)
    g = Parameter('g', 'g', pdf=LoadObj('g.json'), use_samples=True)

    host = InteractiveHost()
    uq = Smolyak([f,g], level=2)
    prog = TestProgram('./c2_prog.py')
    return Sweep(uq, host, prog)
