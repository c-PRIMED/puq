from puq import *
import numpy as np


def callback(sw, hf):
    data = hdf.get_result(hf)
    print 'Callback %s points.  mean=%s, dev=%s' % (len(data), np.mean(data), np.std(data))    

    # normally we would have some other check here to see if more data points
    # need to be done
    if len(data) < 500 :
        valarray = np.vstack((np.linspace(-2, 2, 500),np.linspace(-2, 2, 500)))
        sw.psweep.extend(valarray)
        return False
    return True

def run():
    # Declare our parameters here. Both are uniform on [-2, 2]
    x = UniformParameter('x', 'x', min=-2, max=2)
    y = UniformParameter('y', 'y', min=-2, max=2)

    # Create a host
    host = InteractiveHost()

    # Declare a UQ method.
    valarray = np.vstack((np.linspace(-2,2,2),np.linspace(-2,2,2)))
    uq = SimpleSweep([x,y], valarray, iteration_cb=callback)

    # Our test program
    prog = TestProgram('./rosen_prog.py', desc='Rosenbrock Function (python)')

    return Sweep(uq, host, prog)
