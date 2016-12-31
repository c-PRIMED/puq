"""
This module implements all the type handlers and wrappers necessary
to use jsonpickle with PUQ.

This file is part of PUQ
Copyright (c) 2013-2016 PUQ Authors
See LICENSE file for terms.
"""

#
# Note: classes must inherit from object to be pickled!!
#
from __future__ import absolute_import, division, print_function

import os
import jsonpickle
import numpy as np
import sympy
from scipy.interpolate import Rbf
from sympy.core.numbers import Float


class NumpyFloatHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        return float(obj)
jsonpickle.handlers.registry.register(np.float, NumpyFloatHandler)
jsonpickle.handlers.registry.register(np.float32, NumpyFloatHandler)
jsonpickle.handlers.registry.register(np.float64, NumpyFloatHandler)


class NumpyIntHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        return int(obj)
jsonpickle.handlers.registry.register(np.int, NumpyIntHandler)
jsonpickle.handlers.registry.register(np.int8, NumpyIntHandler)
jsonpickle.handlers.registry.register(np.int16, NumpyIntHandler)
jsonpickle.handlers.registry.register(np.int32, NumpyIntHandler)
jsonpickle.handlers.registry.register(np.int64, NumpyIntHandler)
jsonpickle.handlers.registry.register(np.uint8, NumpyIntHandler)
jsonpickle.handlers.registry.register(np.uint16, NumpyIntHandler)
jsonpickle.handlers.registry.register(np.uint32, NumpyIntHandler)
jsonpickle.handlers.registry.register(np.uint64, NumpyIntHandler)


class NumpyBoolHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        return bool(obj)
jsonpickle.handlers.registry.register(np.bool, NumpyBoolHandler)


class SympyAddHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        data['value'] = str(obj)
        return data

    def restore(self, obj):
        return sympy.S(obj['value'])
jsonpickle.handlers.registry.register(sympy.Add, SympyAddHandler)


class SympyMulHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        data['value'] = str(obj)
        return data

    def restore(self, obj):
        return sympy.S(obj['value'])
jsonpickle.handlers.registry.register(sympy.Mul, SympyMulHandler)


class SympyFloatHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        data['value'] = str(obj)
        return data

    def restore(self, obj):
        return sympy.S(obj['value'])
jsonpickle.handlers.registry.register(Float, SympyFloatHandler)


class NumpyArrayHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        # print "arrayhandler flatten", obj.dtype
        data['value'] = obj.tolist()
        data['dtype'] = str(obj.dtype)
        return data

    def restore(self, obj):
        # print 'arrayhandler restore', obj
        return np.array(obj['value'], dtype=obj['dtype'])
jsonpickle.handlers.registry.register(np.ndarray, NumpyArrayHandler)


# don't try to flatten this.  Will be handled in _reinit_()
class RbfHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        return data

    def restore(self, obj):
        return obj
jsonpickle.handlers.registry.register(Rbf, RbfHandler)


def pickle(obj):
    return jsonpickle.encode(obj)


def unpickle(st):
    obj = jsonpickle.decode(str(st))
    if hasattr(obj, '_reinit_'):
        obj._reinit_()
    return obj


def LoadObj(filename):
    """
    Reads a json encoded python object from a file.

    :param filename: filename
    :returns: An object.

    :Example:

    >>> u = LoadObj('pdf2.json')
    """
    obj = None
    f = open(filename, 'r')
    obj = unpickle(f.read())
    f.close()
    return obj


def NetObj(addr):
    """
    Retrieves a json encoded python object from a remote address.

    :param addr: URI. Returned object must be stored in JSON format
        (from jpickle)
    :returns: An object

    :Example:

    >>> u = NetObj('http://foo.com/myproject/response')
    """
    from urllib2 import urlopen, URLError
    try:
        response = urlopen(addr)
        val = response.read()
    except URLError as e:
        print(e.reason)
        raise URLError

    return unpickle(val)


def write_json(obj, filename):
    """
    Encode an object with json and write it to a file.

    :param obj: A PUQ object, such as a response function or PDF.
    :param filename: Filename.  If the name has an extension, it must be 'json'.
    Otherwise, '.json' will be appended to the filename.
    Previous files with the same name will be overwritten.
    """
    fn, ext = os.path.splitext(filename)
    if ext and ext != '.json':
        raise ValueError("Filename extension needs to be '.json'")
    filename = fn + '.json'
    with open(filename, 'w') as jfile:
        jfile.write(pickle(obj))
