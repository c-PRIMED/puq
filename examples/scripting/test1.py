#!/usr/bin/env python
"""
Example of scripting a PUQ run, extending it, and plotting PDFs
"""

import puq
import numpy as np
import matplotlib
matplotlib.use('tkagg', warn=False)
import matplotlib.pyplot as plt

# save to this filename
fname = 'script_test.hdf5'

# our input parameters
v1 = puq.Parameter('x', 'velocity1', mean=10, dev=2)
v2 = puq.Parameter('y', 'velocity2', mean=100, dev=3)

# run a level 1 Smolyak
uq = puq.Smolyak([v1, v2], 1)
sw = puq.Sweep(uq, puq.InteractiveHost(), './basic_prog.py')
sw.run(fname)

# get the response surface for output variable 'h'
rs = puq.hdf.get_response(fname, 'h')
# sample the response surface to get a PDF
val, samples = rs.pdf(fit=True, return_samples=True)
# plot it in blue
val.plot(color='b')
print 'Run 1: mean=%s   dev=%s\n' % (np.mean(samples), np.std(samples))

# not extend the run to a level 2
sw.extend()
sw.run()

# plot the PDF like before, but in green
rs = puq.hdf.get_response(fname, 'h')
val, samples = rs.pdf(fit=True, return_samples=True)
val.plot(color='g')
print 'Run 2: mean=%s   dev=%s' % (np.mean(samples), np.std(samples))

plt.show()


