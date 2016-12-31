"""
Smolyak Sparse Grid based on Clenshaw-Curtis

This file is part of PUQ
Copyright (c) 2013 PUQ Authors
See LICENSE file for terms.
"""
from __future__ import absolute_import, division, print_function

import numpy as np
from puq.smolyak_funcs import legendre_nd, jacobi_e2_nd, nelms, chaos_sequence
from puq.util import process_data, vprint
from puq.psweep import PSweep
from puq.jpickle import pickle
from puq.sparse_grid import sgrid
from collections import defaultdict
from logging import debug
from .response import ResponseFunc


class Smolyak(PSweep):
    """
    Class implementing gPC using Smolyak Sparse Grids

    Args:
      params: Input list of :class:`Parameter`\s.
      level: Polynomial degree for the response function.

    If *level* is set too low, then the response surface
    will not precisely fit the observed responses. The goodness
    of the fit is calculated as by RMSE. A perfect fit will have RMSE=0.
    """

    def __init__(self, params, level, iteration_cb=None):
        PSweep.__init__(self, iteration_cb)
        self.params = params
        self.level = int(level)
        self._calculate_params()

    def _calculate_params(self):
        # self.grid is the original smolyak grid
        self.grid = sgrid(len(self.params), self.level)

        # pgrid is the scaled grid.
        # used for generating parameter values
        self.pgrid = self.grid.copy()

        for i, p in enumerate(self.params):
            pmin, pmax = p.pdf.srange
            self.pgrid[:, i] *= (pmax - pmin) / 2.0
            self.pgrid[:, i] += (pmax + pmin) / 2.0
            p.values = self.pgrid[:, i]

    def extend(self, num=None):
        self.level += 1
        vprint(1, "Extending Smolyak to level %d" % self.level)
        oldsize = self.grid.shape[0]
        self._calculate_params()
        self.pgrid = self.pgrid[oldsize:]

    # Returns a list of name,value tuples
    # For example, [('t', 1.0), ('freq', 133862.0)]
    def get_args(self):
        for row in self.pgrid:
            yield zip([p.name for p in self.params], row[:-1])

    def _do_rs(self, hf, data):
        rs = self._uhat(data)
        sens = self.sensitivity(data)
        return [('response', pickle(rs)), ('sensitivity', sens)]

    def analyze(self, hf):
        debug('')
        process_data(hf, 'smolyak', self._do_rs)

    def polyrs(self, uhat):
        "Compute the polynomial for the response surface."
        import sympy

        dim = len(self.params)
        var = []
        for i, p in enumerate(self.params):
            var.append(sympy.Symbol(str(p.name)))

        chaos = chaos_sequence(dim, self.level)
        chaos = np.int_(chaos)
        for d in range(0, dim):
            poly = np.array(list(map(lambda x: sympy.legendre(int(x), var[d]), chaos[:, d])))
            if d == 0:
                s = poly
            else:
                s *= poly

        eqn = np.sum(uhat * s)
        for i, p in enumerate(self.params):
            pmin, pmax = p.pdf.srange
            c = (pmax + pmin) / 2.0
            s = (pmax - pmin) / 2.0
            eqn = eqn.subs(var[i], (var[i] - c)/s)
        return sympy.sstr(eqn.expand().evalf())

    def _uhat(self, results):
        nc = len(self.grid[:, 0])
        ndim = len(self.params)
        level = self.level
        x = self.grid
        weight = x[:, ndim]
        weight = weight / np.sum(weight)
        x = x[:, 0:ndim]
        nterm = nelms(self.level, ndim)
        jf = np.zeros((nc, nterm))
        h2 = jacobi_e2_nd(ndim, self.level, 0, 0)
        for i in range(0, nc):
            jf[i, :] = legendre_nd(x[i, :], ndim, level)

        # calculate uhat
        uhat = np.zeros((nterm))
        for i in range(0, nterm):
            uhat[i] = np.sum(results.T * jf[:, i] * weight) / h2[i]

        poly = self.polyrs(uhat)

        # collect parameters and results in one array
        pgrid = self.grid.copy()
        for i, p in enumerate(self.params):
            pmin, pmax = p.pdf.srange
            pgrid[:, i] *= (pmax - pmin) / 2.0
            pgrid[:, i] += (pmax + pmin) / 2.0
        actual_data = np.column_stack((pgrid[:, :-1], results))
        rs = ResponseFunc(poly, params=self.params, data=actual_data)
        vprint(1, "\tSurface   = %s" % rs.eqn)
        srmse, srmsep = rs.rmse()
        vprint(1, "\tRMSE      = %.2e (%.2e %%)" % (srmse, srmsep))
        return rs

    def sensitivity(self, data):
        """
        Elementary Effects Screening
        see http://en.wikipedia.org/wiki/Elementary_effects_method
        """

        vprint(1, "\nSENSITIVITY:")
        ee = {}

        # strip out weight column and rescale to [0,1]
        grid = (self.grid[:, :-1] + 1) / 2
        vgrid = np.column_stack((grid, data))

        numcols = grid.shape[1]

        # Each parameter's value is in a column, so for each
        # column, create a new grid without that column, then look for
        # duplicate rows.
        for coln in range(0, numcols):
            ee[coln] = []
            newgrid = grid[:, [x for x in range(0, numcols) if x != coln]]
            # (alternative) newgrid = np.delete(grid, coln, axis=1)
            rowlist = defaultdict(list)
            for n, row in enumerate(newgrid):
                rowlist[tuple(row)].append(n)
            for r in list(rowlist.keys()):
                if len(rowlist[r]) < 2:
                    del rowlist[r]

            # For each list of duplicate rows, create an array with all the
            # parameter values and the output value.  Iterate through it to
            for r in rowlist:
                rdata = None
                for rr in rowlist[r]:
                    if rdata is None:
                        rdata = vgrid[rr]
                    else:
                        rdata = np.vstack((rdata, vgrid[rr]))
                rdata = rdata[rdata[:, coln].argsort()]
                Y = None
                for d in rdata:
                    if Y is not None:
                        ee[coln] = np.append(ee[coln], (d[-1] - Y) / (d[coln] - X))
                        #print (d[-1] - Y) / (d[coln] - X)
                    Y = d[-1]
                    X = d[coln]

        max_name_len = max(map(len, [p.name for p in self.params]))
        sens = {}
        for n, p in enumerate(self.params):
            std = np.std(ee[n])
            ustar = np.mean(np.abs(ee[n]))
            sens[p.name] = {'std': std, 'ustar': ustar}
            #p.sensitivity_ustar = ustar
            #p.sensitivity_dev = std
        sorted_list = sorted(list(sens.items()), key=lambda a: a[1]['ustar'], reverse=True)

        vprint(1, "Var%s     u*            dev" % (' '*(max_name_len)))
        vprint(1, '-'*(28+max_name_len))
        for item in sorted_list:
            pad = ' '*(max_name_len - len(item[0]))
            vprint(1, "%s%s    %.4e    %.4e" % (pad, item[0], item[1]['ustar'], item[1]['std']))
        return pickle(sorted_list)
