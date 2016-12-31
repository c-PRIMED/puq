#! /usr/bin/env python
'''
Testsuite for the NormalPDF class
'''
from __future__ import absolute_import, division, print_function

import numpy as np
from puq import *
import scipy.stats as stats
from puq.options import options

options['pdf']['range'] = 0.999999

def _hisplot(y, nbins):
    n, bins = np.histogram(y, nbins, normed=True)
    mids = bins[:-1] + np.diff(bins) / 2.0
    return mids, n

def compare_curves(x1, y1, x2, y2, **args):
    ay = np.interp(x2, x1, y1)
    rmse = np.sqrt(np.sum((ay - y2)**2))
    print("maximum difference is", np.max(np.abs(ay - y2)))
    print("RMSE=%s" % rmse)
    assert rmse < .02
    #assert np.allclose(ay, y2, **args)

def _test_npdf(mean, dev, nsamples):
    options['pdf']['samples'] = nsamples

    c = NormalPDF(mean=mean, dev=dev)
    assert isinstance(c, PDF)

    print("Normal(%s, %s)" % (mean, dev))

    sfunc = stats.norm(mean, dev)
    x = c.x
    y = sfunc.pdf(x)
    rmse = 100.0 * np.sqrt(np.mean((c.y - y)**2)) / (np.max(c.y) - np.min(c.y))
    print("PDF for %d points:" % len(x))
    print("\tRMSE (%d points)=%s %%" % (len(x), rmse))
    assert rmse < .01

    # for Normal distributions, range is truncated
    _range = options['pdf']['range']
    range = [(1.0 - _range)/2.0, (1.0 + _range)/2.0]
    assert np.allclose(c.range, sfunc.ppf(range))

    # now compare linear interpolated pdf versus reference
    ref_num_points = 100000

    x = np.linspace(sfunc.ppf(.000001),sfunc.ppf(.999999), ref_num_points)
    y = sfunc.pdf(x)
    interp_y = c.pdf(x)
    rmse = 100.0 * np.sqrt(np.mean((interp_y - y)**2))/ (np.max(y) - np.min(y))
    print("\tRMSE (%d points)=%s %%" % (ref_num_points,rmse))
    assert rmse < .05

    """
    import matplotlib.pyplot as plt
    plt.plot(x,y, color='green')
    plt.plot(x, interp_y, color='red')
    plt.show()
    """


def _test_npdf_trunc(mean, dev, min, max):
    print("Normal(%s, %s, min=%s, max=%s)" % (mean, dev, min, max))
    options['pdf']['samples'] = 1000
    c = NormalPDF(mean=mean, dev=dev, min=min, max=max)
    if min != None:
        a = (float(min) - mean) / dev
    else:
        a = -4.
    if max != None:
        b = (float(max) - mean) / dev
    else:
        b = 4.
    sfunc = stats.truncnorm(a, b, loc=mean, scale=dev)
    x = c.x
    y = sfunc.pdf(x)
    rmse = 100.0 * np.sqrt(np.mean((c.y - y)**2)) / (np.max(c.y) - np.min(c.y))
    print("PDF for %d points:" % len(x))
    print("\tRMSE (%d points)=%s %%" % (len(x), rmse))
    assert rmse < .01

    # now compare linear interpolated pdf versus reference
    ref_num_points = 100000

    x = np.linspace(sfunc.ppf(.000001),sfunc.ppf(.999999), ref_num_points)
    y = sfunc.pdf(x)
    interp_y = c.pdf(x)
    rmse = 100.0 * np.sqrt(np.mean((interp_y - y)**2))/ (np.max(y) - np.min(y))
    print("\tRMSE (%d points)=%s %%" % (ref_num_points,rmse))
    assert rmse < .05

    """
    import matplotlib.pyplot as plt
    plt.plot(x,y, color='red')
    plt.plot(x, interp_y, color='green')
    plt.show()
    """

def _test_ncdf_trunc(mean, dev, min, max):
    print("CDF Normal(%s, %s, min=%s, max=%s)" % (mean, dev, min, max))
    options['pdf']['samples'] = 1000
    c = NormalPDF(mean=mean, dev=dev, min=min, max=max)
    if min is not None:
        a = (float(min) - mean) / dev
    else:
        a = -4.
    if max is not None:
        b = (float(max) - mean) / dev
    else:
        b = 4.
    sfunc = stats.truncnorm(a, b, loc=mean, scale=dev)
    x = c.x
    y = sfunc.cdf(x)
    rmse = 100.0 * np.sqrt(np.mean((c.cdfy - y)**2)) / (np.max(c.cdfy) - np.min(c.cdfy))
    print("PDF for %d points:" % len(x))
    print("\tRMSE (%d points)=%s %%" % (len(x), rmse))
    assert rmse < .01

    # now compare linear interpolated pdf versus reference
    ref_num_points = 100000

    x = np.linspace(sfunc.ppf(.000001), sfunc.ppf(.999999), ref_num_points)
    y = sfunc.cdf(x)
    interp_y = c.cdf(x)
    rmse = 100.0 * np.sqrt(np.mean((interp_y - y)**2)) / (np.max(y) - np.min(y))
    print("\tRMSE (%d points)=%s %%" % (ref_num_points, rmse))
    assert rmse < .05

    """
    import matplotlib.pyplot as plt
    plt.plot(x,y, color='red')
    plt.plot(x, interp_y, color='green')
    plt.show()
    """

def _test_ncdf(mean, dev, nsamples):
    print("CDF Normal(%s, %s)" % (mean, dev))
    options['pdf']['samples'] = nsamples

    c = NormalPDF(mean=mean, dev=dev)

    sfunc = stats.norm(mean, dev)
    cdfy = sfunc.cdf(c.x)
    rmse = np.sqrt(np.sum((c.cdfy - cdfy)**2))
    rmse = 100.0 * np.sqrt(np.mean((c.cdfy - cdfy)**2)) / (np.max(c.cdfy) - np.min(c.cdfy))
    print("CDF for %d points:" % len(c.x))
    print("\tRMSE (%d points)=%s %%" % (len(c.x), rmse))
    assert rmse < .01

    # now compare linear interpolated cdf versus reference
    ref_num_points = 100000
    x = np.linspace(sfunc.ppf(.000001), sfunc.ppf(.999999), ref_num_points)
    y = sfunc.cdf(x)
    interp_y = c.cdf(x)
    rmse = 100.0 * np.sqrt(np.mean((interp_y - y)**2)) / (np.max(y) - np.min(y))
    print("\tRMSE (%d points)=%s %%" % (ref_num_points, rmse))
    assert rmse < .05

    """
    import matplotlib.pyplot as plt
    plt.plot(c.x, c.cdfy, color='green')
    plt.plot(c.x, cdfy, color='red')
    plt.show()
    """
# test mean and deviation
def _test_normal_meandev(m, d):
    c = NormalPDF(mean=m, dev=d)

    print("m=%s c.mean=%s" % (m, c.mean))
    assert np.allclose(c.mean, m, rtol=.001)
    print("d=%s c.dev=%s" % (d, c.dev))
    assert np.allclose(c.dev, d, rtol=.001)


# test ds()
def _test_normal_ds(m, d):
    options['pdf']['samples'] = 1000
    c = NormalPDF(mean=m, dev=d)

    # test the lhs() function to see if the curve it generates is
    # close enough
    data = c.ds(1000)
    assert len(data) == 1000
    dx,dy = _hisplot(data, 30)

    x = np.arange(m - 3.*d, m + 3.*d, .01)
    y = stats.norm(m,d).pdf(x)
    compare_curves(x, y, dx, dy, atol=.001)

    # check mean and std deviation
    print("MEAN=",m, np.mean(data))
    print("DEV=",d, np.std(data))
    assert np.allclose(m, np.mean(data), rtol=.01)
    assert np.allclose(d, np.std(data), rtol=.02), 'Dev = %s' % np.std(data)

    """
    import matplotlib.pyplot as plt
    plt.plot(x, y, color='green')
    plt.plot(dx, dy, color='blue')
    plt.show()
    """
def _test_normal_lhs(m, d):
    options['pdf']['samples'] = 1000
    c = NormalPDF(mean=m, dev=d)

    # test the lhs() function to see if the curve it generates is
    # close enough
    data = c.lhs(1000)
    assert len(data) == 1000
    dx, dy = _hisplot(data, 30)

    x = np.arange(m - 3.*d, m + 3.*d, .01)
    y = stats.norm(m, d).pdf(x)
    compare_curves(x, y, dx, dy, atol=.001)

    # check mean and std deviation
    assert np.allclose(m, np.mean(data), rtol=.01)
    assert np.allclose(d, np.std(data), rtol=.01), 'Dev = %s' % np.std(data)

    """
    import matplotlib.pyplot as plt
    plt.plot(x, y, color='green')
    plt.plot(dx, dy, color='blue')
    plt.show()
    """

# test ds1()
def _test_normal_ds1(m, d):
    options['pdf']['samples'] = 1000
    c = NormalPDF(mean=m, dev=d)

    # test the lhs1() function to see if the curve it generates is
    # close enough
    data = c.ds1(1000)
    xs = data
    assert len(xs) == 1000
    # scale [-1,1] back to original size
    max, min = c.range
    mean = (max + min)/2.0
    xs *= max - mean
    xs += mean
    dx, dy = _hisplot(xs, 30)

    x = np.arange(m - 3.*d, m + 3.*d, .01)
    y = stats.norm(m, d).pdf(x)
    compare_curves(x, y, dx, dy, atol=.003)

    print("MEAN=", m, np.mean(data))
    print("DEV=", d, np.std(data))
    assert np.allclose(m, np.mean(data), rtol=.01)
    assert np.allclose(d, np.std(data), rtol=.02)

    """
    import matplotlib.pyplot as plt
    plt.plot(x, y, color='green')
    plt.plot(dx, dy, color='blue')
    plt.show()
    """
# test lhs1()
def _test_normal_lhs1(m, d):
    options['pdf']['samples'] = 1000
    c = NormalPDF(mean=m, dev=d)

    # test the lhs1() function to see if the curve it generates is
    # close enough
    data = c.lhs1(1000)
    xs = data
    assert len(xs) == 1000
    # scale [-1,1] back to original size
    max, min = c.range
    mean = (max + min)/2.0
    xs *= max - mean
    xs += mean
    dx, dy = _hisplot(xs, 30)

    x = np.arange(m - 3.*d, m + 3.*d, .01)
    y = stats.norm(m, d).pdf(x)
    compare_curves(x, y, dx, dy, atol=.003)

    print("MEAN=", np.mean(data))
    print("DEV=", np.std(data))
    assert np.allclose(m, np.mean(data), rtol=.01)
    assert np.allclose(d, np.std(data), rtol=.01)

    """
    import matplotlib.pyplot as plt
    plt.plot(x, y, color='green')
    plt.plot(dx, dy, color='blue')
    plt.show()
    """

def _test_normal_random(m, d):
    options['pdf']['samples'] = 1000
    c = NormalPDF(mean=m, dev=d)

    data = c.random(1000000)
    dx, dy = _hisplot(data, 50)

    x = np.arange(m - 3.*d, m + 3.*d, .01)
    y = stats.norm(m, d).pdf(x)
    compare_curves(x, y, dx, dy, atol=.005)

    print("MEAN=", np.mean(data))
    print("DEV=", np.std(data))
    assert np.allclose(m, np.mean(data), rtol=.01)
    assert np.allclose(d, np.std(data), rtol=.01)

    """
    import matplotlib.pyplot as plt
    plt.plot(dx, dy, color='red')
    plt.plot(x, y, color='blue')
    plt.show()
    """

def test_pdf():
    _test_npdf(0,1,100)
    _test_npdf(0,1,1000)
    _test_npdf(10,2,100)
    _test_npdf(10,2,1000)
    _test_npdf(-10,3,100)
    _test_npdf(-10,3,1000)

def test_pdf_trunc():
    _test_npdf_trunc(20,3,20,30)
    _test_npdf_trunc(8,3,0,None)
    _test_npdf_trunc(-8,3,None,0)

def test_cdf():
    _test_ncdf(0,1,100)
    _test_ncdf(0,1,1000)
    _test_ncdf(10,2,100)
    _test_ncdf(10,2,1000)
    _test_ncdf(-10,3,100)
    _test_ncdf(-10,3,1000)

def test_cdf_trunc():
    _test_ncdf_trunc(20,3,20,30)
    _test_ncdf_trunc(8,3,0,None)
    _test_ncdf_trunc,(8,3,None,0)


def test_lhs():
    _test_normal_lhs(10,1)
    _test_normal_lhs(1020,50)

def test_ds():
    _test_normal_ds(10,1)
    _test_normal_ds(1020,50)

def test_ds1():
    _test_normal_ds1(10,1)
    _test_normal_ds1(1020,50)

def test_meandev():
    _test_normal_meandev(0, .01)
    _test_normal_meandev(-100, 1)
    _test_normal_meandev(1000000, .000001)

def test_lhs1():
    _test_normal_lhs1(10,1)
    _test_normal_lhs1(1020,50)

def test_random():
    _test_normal_random(5,1)
    _test_normal_random(1e6,300)


if __name__ == "__main__":
    test_pdf()
    test_pdf_trunc()
    test_cdf()
    test_cdf_trunc()
    test_lhs()
    test_lhs1()
    test_ds()
    test_ds1()
    test_meandev()
    test_random()

