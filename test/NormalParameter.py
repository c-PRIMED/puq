#! /usr/bin/env python
'''
Testsuite for the NormalParameter class
'''

import numpy as np
from puq import *


def test_normal():
    n = Parameter("name", "description", mean=100, dev=2)
    assert n
    assert isinstance(n, Parameter)
    assert isinstance(n, NormalParameter)
    assert np.allclose(n.pdf.mean, 100), 'Error: mean was %s' % n.pdf.mean
    assert np.allclose(n.pdf.dev, 2, rtol=.1), 'Error: dev was %s' % n.pdf.dev

def test_normal2():
    n = NormalParameter("name", "description", mean=1000, dev=14)
    assert n
    assert isinstance(n, Parameter)
    assert isinstance(n, NormalParameter)
    assert np.allclose(n.pdf.mean, 1000), 'Error: mean was %s' % n.pdf.mean
    assert np.allclose(n.pdf.dev, 14, rtol=.1), 'Error: dev was %s' % n.pdf.dev

#### EXCEPTION TESTING

def test_normal_exception1():
    ok = False
    try:
        c = NormalParameter('x', 'unknown')
    except TypeError:
        ok = True
    except:
        assert False, 'Wrong Exception'
    if not ok:
        assert False, 'No Exception when one was expected'

def test_normal_exception2():
    ok = False
    try:
        c = NormalParameter('x', 'unknown', mean=10)
    except TypeError:
        ok = True
    except:
        assert False, 'Wrong Exception'
    if not ok:
        assert False, 'No Exception when one was expected'

def test_normal_exception3():
    ok = False
    try:
        c = NormalParameter('x', 'unknown', dev=1)
    except TypeError:
        ok = True
    except:
        assert False, 'Wrong Exception'
    if not ok:
        assert False, 'No Exception when one was expected'

def test_normal_exception4():
    ok = False
    try:
        c = NormalParameter('x', 'unknown', mean=0, dev=-1)
    except ValueError:
        ok = True
    except:
       assert False, 'Wrong Exception'
    if not ok:
        assert False, 'No Exception when one was expected'

def test_pickle():
    m = NormalParameter("name", "description", mean=1000, dev=14)
    n = unpickle(pickle(m))
    assert n
    assert isinstance(n, Parameter)
    assert isinstance(n, NormalParameter)
    assert np.allclose(n.pdf.mean, 1000), 'Error: mean was %s' % n.pdf.mean
    assert np.allclose(n.pdf.dev, 14, rtol=.1), 'Error: dev was %s' % n.pdf.dev
    assert np.all(m.pdf.x == n.pdf.x)
    assert np.all(m.pdf.y == n.pdf.y)
    assert np.all(m.pdf.mode == n.pdf.mode)
    assert np.all(m.pdf.cdfy == n.pdf.cdfy)

if __name__ == "__main__":
    test_normal()
    test_normal2()
    test_normal_exception1()
    test_normal_exception2()
    test_normal_exception3()
    test_normal_exception4()
    test_pickle()


