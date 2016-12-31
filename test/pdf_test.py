#!/usr/bin/env python
"""
unit tests for basic math operations on PDFs.
"""
#from __future__ import absolute_import, division, print_function

from puq import *
import numpy as np
import sys, matplotlib, time
import scipy.stats
if sys.platform == 'darwin':
    matplotlib.use('macosx', warn=False)
else:
    matplotlib.use('tkagg', warn=False)
import matplotlib.pyplot as plt
np.set_printoptions(threshold=np.nan)
global plot_errors
plot_errors = False

"""
We need to test PDFs with different overlapping
of endpoints, as well as their location relative to
the Y axis.

Below, a and b are endpoints of first PDF
c and d are endpoints of second PDF
Y is location of Y axis
so ['a','c','d','bY'] would look like this:

* = (a,b)
@ = (c,d)
                                   |
          **********************   |
         *                      *  |
        *      @@@@@@@@@@        * |
       *      @          @        *|
------*------@------------@--------*--------
"""

all_pts = [
    # a,b,c,d
    ['a','b','c','d','Y'],
    ['a','b','c','Y','d'],
    ['a','b','Y','c','d'],
    ['a','Y','b','c','d'],
    ['Y','a','b','c','d'],
    # a,c,b,d
    ['a','c','b','d','Y'],
    ['a','c','b','Y','d'],
    ['a','c','Y','b','d'],
    ['a','Y','c','b','d'],
    ['Y','a','c','b','d'],
    # a,c,d,b
    ['a','c','d','b','Y'],
    ['a','c','d','Y','b'],
    ['a','c','Y','d','b'],
    ['a','Y','c','d','b'],
    ['Y','a','c','d','b'],
    # aY
    ['aY','b','c','d'],
    ['aY','c','b','d'],
    ['aY','c','d','b'],
    # bY
    ['a','bY','c','d'],
    ['a','c', 'bY','d'],
    ['a','c','d','bY'],
    # cY
    ['a','b','cY','d'],
    ['a','cY','b','d'],
    ['a','cY','d','b'],
    # dY
    ['a','b','c','dY'],
    ['a','c','b','dY'],
    ['a','c','dY','b'],
    # acY
    ['acY','b','d'],
    # bdY
    ['a','c','bdY'],
    # ac
    ['ac','b','d','Y'],
    ['ac','b','Y','d'],
    ['ac','Y','b','d'],
    ['Y','ac','b','d'],
    # bd
    ['a','c','bd','Y'],
    ['a','c','Y','bd'],
    ['a','Y','c','bd'],
    ['Y','a','c','bd'],
    ]

def get_locs(pts):
    for i, p in enumerate(pts):
        if 'Y' in p:
            yloc = i
            break
    for i, p in enumerate(pts):
        for v in ['a', 'b', 'c', 'd']:
            if v in p:
                if v == 'a':
                    a = (i-yloc) * 10
                elif v == 'b':
                    b = (i-yloc) * 10
                elif v == 'c':
                    c = (i-yloc) * 10
                elif v == 'd':
                    d = (i-yloc) * 10
    return a, b, c, d


def memoize(f):
    cache = {}
    def g(*args, **kwargs):
        key = (f, tuple(args), frozenset(kwargs.items()))
        if key not in cache:
            cache[key] = f(*args, **kwargs)
        return cache[key]
    return g

@memoize
def mc_tri_dist(a, b, nsamp, flip=False):
    if flip:
        return scipy.stats.triang(0.8, loc=a, scale=b-a).rvs(size=nsamp)
    return scipy.stats.triang(0.2, loc=a, scale=b-a).rvs(size=nsamp)

@memoize
def tri_dist(a, b, flip=False):
    if flip:
        return TrianglePDF(min=a, max=b, mode=a + 0.8*(b-a))
    return TrianglePDF(min=a, max=b, mode=a + 0.2*(b-a))

def compare_pdfs(a, b):
    global max_rmse
    rmin = min(a.range[0], b.range[0])
    rmax = max(a.range[1], b.range[1])
    nsamp = 10
    cx = np.linspace(rmin, rmax, nsamp)
    ar = a.pdf(cx)
    br = b.pdf(cx)
    w = np.ones(cx.shape)
    for i, val in enumerate(cx):
        if np.abs(val) < 1:
            w[i] = np.abs(val)
    rmse = np.sqrt(np.mean(w*(ar - br)**2))
    rmsep = 100.0 * rmse/(np.max(ar) - np.min(ar))
    max_rmse = max(max_rmse, rmsep)
    return rmsep

def _do_test(op, p, swap=False, flip=False):
    global ttime, plotall, tops, rmse_limit, plot_errors
    nsamp = 1000000
    if swap:
        c,d,a,b = get_locs(p)
    else:
        a,b,c,d = get_locs(p)

    p1 = tri_dist(a,b)
    p2 = tri_dist(c,d, flip)
    mc1 = mc_tri_dist(a,b,nsamp)
    mc2 = mc_tri_dist(c,d,nsamp, flip)

    if op == '*':
        starttime = time.time()
        dd = p1 * p2
        ttime += time.time() - starttime
        mcd = mc1 * mc2
        tops += 1
    elif op == '/':
        # check if range crosses zero
        if p2.range[0] * p2.range[1] > 0:
            starttime = time.time()
            dd = p1 / p2
            ttime += time.time() - starttime
            mcd = mc1 / mc2
            tops += 1
        else:
            dd = None
    elif op == '+':
        starttime = time.time()
        dd = p1 + p2
        ttime += time.time() - starttime
        mcd = mc1 + mc2
        tops += 1
    elif op == '-':
        starttime = time.time()
        dd = p1 - p2
        ttime += time.time() - starttime
        mcd = mc1 - mc2
        tops += 1

    if not dd:
        return

    mcd = ExperimentalPDF(data=mcd,nbins=100)
    rmse = compare_pdfs(dd, mcd)

    if not plot_errors:
        assert rmse <= rmse_limit, "rmse %s limit %s" % (rmse, rmse_limit)

    if np.isnan(rmse) or rmse > rmse_limit or plotall:
        print("(a=%s b=%s) %s (c=%s d=%s)" % (a,b,op,c,d))
        print("RMSE=",rmse)
        mcd.plot(color='red')
        dd.plot()
        plt.show()

def __do_testn(op, p, n, swap=False):
    global ttime, plotall, tops, rmse_limit, plot_errors
    # print("do_testn(%s, %s, %s, %s" % (op, p, n, swap))
    nsamp = 1000000
    a,b = p
    p1 = tri_dist(a,b)
    mc1 = mc_tri_dist(a,b,nsamp)
    if op == '*':
        try:
            starttime = time.time()
            if swap:
                dd = p1 * n
            else:
                dd = n * p1
            ttime += time.time() - starttime
            mcd = n * mc1
            tops += 1
        except ValueError:
            dd = None
    elif op == '/':
        try:
            starttime = time.time()
            if swap:
                dd = p1 / n
                ttime += time.time() - starttime
                mcd = mc1 / n
            else:
                dd = n / p1
                ttime += time.time() - starttime
                mcd = n / mc1
            tops += 1
        except ValueError:
            dd = None
    elif op == '+':
        starttime = time.time()
        if swap:
            dd = p1 + n
        else:
            dd = n + p1
        ttime += time.time() - starttime
        mcd = mc1 + n
        tops += 1
    elif op == '-':
        starttime = time.time()
        if swap:
            dd = p1 - n
            ttime += time.time() - starttime
            mcd = mc1 - n
        else:
            dd = n - p1
            ttime += time.time() - starttime
            mcd = n - mc1
        tops += 1

    if not dd:
        return

    mcd = ExperimentalPDF(data=mcd,nbins=100)
    rmse = compare_pdfs(dd, mcd)

    if not plot_errors:
        assert rmse <= rmse_limit

    if np.isnan(rmse) or rmse > rmse_limit or plotall:
        if swap:
            print("(a=%s b=%s) %s %s" % (a,b,op,n))
        else:
            print("%s %s (a=%s b=%s)" % (n, op, a,b))
        print("RMSE=",rmse)
        mcd.plot(color='red')
        dd.plot()
        plt.show()


def test_scalar_add():
    global ttime, plotall, max_rmse, tops, rmse_limit
    plotall = 0
    ttime = 0.0
    max_rmse=0.0
    rmse_limit = 1.0
    tops = 0

    __do_testn('+', (10,20), 5)
    __do_testn('+', (10,20), 5, True)
    __do_testn('+', (10,20), 0)
    __do_testn('+', (10,20), 0, True)
    __do_testn('+', (-20,-10), 5)
    __do_testn('+', (-20,-10), 5, True)
    __do_testn('+', (10,20), -5)
    __do_testn('+', (10,20), -5, True)
    __do_testn('+', (-10,10), 5)
    __do_testn('+', (-10,10), 5, True)
    __do_testn('+', (10,20), 5.5)
    __do_testn('+', (10,20), 5.5, True)
    __do_testn('+', (10,20.5), 5)
    print('MAX RMSE = %s%%' % max_rmse)
    print("Total Time = %s" % ttime)
    print("%.2f ms per scalar addition\n" % ((ttime * 1000.0) / tops))

def test_scalar_subtract():
    global ttime, plotall, max_rmse, tops, rmse_limit
    plotall = 0
    ttime = 0.0
    max_rmse=0.0
    rmse_limit = 1.0
    tops = 0

    __do_testn('-', (10,20), 5)
    __do_testn('-', (10,20), 5, True)
    __do_testn('-', (10,20), 0)
    __do_testn('-', (10,20), 0, True)
    __do_testn('-', (-20,-10), 5)
    __do_testn('-', (-20,-10), 5, True)
    __do_testn('-', (10,20), -5)
    __do_testn('-', (10,20), -5, True)
    __do_testn('-', (-10,10), 5)
    __do_testn('-', (-10,10), 5, True)
    __do_testn('-', (10,20), 5.5)
    __do_testn('-', (10,20), 5.5, True)
    __do_testn('-', (10,20.5), 5)
    print('MAX RMSE = %s%%' % max_rmse)
    print("Total Time = %s" % ttime)
    print("%.2f ms per scalar subtraction\n" % ((ttime * 1000.0) / tops))

def test_scalar_divide():
    global ttime, plotall, max_rmse, tops, rmse_limit
    plotall = 0
    ttime = 0.0
    max_rmse=0.0
    rmse_limit = 1.0
    tops = 0

    __do_testn('/', (10,20), 5)
    __do_testn('/', (10,20), 5, True)
    __do_testn('/', (10,20), 0)
    __do_testn('/', (10,20), 0, True)
    __do_testn('/', (-20,-10), 5)
    __do_testn('/', (-20,-10), 5, True)
    __do_testn('/', (10,20), -5)
    __do_testn('/', (10,20), -5, True)
    __do_testn('/', (-10,10), 5)
    __do_testn('/', (-10,10), 5, True)
    __do_testn('/', (10,20), 5.5)
    __do_testn('/', (10,20), 5.5, True)
    __do_testn('/', (10,20.5), 5)
    print('MAX RMSE = %s%%' % max_rmse)
    print("Total Time = %s" % ttime)
    print("%.2f ms per scalar division\n" % ((ttime * 1000.0) / tops))

def test_scalar_multiply():
    global ttime, plotall, max_rmse, tops, rmse_limit
    plotall = 0
    ttime = 0.0
    max_rmse=0.0
    rmse_limit = 1.0
    tops = 0

    __do_testn('*', (10,20), 5)
    __do_testn('*', (10,20), 5, True)
    __do_testn('*', (10,20), 0)
    __do_testn('*', (10,20), 0, True)
    __do_testn('*', (-20,-10), 5)
    __do_testn('*', (-20,-10), 5, True)
    __do_testn('*', (10,20), -5)
    __do_testn('*', (10,20), -5, True)
    __do_testn('*', (-10,10), 5)
    __do_testn('*', (-10,10), 5, True)
    __do_testn('*', (10,20), 5.5)
    __do_testn('*', (10,20), 5.5, True)
    __do_testn('*', (10,20.5), 5)
    print('MAX RMSE = %s%%' % max_rmse)
    print("Total Time = %s" % ttime)
    print("%.2f ms per scalar multiplication\n" % ((ttime * 1000.0) / tops))

def test_add():
    global ttime, plotall, max_rmse, tops, rmse_limit
    plotall = 0
    ttime = 0.0
    max_rmse=0.0
    rmse_limit = 1.0
    tops = 0
    for p in all_pts:
        _do_test('+', p)
        _do_test('+', p, True)
        _do_test('+', p, False, True)
        _do_test('+', p, True, True)
    print('MAX RMSE = %s%%' % max_rmse)
    print("Total Time = %s" % ttime)
    print("%.2f ms per addition\n" % ((ttime * 1000.0) / tops))

def test_subtract():
    global ttime, plotall, max_rmse, tops, rmse_limit
    plotall = 0
    ttime = 0.0
    max_rmse=0.0
    rmse_limit = 1.2
    tops = 0
    for p in all_pts:
        _do_test('-', p)
        _do_test('-', p, True)
        _do_test('-', p, False, True)
        _do_test('-', p, True, True)
    print('MAX RMSE = %s%%' % max_rmse)
    print("Total Time = %s" % ttime)
    print("%.2f ms per subtraction\n" % ((ttime * 1000.0) / tops))

def test_multiply():
    global ttime, plotall, max_rmse, tops, rmse_limit
    plotall = 0
    ttime = 0.0
    max_rmse=0.0
    rmse_limit = 5.5
    tops = 0
    for p in all_pts:
        _do_test('*', p)
        _do_test('*', p, True)
        _do_test('*', p, False, True)
        _do_test('*', p, True, True)
    print('MAX RMSE = %s%%' % max_rmse)
    print("Total Time = %s" % ttime)
    print("%.2f ms per multiplication\n" % ((ttime * 1000.0) / tops))

def test_divide():
    global ttime, plotall, max_rmse, tops, rmse_limit
    plotall = 0
    ttime = 0.0
    max_rmse=0.0
    rmse_limit = 1.0
    tops = 0
    for p in all_pts:
        _do_test('/', p)
        _do_test('/', p, True)
        _do_test('/', p, False, True)
        _do_test('/', p, True, True)
    print('MAX RMSE = %s%%' % max_rmse)
    print("Total Time = %s" % ttime)
    print("%.2f ms per division\n" % ((ttime * 1000.0) / tops))

if __name__ == "__main__":
    plot_errors = True
    test_scalar_add()
    test_scalar_subtract()
    test_scalar_divide()
    test_scalar_multiply()
    test_add()
    test_subtract()
    test_multiply()
    test_divide()
