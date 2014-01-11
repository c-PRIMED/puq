"""
Convenience functions that read or write to the HDF5 file

This file is part of PUQ
Copyright (c) 2013 PUQ Authors
See LICENSE file for terms.
"""

import h5py
from puq.jpickle import unpickle
from functools import wraps

def hdf5_wrap(func):
    @wraps(func)
    def wrapped(hf, *args, **kargs):
        close = False
        if type(hf) == str:
            hf = h5py.File(hf, 'r')
            close = True
        res = func(hf, *args, **kargs)
        if close:
            hf.close()
        return res
    return wrapped

@hdf5_wrap
def get_output_names(hf):
    """
    Returns a sorted list of the output variables names in the HDF5 file.

    Args:

    - *hf* : An open filehandle.
    - *fn* : Filename. If *hf* is None then this file will be opened, read, then closed.
    """
    return sorted(map(str, hf['/output/data'].keys()))

@hdf5_wrap
def set_result(hf, var, data, desc=''):
    """
    Sets values of the output variable. Writes array to '/output/data/var'.

    Args:

    - *hf* : An open filehandle.
    - *var* : Output variable name.
    - *data* : Array of data to write.
    - *desc* : Description.
    - *fn* : Filename. If *hf* is None then this file will be opened, read, then closed.
    """
    try:
        del hf['/output/data/%s' % var]
    except:
        pass
    hf['/output/data/%s' % var] = data
    hf['/output/data/%s' % var].attrs['description'] = desc

@hdf5_wrap
def get_result(hf, var=None):
    """
    Returns an array containing the values of the output variable.

    Args:

    - *hf* : An open filehandle.
    - *fn* : Filename. If *hf* is None then this file will be opened, read, then closed.
    - *var* : Output variable name. Only required if there is more than one output variable.
    """
    if not '/output/data' in hf:
        return []

    output_variables = get_output_names(hf)
    if len(output_variables) == 0:
        return []

    if var and not var in output_variables:
        print "Variable %s not found in output data" % var
        raise ValueError
    if not var:
        if len(output_variables) > 1:
            print "Output data contains multiple variables."
            print "You must indicate which you want."
            raise ValueError
        var = output_variables[0]

    return hf['/output/data/%s' % var].value

@hdf5_wrap
def get_param_names(hf):
    """
    Returns a list of the input parameter names in the HDF5 file.

    Args:

    - *hf* : An open filehandle.
    - *fn* : Filename. If *hf* is None then this file will be opened, read, then closed.
    """
    parameters = get_params(hf)
    return [p.name for p in parameters]

@hdf5_wrap
def get_params(hf):
    """
    Returns a list of arrays of input parameter values.

    Args:

    - *hf* : An open filehandle.
    - *fn* : Filename. If *hf* is None then this file will be opened, read, then closed.
    """
    return [unpickle(hf['/input/params'][p].value) for p in hf['/input/params']]

@hdf5_wrap
def data_description(hf, var):
    """
    Returns the description of an output variable. If the description is empty,
    returns the variable name.

    Args:

    - *hf* : An open filehandle.
    - *var* : Output variable name.
    - *fn* : Filename. If *hf* is None then this file will be opened, read, then closed.
    """
    desc = hf['/output/data/%s' % var].attrs['description']
    if desc:
        return desc
    return var

@hdf5_wrap
def param_description(hf, var):
    """
    Returns the description of an input variable. If the description is empty,
    returns the variable name.

    Args:

    - *hf* : An open filehandle.
    - *var* : Input variable name.
    - *fn* : Filename. If *hf* is None then this file will be opened, read, then closed.
    """
    desc = unpickle(hf['/input/params/%s' % var].value).description
    if desc:
        return desc
    return var

@hdf5_wrap
def get_response(hf, var):
    """
    Returns the response function for an output.

    Args:

    - *hf* : An open filehandle.
    - *var* : Variable name.
    - *fn* : Filename. If *hf* is None then this file will be opened, read, then closed.
    """
    psweep = hf.attrs['UQtype']
    return unpickle(hf['/%s/%s/response' % (psweep, var)].value)
