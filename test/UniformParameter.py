#! /usr/bin/env python
'''
Testsuite for the UniformParameter class
'''
import numpy as np
from puq import *

def test_uniform():
    n = Parameter("name", "description", mean=100, min=98)
    assert n
    assert isinstance(n, Parameter)
    assert isinstance(n, UniformParameter)
    assert np.allclose(n.pdf.mean, 100), 'Error: mean was %s' % n.pdf.mean
    assert n.pdf.range[0]==98, 'Error: min was %s' % n.pdf.range[0]
    assert n.pdf.range[1]==102, 'Error: max was %s' % n.pdf.range[1]

def test_uniform2():
    n = UniformParameter("name", "description", min=-41, max=-20)
    assert n
    assert isinstance(n, Parameter)
    assert isinstance(n, UniformParameter)
    assert np.allclose(n.pdf.mean, -30.5), 'Error: mean was %s' % n.pdf.mean
    assert n.pdf.range[0] == -41, 'Error: min was %s' % n.pdf.range[0]
    assert n.pdf.range[1] == -20, 'Error: max was %s' % n.pdf.range[1]

#### EXCEPTION TESTING

def test_uniform_exception1():
    ok = False
    try:
        c = UniformParameter('x', 'unknown', mean=10, max=8)
    except ValueError:
        ok = True
    except:
        assert False, 'Wrong Exception'
    if not ok:
        assert False, 'No Exception when one was expected'

def test_uniform_exception2():
    ok = False
    try:
        c = UniformParameter('x', 'unknown', mean=10)
    except ValueError:
        ok = True
    except:
        assert False, 'Wrong Exception'
    if not ok:
        assert False, 'No Exception when one was expected'

def test_uniform_exception3():
    ok = False
    try:
        c = UniformParameter('x', 'unknown', min=12, max=8)
    except ValueError:
        ok = True
    except:
        assert False, 'Wrong Exception'
    if not ok:
        assert False, 'No Exception when one was expected'


def test_uniform_exception4():
    ok = False
    try:
        c = UniformParameter('x', 'unknown', mean=10, min=8, max=13)
    except ValueError:
        ok = True
    except:
        assert False, 'Wrong Exception'
    if not ok:
        assert False, 'No Exception when one was expected'

def test_pickle():
    m = Parameter("name", "description", mean=100, min=98)
    n = unpickle(pickle(m))
    assert n
    assert isinstance(n, Parameter)
    assert isinstance(n, UniformParameter)
    assert np.allclose(n.pdf.mean,100), 'Error: mean was %s' % n.pdf.mean
    assert n.pdf.range[0]==98, 'Error: min was %s' % n.pdf.range[0]
    assert n.pdf.range[1]==102, 'Error: max was %s' % n.pdf.range[1]

if __name__ == "__main__":
    test_uniform()
    test_uniform2()
    test_uniform_exception1()
    test_uniform_exception2()
    test_uniform_exception3()
    test_uniform_exception4()
    test_pickle()

