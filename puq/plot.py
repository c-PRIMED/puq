"""
Plotting functions for UQ

This file is part of PUQ
Copyright (c) 2013 PUQ Authors
See LICENSE file for terms.
"""
from __future__ import absolute_import, division, print_function

from puq.jpickle import unpickle, pickle
import sys, string, matplotlib
if sys.platform == 'darwin':
    matplotlib.use('macosx', warn=False)
else:
    matplotlib.use('tkagg', warn=False)
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
#from matplotlib import rc
#rc('text', usetex=True)
import numpy as np
from .pdf import ExperimentalPDF


def plot_customize(opt, p, fname):
    try:
        if opt.nogrid:
            plt.grid(False)
        else:
            plt.grid(True)
    except:
        pass

    if isinstance(p, Axes3D) and opt.zlabel:
        p.set_zlabel(opt.zlabel)

    if opt.xlabel:
        plt.xlabel(opt.xlabel)

    if opt.ylabel:
        plt.ylabel(opt.ylabel)

    if opt.title:
        plt.title(opt.title)

    if opt.fontsize:
        matplotlib.rcParams.update({'font.size': opt.fontsize})

    if opt.f != 'i':
        plt.savefig('%s.%s' % (fname, opt.f))


def plot(sweep, h5, opt, params=[]):

    if opt.v:
        opt.v = [s.strip() for s in opt.v.split(',')]

    if not opt.l:
        opt.k = True

    method = string.lower(sweep.psweep.__class__.__name__)
    if opt.r:
        for vname in h5[method]:
            if not opt.v or vname in opt.v:
                print("Plotting Response Surface for %s" % vname)
                desc = h5[method][vname].attrs['description']
                rsv = h5[method][vname]['response'].value
                rs = unpickle(rsv)
                p = rs.plot()
                if desc and desc != vname:
                    plt.title(desc)
                else:
                    plt.title("Response Function for %s" % vname)
                plot_customize(opt, p, 'response-%s' % vname)
    else:
        if opt.psamples:
            psamples = get_psamples_from_csv(sweep, h5, opt.samples)
        else:
            psamples = None

        for vname in h5[method]:
            if not opt.v or vname in opt.v:
                print("plotting PDF for %s" % vname)
                desc = h5[method][vname].attrs['description']
                if 'samples' in h5[method][vname]:
                    # response surface already sampled.  Just calculate pdf.
                    data = h5[method][vname]['samples'].value
                    if opt.k:
                        p = ExperimentalPDF(data, fit=True).plot()
                    if opt.l:
                        p = ExperimentalPDF(data, fit=False).plot()
                else:
                    rsv = h5[method][vname]['response'].value
                    rs = unpickle(rsv)
                    data = None
                    if opt.k:
                        pdf, data = rs.pdf(fit=True, params=params, psamples=psamples, return_samples=True)
                        p = pdf.plot()
                    if opt.l:
                        if data is not None:
                            p = ExperimentalPDF(data, fit=False).plot()
                        else:
                            pdf, data = rs.pdf(fit=False, params=params, psamples=psamples, return_samples=True)
                            p = pdf.plot()

                    h5[method][vname]['samples'] = data
                    if 'pdf' not in h5[method][vname]:
                        h5[method][vname]['pdf'] = pickle(pdf)
                plt.xlabel(vname)
                if desc and desc != vname:
                    plt.title("PDF for %s" % desc)
                else:
                    plt.title("PDF for %s" % vname)
                plot_customize(opt, p, 'pdf-%s' % vname)
