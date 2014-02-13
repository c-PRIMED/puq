from puq import *

def run():
    p1 = UniformParameter('x', 'x', min=-5, max=5)
    host = InteractiveHost()
    uq = Smolyak([p1], level=2)

    # call the wrapper with a=1, b=2, c=3

    # example using bash wrapper
    prog = TestProgram(desc='Quadratic using bash wrapper',
                       exe="./sim_wrap.sh 1 2 3 $x")

    # example using python wrapper
    """
    prog = TestProgram(desc='Quadratic using bash wrapper',
       exe="./sim_wrap.py 1 2 3 $x")
    """

    return Sweep(uq, host, prog)
