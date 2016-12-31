"""
Tests for HPDF function.  Creates PDFs from Histogram data.
"""
from __future__ import absolute_import, division, print_function

import numpy as np
import scipy.stats
import sys, matplotlib
if sys.platform == 'darwin':
    matplotlib.use('macosx', warn=False)
else:
    matplotlib.use('tkagg', warn=False)
import matplotlib.pyplot as plt

from puq import *

global plot_all
plot_all = False


def test_hpdf():
    _test_hpdf(10,2)
    _test_hpdf(-10,2)
    _test_hpdf(0,1)


def _test_hpdf(mean, dev):
    global plot_all
    xrv = scipy.stats.norm(mean, dev)
    range = xrv.ppf([.001, .999])
    x = np.linspace(range[0], range[1], 20)
    xp = xrv.pdf(x)
    data = np.column_stack((x, xp))
    h = HPDF(data)

    x2 = np.linspace(range[0], range[1], options['pdf']['numpart'])
    x2p = xrv.pdf(x2)

    if plot_all:
        plt.figure()
        plt.bar(x, xp, width=x[1]-x[0], alpha=0.4, align='center')
        h.plot(color='red')
        plt.plot(x2, x2p)

    rmse = np.sqrt(np.mean((h.y - x2p)**2))
    rmsep = 100.0 * rmse/(np.max(x2p) - np.min(x2p))
    print("RMSE=%s%%" % rmsep)
    assert rmsep < 3.0

if __name__ == "__main__":
    plot_all = True
    test_hpdf()
    plt.show()
