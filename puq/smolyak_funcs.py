from numpy import *
from scipy.special import jacobi, gamma, legendre

"""@package smolyak_funcs
Functions for Smolyak UQ method
"""

def memoize(f, cache={}):
    def g(*args, **kwargs):
        key = ( f, tuple(args), frozenset(kwargs.items()) )
        if key not in cache:
            cache[key] = f(*args, **kwargs)
        return cache[key]
    return g

def factorial(k):
    return reduce(int.__mul__, xrange(1, k + 1), 1)

def nelms(n, m):
    return factorial(n + m) / factorial(m) / factorial(n)

def index_step1(m):
    rows, cols = m.shape
    out = None
    for row in m:
        for i in range(0, cols):
            z = row.copy()
            z[i] += 1
            if out == None:
                out = array([z])
            else:
                copy = True
                for r in out:
                    if all(r == z):
                        copy = False
                        break
                if copy:
                    out = vstack((out, z))
    return out

def index_step(p, n):
    p1 = index_step1(p)
    pn = vstack((p, p1))
    for i in range(1, n):
        ptmp = p1
        p1 = index_step1(ptmp)
        pn = vstack((pn, p1))
    return pn

@memoize
def chaos_sequence(ndim, p):
    assert ndim > 0
    return index_step(zeros((1, ndim)), p);

@memoize
def _legendre(n):
    return legendre(n)

def legendre_nd(x, ndim, norder):
    ntmp = len(x)
    assert(ntmp == ndim)

    pmatrix = chaos_sequence(ndim, norder)
    ptmp = zeros((norder + 1, ndim))

    for n in range(0, norder + 1):
        ptmp[n, :] = _legendre(n)(x)

    nterm, ntmp = pmatrix.shape
    poly = ones((nterm))

    for m in range(1, nterm):
        for n in range(0, ndim):
            poly[m] *=  ptmp[pmatrix[m, n], n]
    return poly


def jacobi_e2_1d(order, alpha, beta):
    """
    jacobi_e2_1d.m - Evaluate the inner product of 1d Jacobi-chaos doubles

    Syntax     e = jacobi_e2_1d(order, alpha, beta)

    Input:     order = order of Jacobi-chaos
                alpha, beta = parameters of Jacobi-chaos (alpha, beta>-1)
    Output:    e = 1 x (p+1) row vector containing the result.

    NO WARNING MESSAGE IS GIVEN WHEN PARAMETERS ARE OUT OF RANGE.

    Original Matlab version by Dongbin Xiu   04/13/2003
    """

    e = zeros((order + 1, 1))
    np = ceil((2.0 * order + 1.0) / 2.0)

    j = jacobi(np, alpha, beta).weights
    z = j[:, 0]
    w = j[:, 1]

    factor = 2 ** (alpha + beta + 1) * gamma(alpha + 1) * gamma(beta + 1) / gamma(alpha + beta + 2)

    for i in range(0, order + 1):
        e[i] = sum(jacobi(i, alpha, beta)(z) ** 2 * w) / factor
    return e


def jacobi_e2_nd(ndim, p, alpha, beta):
    """
    jacobi_e2_nd.m - Evaluate the inner product of n-dimensional
                    Jacobi-chaos, i.e. int J^2 dx

    Syntax     e = jacobi_e2_nd( ndim, p, alpha, beta)

    Input:     ndim = dimensionality of the Jacobi-chaos
            p    = order of the Jacobi-chaos
            alpha, beta = parameters of Jacobi-chaos (alpha, beta>-1)
    Output:    e = 1xP (P=(ndim+p)!/(ndim!p!)) array containing the result.

    NO WARNING MESSAGE IS GIVEN WHEN PAPAMETERS ARE OUT OF RANGE.

    Original Matlab version by Dongbin Xiu   11/09/2005
    """

    assert (ndim > 0)
    if ndim == 1:
        e = jacobi_e2_1d(p, alpha, beta)
    else:
        e1 = jacobi_e2_1d(p, alpha, beta)
        poly = chaos_sequence(ndim, p)
        P = poly.shape[0]
        e = ones((P, 1))
        for m in range(0, P):
            for n in range(0, ndim):
                e[m] = e[m] * e1[poly[m, n]]
    return e

# TESTING STUFF STARTS BELOW
values = [(jacobi_e2_1d, (3, 1.5, 0), array([[1.0], [0.55555556], [0.38461538], [0.29411765]])),
          (jacobi_e2_1d, (1, 1, 0), array([[1.0], [0.5]])),
          (jacobi_e2_1d, (1, 0, 0), array([[1.0], [0.33333333]])),
          (jacobi_e2_1d, (2, 0, 0), array([[1.0], [0.33333333], [0.2]])),
          (jacobi_e2_1d, (3, 0, 0), array([[1.0], [0.33333333], [0.2], [0.14285714]])),
          (jacobi_e2_nd, (1, 2, 0, 0), array([[1.0], [0.33333333], [0.2]])),
          (jacobi_e2_nd, (2, 1, 0, 0), array([[1.0], [0.33333333], [0.33333333]])),
          (jacobi_e2_nd, (3, 2, 0, 0), array([[1.0], [0.33333333], [0.33333333], [0.33333333], [0.2], [0.11111111], [0.11111111], [0.2], [0.11111111], [0.2]])),
          (legendre_nd, (array([0, 0.70711]), 2, 2), array([1.0, 0.0, 0.70711, -0.5, 0.0, 0.25000683])),
          (chaos_sequence, (1, 1), array([[0], [1]])),
          (chaos_sequence, (2, 1), array([[0, 0], [1, 0], [0, 1]])),
          (chaos_sequence, (2, 2), array([[0, 0], [1, 0], [0, 1], [2, 0], [1, 1], [0, 2]])),
          (chaos_sequence, (3, 2), array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [2, 0, 0], [1, 1, 0], [1, 0, 1], [0, 2, 0], [0, 1, 1], [0, 0, 2]])),
          ]

# nosetests requires this simplistic approach to generate decent xml test names
def test_jacobi_e2_1d_0():
    func, args, expected = values[0]
    do_tst(func, args, expected)
def test_jacobi_e2_1d_1():
    func, args, expected = values[1]
    do_tst(func, args, expected)
def test_jacobi_e2_1d_2():
    func, args, expected = values[2]
    do_tst(func, args, expected)
def test_jacobi_e2_1d_3():
    func, args, expected = values[3]
    do_tst(func, args, expected)
def test_jacobi_e2_1d_4():
    func, args, expected = values[4]
    do_tst(func, args, expected)
def test_jacobi_e2_nd_0():
    func, args, expected = values[5]
    do_tst(func, args, expected)
def test_jacobi_e2_nd_1():
    func, args, expected = values[6]
    do_tst(func, args, expected)
def test_jacobi_e2_nd_2():
    func, args, expected = values[7]
    do_tst(func, args, expected)
def test_legendre_nd():
    func, args, expected = values[8]
    do_tst(func, args, expected)
def test_chaos_sequence_0():
    func, args, expected = values[9]
    do_tst(func, args, expected)
def test_chaos_sequence_1():
    func, args, expected = values[10]
    do_tst(func, args, expected)
def test_chaos_sequence_2():
    func, args, expected = values[11]
    do_tst(func, args, expected)
def test_chaos_sequence_3():
    func, args, expected = values[12]
    do_tst(func, args, expected)



def do_tst(f, args, res):
    tmp = apply(f, args)
    #print tmp
    assert allclose(tmp, res)

