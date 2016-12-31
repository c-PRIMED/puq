from numpy import *
from scipy.special import jacobi, gamma, legendre
from math import factorial

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

def nelms(n, m):
    return int(factorial(n + m) / factorial(m) / factorial(n))

def index_step1(m):
    rows, cols = m.shape
    out = None
    for row in m:
        for i in range(0, cols):
            z = row.copy()
            z[i] += 1
            if out is None:
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
    return index_step(zeros((1, ndim), int), p);

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
