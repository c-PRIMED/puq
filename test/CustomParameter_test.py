#! /usr/bin/env python
'''
Testsuite for the CustomParameter class
'''
from __future__ import absolute_import, division, print_function
import numpy as np
from puq import *

def _hisplot(y, nbins):
    n, bins = np.histogram(y, nbins, normed=True)
    mids = bins[:-1] + np.diff(bins) / 2.0
    return mids, n

def compare_curves(x1, y1, x2, y2, **args):
    ay = np.interp(x2, x1, y1)
    print("maximum difference is", np.max(np.abs(ay - y2)))
    assert np.allclose(ay, y2, **args)

n = NormalParameter('x','x',mean=10,dev=1)
norm80 = n.pdf.lhs(80)

# test mean and deviation
def test_custom_pdf_meandev():
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(norm80))
    assert np.allclose(c.pdf.mean, 10.0, rtol=.05), "mean=%s" % c.pdf.mean
    assert np.allclose(c.pdf.dev, 1.0, rtol=.05), "dev=%s" % c.pdf.dev

# test lhs()
def test_custom_pdf_lhs():
    a = np.array([2,2,3,3,3,4,4,4,4,5,5,5,5,5,6,6,6,6,6,7,7,7,8,8])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a, fit=True))
    print("LHS: mean=%s  dev=%s" % (c.pdf.mean, c.pdf.dev))
    assert(np.allclose(c.pdf.mean, 5.04, atol=.1))
    assert(np.allclose(c.pdf.dev, 1.9, atol=.1))

    # test the lhs() function to see if the curve it generates is
    # close enough
    data = c.pdf.lhs(1000)
    dx, dy = _hisplot(data, 40)
    compare_curves(c.pdf.x, c.pdf.y, dx, dy, atol=.01)


# test lhs1()
def test_custom_pdf_lhs1():
    a = np.array([12,12,13,13,13,14,14,14,14,15,15,15,15,15,16,16,16,16,16,17,17,17,18,18])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a, fit=True))

    # test the lhs1() function to see if the curve it generates is
    # close enough
    xs = c.pdf.ds1(1000)
    assert len(xs) == 1000
    # scale [-1,1] back to original size
    min, max = c.pdf.range
    mean = (min + max)/2.0
    xs *= max - mean
    xs += mean

    # bin it
    mids, n = _hisplot(xs, 40)
    compare_curves(c.pdf.x, c.pdf.y, mids, n, atol=.004)

    '''
    import matplotlib.pyplot as plt
    plt.plot(mids, n, color='green')
    plt.plot(c.pdf.x, c.pdf.y, color='blue')
    plt.show()
    '''

def test_custom_pdf_random():
    a = np.array([2,2,3,3,3,4,4,4,4,5,5,5,5,5,6,6,6,6,6,7,7,7,8,8])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a, fit=True))

    data = c.pdf.random(100000)
    dx,dy = _hisplot(data, 40)
    compare_curves(c.pdf.x, c.pdf.y, dx, dy, atol=.03)

    '''
    import matplotlib.pyplot as plt
    plt.plot(dx, dy, color='red')
    plt.plot(c.pdf.x, c.pdf.y, color='blue')
    plt.show()
    '''
# test lhs()
def test_custom_pdf_lhs_nofit():
    a = np.array([2,2,3,3,3,4,4,4,4,5,5,5,5,5,6,6,6,6,6,7,7,7,8,8])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a, nbins=40))
    print("LHS: mean=%s  dev=%s" % (c.pdf.mean, c.pdf.dev))
    assert(np.allclose(c.pdf.mean, 5.04, atol=.1))
    assert(np.allclose(c.pdf.dev, 1.7, atol=.1))

    # test the lhs() function to see if the curve it generates is
    # close enough
    data = c.pdf.ds(1000)
    dx,dy = _hisplot(data, 40)
    """
    import matplotlib.pyplot as plt
    plt.plot(dx, dy, color='red')
    plt.plot(c.pdf.x, c.pdf.y, color='blue')
    plt.show()
    """
    compare_curves(c.pdf.x, c.pdf.y, dx, dy, atol=.4)


# test lhs1()
def test_custom_pdf_lhs1_nofit():
    a = np.array([2,2,3,3,3,4,4,4,4,5,5,5,5,5,6,6,6,6,6,7,7,7,8,8])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a, nbins=40))

    # test the lhs1() function to see if the curve it generates is
    # close enough
    xs = c.pdf.ds1(1000)
    assert len(xs) == 1000
    # scale [-1,1] back to original size
    min, max = c.pdf.range
    mean = (min + max)/2.0
    xs *= max - mean
    xs += mean

    # bin it
    mids, n = _hisplot(xs, 40)
    compare_curves(c.pdf.x, c.pdf.y, mids, n, atol=.4)

    '''
    import matplotlib.pyplot as plt
    plt.plot(mids, n, color='green')
    plt.plot(c.pdf.x, c.pdf.y, color='blue')
    plt.show()
    '''

def test_custom_pdf_random_nofit():
    a = np.array([2,2,3,3,3,4,4,4,4,5,5,5,5,5,6,6,6,6,6,7,7,7,8,8])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a, nbins=40))

    data = c.pdf.random(100000)
    dx,dy = _hisplot(data, 40)
    compare_curves(c.pdf.x, c.pdf.y, dx, dy, atol=.4)

    '''
    import matplotlib.pyplot as plt
    plt.plot(dx, dy, color='red')
    plt.plot(c.pdf.x, c.pdf.y, color='blue')
    plt.show()
    '''

def test_custom_pdf_small():
    a = np.array([2,3,2])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a))
    assert np.allclose(c.pdf.mean, 7.0/3, atol=.3), "mean=%s" % c.pdf.mean
    assert np.allclose(c.pdf.dev, 0.4, atol=.2), "dev=%s" % c.pdf.dev

def test_custom_pdf_small_fit():
    a = np.array([2,3,2])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a, fit=True))
    assert np.allclose(c.pdf.mean, 7.0/3, atol=.3), "mean=%s" % c.pdf.mean
    assert np.allclose(c.pdf.dev, 0.4, atol=.4), "dev=%s" % c.pdf.dev


# single data point.  Must use Bayesian fit.
def test_custom_pdf_single_fit():
    a = np.array([42])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a, error=NormalPDF(0,.1)))
    assert np.allclose(c.pdf.mean, 42), "mean=%s" % c.pdf.mean
    assert np.allclose(c.pdf.dev, .1, atol=.01), "dev=%s" % c.pdf.dev

def test_custom_pdf_single():
    a = np.array([42])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a))
    assert c.pdf.mean == 42
    assert c.pdf.dev == 0
    assert c.pdf.mode == 42


def test_custom_pdf_zero():
    a = np.array([0])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a))
    assert c.pdf.mean == 0
    assert c.pdf.dev == 0
    assert c.pdf.mode == 0


def test_custom_pdf_zerozero():
    a = np.array([0, 0])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a))
    assert c.pdf.mean == 0
    assert c.pdf.dev == 0
    assert c.pdf.mode == 0


def test_custom_pdf_zerozerozero():
    a = np.array([0, 0, 0])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a))
    assert c.pdf.mean == 0
    assert c.pdf.dev == 0
    assert c.pdf.mode == 0


def test_custom_pdf_zerozerozero_fit():
    a = np.array([0, 0, 0])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a, fit=True))
    assert c.pdf.mean == 0
    assert c.pdf.dev == 0
    assert c.pdf.mode == 0


def test_custom_pdf_const():
    a = np.array([2,2,2,2,2,2,2,2,2,2,2])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a))
    assert c.pdf.mean == 2
    assert c.pdf.dev == 0
    assert c.pdf.mode == 2


def test_custom_pdf_const_fit():
    a = np.array([2,2,2,2,2,2,2,2,2,2,2])
    c = CustomParameter('x', 'unknown', pdf=ExperimentalPDF(a, fit=True))
    assert c.pdf.mean == 2
    assert c.pdf.dev == 0
    assert c.pdf.mode == 2


#### EXCEPTION TESTING

# forget to include pdf
def test_custom_pdf_exception():
    ok = False
    try:
        c = CustomParameter('x', 'X, the unknown')
    except ValueError:
        ok = True
    except:
        assert False, 'Wrong Exception'
    if not ok:
        assert False, 'No Exception when one was expected'


if __name__ == "__main__":
    test_custom_pdf_meandev()
    test_custom_pdf_lhs()
    test_custom_pdf_lhs1()
    test_custom_pdf_random()
    test_custom_pdf_lhs_nofit()
    test_custom_pdf_lhs1_nofit()
    test_custom_pdf_random_nofit()
    test_custom_pdf_exception()
    test_custom_pdf_small()
    test_custom_pdf_small_fit()
    test_custom_pdf_single()
    test_custom_pdf_single_fit()
    test_custom_pdf_const()
    test_custom_pdf_const_fit()
    test_custom_pdf_zero()
    test_custom_pdf_zerozero()
    test_custom_pdf_zerozerozero()
    test_custom_pdf_zerozerozero_fit()
