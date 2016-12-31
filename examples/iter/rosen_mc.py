from puq import *
import numpy as np

def callback(sw, hf):
    d = hdf.get_result(hf, 'z')
    num = len(d)
    mean = np.mean(d)
    dev = np.std(d)
    print("Mean,Dev   = %s, %s" % (mean, dev))
    if num >= 500:
        return True
    sw.psweep.extend(100)
    return False

def run():
    # Declare our parameters here. Both are uniform on [-2, 2]
    x = UniformParameter('x', 'x', min=-2, max=2)
    y = UniformParameter('y', 'y', min=-2, max=2)

    # Create a host
    host = InteractiveHost()

    # Declare a UQ method.
    uq = MonteCarlo([x,y], num=10, response=1, iteration_cb=callback)

    # Our test program
    prog = TestProgram('./rosen_prog.py', desc='Rosenbrock Function (python)')

    return Sweep(uq, host, prog)
