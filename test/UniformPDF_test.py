#! /usr/bin/env python
'''
Testsuite for the UniformPDF class
'''
from __future__ import absolute_import, division, print_function

import numpy as np
from puq import *
import scipy.stats as stats


def _hisplot(y, nbins):
    n, bins = np.histogram(y, nbins, normed=True)
    mids = bins[:-1] + np.diff(bins) / 2.0
    return mids, n


def compare_curves(x1, y1, x2, y2, **args):
    ay = np.interp(x2, x1, y1)
    rmse = np.sqrt(np.sum((ay - y2)**2))
    print("maximum difference is", np.max(np.abs(ay - y2)))
    print("RMSE=%s" % rmse)
    # assert rmse < .002
    assert np.allclose(ay, y2, **args)


def _test_updf(min, max):
    options['pdf']['samples'] = 1000

    c = UniformPDF(min=min, max=max)
    assert isinstance(c, PDF)

    x = c.x
    y = stats.uniform(min, max-min).pdf(x)
    rmse = np.sqrt(np.sum((c.y - y)**2))
    print("RMSE=%s" % rmse)
    print("MaxError=", np.max(abs(c.y - y)))
    assert rmse < 1e-11


def _test_ucdf(min, max):
    options['pdf']['samples'] = 1000

    c = UniformPDF(min=min, max=max)

    cdfy = stats.uniform(min, max-min).cdf(c.x)
    rmse = np.sqrt(np.sum((c.cdfy - cdfy)**2))
    print("RMSE=%s" % rmse)
    print("MaxError=", np.max(abs(c.cdfy - cdfy)))
    assert rmse < 1e-11

    """
    import matplotlib.pyplot as plt
    plt.plot(c.x, c.cdfy, color='green')
    plt.plot(c.x, cdfy, color='red')
    plt.show()
    """


# test mean, min, max and deviation
def _test_uniform_minmeanmax(min, mean, max):
    c = UniformPDF(min=min, mean=mean, max=max)
    cmin, cmax = c.range
    print("min=%s mean=%s  max=%s" % (cmin, c.mean, cmax))

    if min is not None:
        assert min == cmin
    else:
        assert cmin == mean - (max - mean)
    if max is not None:
        assert max == cmax
    else:
        assert cmax == mean + (mean - min)
    if mean is not None:
        assert np.allclose(mean, c.mean)
    else:
        assert np.allclose(c.mean, (min + max) / 2.0)


# test lhs()
def _test_uniform_lhs(min, max):
    c = UniformPDF(min=min, max=max)

    # test the lhs() function to see if the curve it generates is
    # close enough
    data = c.ds(10000)
    assert len(data) == 10000
    assert np.min(data) >= min
    assert np.max(data) <= max
    dx, dy = _hisplot(data, 20)

    x = dx
    y = stats.uniform(min, max-min).pdf(x)
    compare_curves(x, y, dx, dy, atol=.0001)

    """
    import matplotlib.pyplot as plt
    plt.plot(x, y, color='red')
    plt.plot(dx, dy, color='blue')
    plt.show()
    """

    assert np.allclose(c.mean, np.mean(data), rtol=.001), 'mean=%s' % np.mean(data)


# test lhs1()
def _test_uniform_lhs1(min, max):
    c = UniformPDF(min=min, max=max)

    data = c.ds1(1000)
    xs = data
    assert len(xs) == 1000

    assert min, max == c.range
    # scale [-1,1] back to original size

    mean = (min + max)/2.0
    xs *= max - mean
    xs += mean
    dx, dy = _hisplot(xs, 20)

    x = dx
    y = stats.uniform(min, max-min).pdf(x)
    compare_curves(x, y, dx, dy, atol=.001)

    """
    import matplotlib.pyplot as plt
    plt.plot(x, y, color='green')
    plt.plot(dx, dy, color='blue')
    plt.show()
    """
    assert np.allclose(c.mean, np.mean(data), rtol=.001), 'mean=%s' % np.mean(data)


def _test_uniform_random(min, max):
    c = UniformPDF(min=min, max=max)

    data = c.random(1000000)
    assert len(data) == 1000000
    dx, dy = _hisplot(data, 20)

    x = dx
    y = stats.uniform(min, max-min).pdf(x)
    compare_curves(x, y, dx, dy, atol=.02)

    assert np.min(data) >= min
    assert np.max(data) <= max

    """
    import matplotlib.pyplot as plt
    plt.plot(dx, dy, color='red')
    plt.plot(x, y, color='blue')
    plt.show()
    """
    assert np.allclose(c.mean, np.mean(data), rtol=.001), 'mean=%s' % np.mean(data)


def test_updf():
    _test_updf(10,20)
    _test_updf(-20,-10)


def test_ucdf():
    _test_ucdf(100,105)
    _test_ucdf(-1,2)


def test_uniform_minmeanmax():
    _test_uniform_minmeanmax(0,None,20)
    _test_uniform_minmeanmax(None,0.5,2)
    _test_uniform_minmeanmax(5,10,15)
    _test_uniform_minmeanmax(5,10,None)


def test_uniform_lhs():
    _test_uniform_lhs(10,20)
    _test_uniform_lhs(-100, -50)


def test_uniform_lhs1():
    _test_uniform_lhs1(10,20)
    _test_uniform_lhs1(-100, -50)


def test_uniform_random():
    _test_uniform_random(10,20)

if __name__ == "__main__":
    test_updf()
    test_ucdf()
    test_uniform_minmeanmax()
    test_uniform_lhs()
    test_uniform_lhs1()
    test_uniform_random()
