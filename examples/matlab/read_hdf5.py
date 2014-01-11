#!/usr/bin/env python
"""
This is an example of reading an hdf5 file.

Usage: read_hdf5 file
"""

import sys, h5py
import numpy as np
from puq import PDF

def usage():
    print __doc__
    sys.exit(-1)

if len(sys.argv) != 2:
    usage()

f = h5py.File(sys.argv[1], 'r')

# you can get list of data items like this
hdata = f['output/data']
for x in hdata:
    desc = hdata[x].attrs['description']
    print '%s (%s)' % (x, desc)

# or access them directly if you know the name
impvel = f['output/data/impvel'].value
tclose = f['output/data/tclose'].value

# parameters are under /input/psweep/parameters
e = f['input/psweep/parameters/E/values'].value
gap = f['input/psweep/parameters/gap/values'].value
th = f['input/psweep/parameters/th/values'].value

# put the data and parameters in a big array
# with each data in its own column
big_array = np.column_stack([th,gap,e,impvel,tclose])

# dump the whole thing out on CSV format
import csv
writer = csv.writer(sys.stdout)
for item in big_array:
    writer.writerow(item)

# smolyak method has its own section.
# In it each output variable has the following:
# mean
# dev - std deviation
# uhat
# sampled_pdf - sampled data

# Example. Write impvel PDF in a Adobe PDF file.
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
pdf=PDF(f['smolyak/impvel/sampled_pdf'], fit=True, kernel='G')
plt.plot(pdf.x, pdf.y, 'green', linewidth=1)
pdf.fit = False
plt.plot(pdf.x, pdf.y, 'red', linewidth=1)
plt.savefig('impvel.pdf')
