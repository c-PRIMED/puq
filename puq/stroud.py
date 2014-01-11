#!/usr/bin/env python

from numpy import *

""" @package stroud
Finds Stroud quadrature points.

This file is part of PUQ
Copyright (c) 2013 PUQ Authors
See LICENSE file for terms.
"""

def Stroud_Ck(n, m):
    """
    This routine returns the Stroud quadrature points for Cn, n-cube.
    Such quadratures are exact for n-dimensional multiple integral
    in [-1,1]^n with polynomial integrants of degree up to P^m.

    Syntax:  [z,w] = Stroud_Ck( n, m )

    Input :  n, dimensionality of the space;
    m, polynomial exactness.

    Only m = 2 and 3 are defined, with number of points n+1 (m=2)
    and 2*n (m=3).

    Return: z = [npt, n] are the n-dim coordinates for npt points;
    w = [npt, 1] are the weights.
    For m=2,3, weights are equal, i.e. w=Volume/npt=2^n/npt.

    Original matlab version written and tested by Dongbin Xiu, 12/22/2003.

    Python version by Martin Hunt. Python uses 0-based arrays, so
    \f$x_i^{(2r-1)} = \sqrt{\frac{2}{3}}\cos{(\frac{2r(i-1)\pi}{n+1})}\f$
    for i = 1 to n+1 and r = 1 to rr becomes

    \f$x_i^{2r} = \sqrt{\frac{2}{3}}\cos{(\frac{2(r+1)i\pi}{n+1})}\f$
    for i = 0 to n and r = 0 to (rr-1)

    @param n dimensionality of the space;
    @param m polynomial exactness.
    """

    if m == 2:
        npt = n + 1
        z = zeros((npt, n))
        w = 2. ** n / npt * ones((npt, 1));
        rr = int(n / 2)
        for i in range(0, n + 1):
            for r in range(0, rr):
                z[i, 2 * r] = sqrt(2. / 3) * cos(2 * (r + 1) * i * pi / (n + 1))
                z[i, 2 * r + 1] = sqrt(2. / 3) * sin(2 * (r + 1) * i * pi / (n + 1))
            if n % 2 == 1:
                z[i, n - 1] = (-1) ** i / sqrt(3)
    elif (m == 3):
        npt = n * 2
        z = zeros((npt, n))
        w = 2. ** n / npt * ones((npt, 1));
        rr = int(n / 2)
        for i in range(0, npt):
            for r in range(0, rr):
                z[i, 2 * r] = sqrt(2. / 3) * cos((2 * (r + 1) - 1) * (i + 1) * pi / n)
                z[i, 2 * r + 1] = sqrt(2. / 3) * sin((2 * (r + 1) - 1) * (i + 1) * pi / n)
            if n % 2 == 1:
                z[i, n - 1] = (-1) ** i / sqrt(3)

    else:
        print 'Stroud_Ck: polymonials of degree %s not supported.\n' % m

    return z, w

## @cond
if __name__ == "__main__":
    print "Enter the dimensionality (n):",
    n = input()
    print "Enter the polynominal degree (m):",
    m = input()
    points, weights = Stroud_Ck(n, m)
    print "Points ="
    for p in points:
        for v in p:
            print "%9.5f" % v,
        print

    print "Weights =", weights
## @endcond
