import h5py
from puq import *
import numpy as np

# open hdf5 file
h = h5py('sweep_51723317.hdf5')

# get the output variable array
data = hdf.get_result(h)

# alternative
#data = h['/output/data/z'].value

# get the parameter values
pa = h['/input/param_array'].value

# create an array with parameters and output in columns
vals_and_data = np.column_stack((pa, data))

h.close()
