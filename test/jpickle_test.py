import numpy as np
from puq import *

"""
Some basic tests of the JSON pickle handlers
"""

def test_numpy_int_array():
    a = np.array([1], dtype=np.int)
    assert a.dtype == np.int
    a = unpickle(pickle(a))
    assert a.dtype == np.int

def test_numpy_int8_array():
    a = np.array([1], dtype=np.int8)
    assert a.dtype == np.int8
    a = unpickle(pickle(a))
    assert a.dtype == np.int8

def test_numpy_int16_array():
    a = np.array([1], dtype=np.int16)
    assert a.dtype == np.int16
    a = unpickle(pickle(a))
    assert a.dtype == np.int16

def test_numpy_int32_array():
    a = np.array([1], dtype=np.int32)
    assert a.dtype == np.int32
    a = unpickle(pickle(a))
    assert a.dtype == np.int32

def test_numpy_int64_array():
    a = np.array([1], dtype=np.int64)
    assert a.dtype == np.int64
    a = unpickle(pickle(a))
    assert a.dtype == np.int64

def test_numpy_float_array():
    a = np.array([1], dtype=np.float)
    assert a.dtype == np.float
    a = unpickle(pickle(a))
    assert a.dtype == np.float

def test_numpy_float32_array():
    a = np.array([1], dtype=np.float32)
    assert a.dtype == np.float32
    a = unpickle(pickle(a))
    assert a.dtype == np.float32

def test_numpy_float64_array():
    a = np.array([1], dtype=np.float64)
    assert a.dtype == np.float64
    a = unpickle(pickle(a))
    assert a.dtype == np.float64

def test_numpy_int():
    a = np.int(42)
    assert a == unpickle(pickle(a))

def test_numpy_int16():
    a = np.int16(42)
    assert a == unpickle(pickle(a))

def test_numpy_float():
    a = np.float(3.1415926)
    assert a == unpickle(pickle(a))

def test_numpy_bool():
    a = np.bool(True)
    assert unpickle(pickle(a)) == True
    a = np.bool(False)
    assert unpickle(pickle(a)) == False

def test_2d_array():
    m = np.arange(1, 5)
    m = np.meshgrid(m, m, m)
    assert np.array_equal(m, unpickle(pickle(m)))
