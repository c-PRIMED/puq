from puq import *
import numpy as np

""" 
Another example of Adaptive Stochastic Collocation, this
time demonstrating a callback function.
"""

# The callback args are specific to each APSweep method. For AdapStocColl,
# they look like the following.  You could do other things here, like
# plot the data, or print other statistics on it.
def my_cb(inum, h5, data, m, v, e):
    print "Iteration %d: %d new points, %d total" % \
        (inum, len(data), len(hdf5_get_result(h5, iteration='sum')))
    print "mean=%s\tvar=%s\terrind=%s\n" % (m,v,e)

def run():
    x = UniformParameter('x', 'x', min=0, max=1)
    y = UniformParameter('y', 'y', min=0, max=1)

    host = InteractiveHost()
    prog = TestProgram('./dome_prog.py')
    uq = AdapStocColl([x,y], tol=1.0e-2, callback=my_cb)
    return Sweep(uq, host, prog)




