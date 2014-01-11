import numpy as np

def dump_hdf5(name, v, desc=''):
    np.set_printoptions(threshold=np.nan)
    print 'HDF5:%s:5FDH' % repr({'name': name, 'desc': desc, 'value':v})
