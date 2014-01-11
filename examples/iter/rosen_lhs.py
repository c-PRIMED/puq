from puq import *
import numpy as np
import puq.hdf

done = 0
def callback(sw, hf):
    global done
    # call hdf.get_result(hf) to get output array
    print "Callback"
    if done < 4:
        done += 1
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
    uq = LHS([x,y], num=10, ds=1, response=1, iteration_cb=callback)

    # Our test program
    prog = TestProgram('./rosen_prog.py', desc='Rosenbrock Function (python)')

    return Sweep(uq, host, prog)
