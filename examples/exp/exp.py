from puq import *

def run(level=2):

    k = NormalParameter('k', 'decay rate', mean=0, dev=1)
    t = UniformParameter('t', 'time', min=0, max=1)

    # Create a host
    host = InteractiveHost()

    # Declare a UQ method.
    uq = Smolyak([k,t], level=level)

    # Our test program
    prog = TestProgram('./exp_prog.py', desc='Exponential Decay')

    return Sweep(uq, host, prog)

