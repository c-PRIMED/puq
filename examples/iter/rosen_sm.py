from puq import *

# Example callback that causes the sweep
# to repeat until a specific condition is met.
def callback(sw, hf):
    rmsep = hdf.get_response(hf,'z').rmse()[1]
    print 'callback: rmse=%s%%' % rmsep

    # iterate until error < 1%
    if rmsep > 1:
        sw.psweep.extend()
        return False
    return True

def run():
    # Declare our parameters here. Both are uniform on [-2, 2]
    x = UniformParameter('x', 'x', min=-2, max=2)
    y = UniformParameter('y', 'y', min=-2, max=2)

    # Create a host
    host = InteractiveHost()

    # Declare a UQ method.
    uq = Smolyak([x,y], level=1, iteration_cb=callback)

    # Our test program
    prog = TestProgram('./rosen_prog.py', desc='Rosenbrock Function')

    return Sweep(uq, host, prog)
