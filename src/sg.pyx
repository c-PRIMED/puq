# -*- Mode: Python -*-

# need both of these to pass numpy arrays to C/C++
import numpy as np
cimport numpy as np

# The C++ function we are using
cdef extern from "sg_cc.h" namespace "webbur": 
     int sparse_grid_cc_size( int dims, int level)
     void sparse_grid_cc(int dims, int level, int point_num, double* grid_weight, double* grid_point)

def sgrid(int dims, int level):
    """
    sgrid(dims, level)
    
    Returns a multidimensional sparse grid based on the Clenshaw Curtis rule.
    The grid will have **dims**+1 columns, with the last column containing the weights.
    """
    point_num = sparse_grid_cc_size(dims, level)
    cdef np.ndarray[np.double_t, ndim=1] grid_weight = np.empty((point_num))
    cdef np.ndarray[np.double_t, ndim=1] grid_point = np.empty((dims * point_num))
    sparse_grid_cc(dims, level, point_num, <double*>grid_weight.data, <double*>grid_point.data )
    return np.column_stack((grid_point.reshape((point_num, dims)), grid_weight))



