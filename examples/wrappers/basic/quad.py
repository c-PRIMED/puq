from puq import *

def run():
    x = UniformParameter('x', 'x', min=-5, max=5)
    host = InteractiveHost()
    uq = Smolyak([x], level=2)

    # call the wrapper with a=1, b=2, c=3

    # example using bash wrapper
    prog = TestProgram('bash wrapper', desc='Quadratic using bash wrapper',
                       exe="./sim_wrap.sh 1 2 3 $x")

    # example using python wrapper
    """
    prog = TestProgram('bash wrapper', desc='Quadratic using bash wrapper',
       exe="./sim_wrap.py 1 2 3 $x")
    """

    return Sweep(uq, host, prog)
