"""
This file is part of PUQ
Copyright (c) 2013-2016 PUQ Authors
See LICENSE file for terms.
"""
from __future__ import absolute_import, division, print_function

import sys
import numpy as np
import sympy
from scipy.interpolate import Rbf
from puq.meshgridn import meshgridn
from puq.pdf import ExperimentalPDF
from puq.parameter import get_psamples
from sympy.utilities.lambdify import lambdify

import matplotlib
if sys.platform == 'darwin':
    matplotlib.use('macosx', warn=False)
else:
    matplotlib.use('tkagg', warn=False)
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.pyplot as plt


class Function(object):
    """
    Superclass for ResponseFunc and SampledFunc
    """

    def evala(self, p):
        return self.eval(*p.T)

    # find min and max output of a response
    def minmax(self):
        import heapq
        from scipy.optimize import fmin_l_bfgs_b
        dims = len(self.vars)
        if dims < 3:
            steps = 20
        elif dims < 5:
            steps = 10
        else:
            steps = 3

        d = []
        for v in self.vars:
            d.append(np.linspace(*v[1], num=steps))

        xx = meshgridn(*d)
        pts = np.vstack(list(map(np.ndarray.flatten, xx))).T
        res = self.evala(pts)
        if type(res) is not np.ndarray:
            return res, res

        h = []
        for i, p in enumerate(pts):
            if isinstance(p, np.ndarray):
                p = p.tolist()
            heapq.heappush(h, (res[i], p))

        bounds = [x[1] for x in self.vars]

        minval = float('inf')
        for p in heapq.nsmallest(5, h):
            pt, v, d = fmin_l_bfgs_b(self.evala, p[1], approx_grad=True, bounds=bounds)
            if d['warnflag'] == 0 and v < minval:
                minval = v

        maxval = float('inf')
        for p in heapq.nlargest(5, h):
            pt, v, d = fmin_l_bfgs_b(lambda x: -self.evala(x), p[1], approx_grad=True, bounds=bounds)
            if d['warnflag'] == 0 and v < maxval:
                maxval = v

        maxval = -maxval
        return minval, maxval

    def check_pdf_range(self, a, b):
        if b.pdf.range[0] < b.pdf.range[0] or b.pdf.range[1] > a.pdf.range[1]:
            try:
                if sys.stdin.isatty() and sys.stdout.isatty():
                    print('New PDF has a range outside the original PDF.')
                    loop = True
                    x = 'N'
                    while loop:
                        x = raw_input("Proceed anyway? (Y/N)")
                        if x in ['Y', 'N']: loop = False
                    if x == 'Y': return
            except:
                pass
            raise ValueError('New PDF has a range outside the original PDF')

    def pdf(self, fit=True, params=[], force=False, min=None, max=None,
            return_samples=False, psamples=None):

        if not self.params and not params:
            raise ValueError("Cannot generate PDF for response function without params.")

        if params:
            saved_params = self.params
            saved_vars = self.vars

            for newp in params:
                for i, p in enumerate(self.params):
                    if p.name == newp.name:
                        print("REPLACING\n\t%s\nWITH\n\t%s\n" % (p, newp))
                        if not force:
                            self.check_pdf_range(p, newp)
                        self.params[i] = newp
            self.vars = self.params2vars(self.params)

        # get parameter pdf samples
        if psamples is None:
            xseed = get_psamples(self.params)
        else:
            xseed = psamples

        results = self.evala(xseed)

        # If the response surface is constant, 'results' is a constant.
        # We will need to return an appropriate array filled with it.
        if type(results) != np.ndarray:
            val = results
            results = np.empty(xseed.shape[0])
            results.fill(val)

        if min is None:
            min = np.min(results)

        if max is None:
            max = np.max(results)

        if params:
            self.params = saved_params
            self.vars = saved_vars

        if return_samples:
            return ExperimentalPDF(results, fit=fit, min=min, max=max, force=force), results
        else:
            return ExperimentalPDF(results, fit=fit, min=min, max=max, force=force)

    def params2vars(self, params):
        if not params:
            raise ValueError("Need vars or params.")
        self.params = params
        return [(p.name, (p.pdf.range[0], p.pdf.range[1])) for p in params]

    def plot(self, *args, **kwargs):
        dims = len(self.vars)
        if dims > 2:
            print("Warning: Cannot plot in more than 3 dimensions!")
            return
        if dims == 1:
            return self._plot1(*args, **kwargs)
        elif dims == 2:
            return self._plot2(*args, **kwargs)

    def _plot2(self, steps=40, legend=True, title=True, labels=True, **kwargs):
        # 2 dimensions plus result on Z-axis = 3D plot
        x = np.linspace(*self.vars[0][1], num=steps+1)
        y = np.linspace(*self.vars[1][1], num=steps+1)
        xx = meshgridn(x, y)
        pts = np.vstack(list(map(np.ndarray.flatten, xx))).T
        pts = np.array(self.evala(pts))

        fig = kwargs.get('fig')
        if fig is None:
            fig = plt.figure()

        ax = kwargs.get('ax')
        if ax is None:
            ax = Axes3D(fig, azim=30, elev=30)

        X, Y = xx
        Z = pts.reshape(X.shape)
        surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet, alpha=0.7, linewidth=0)

        # legend
        if legend:
            fig.colorbar(surf, shrink=0.5)

        # titles
        xlab = self.vars[0][0]
        ylab = self.vars[1][0]
        if self.params:
            if xlab != self.params[0].description:
                xlab = "%s (%s)" % (xlab, self.params[0].description)
            if ylab != self.params[1].description:
                ylab = "%s (%s)" % (ylab, self.params[1].description)
        if labels:
            plt.xlabel(xlab)
            plt.ylabel(ylab)
        if title:
            plt.title('Response Plot')
        return ax

    def _plot1(self, steps=100, labels=True, **kwargs):
        fig = kwargs.get('fig')
        if fig is None:
            fig = plt.figure()

        # 1 dimension
        x = np.linspace(*self.vars[0][1], num=steps+1)
        y = self.eval(x)
        p = plt.plot(x, y)
        xlab = self.vars[0][0]
        if self.params:
            if xlab != self.params[0].description:
                xlab = "%s (%s)" % (xlab, self.params[0].description)
        if labels:
            plt.xlabel(xlab)
        # some matplotlibs have broken limits when scatterplots and
        # line plots are mixed
        plt.xlim(np.min(x) - .02*np.min(x), np.max(x) + .02*np.max(x))
        return p


class ResponseFunc(Function):
    """
    Args:
      eqn(string): An equation for the response function.
      params(list): Input parameters.
      vars(list): An list of variables and their ranges.
        Example [(var, (min, max)), ...]
      data(array): Actual data points used to compute the
        response surface. (optional) Used to compute the
        quality of fit (RMSE). First column is first variable
        or parameter, etc. Last column is the result.
    """
    def __init__(self, eqn, **kwargs):
        if not eqn:
            raise ValueError("Need eqn.")
        vars = kwargs.get('vars')
        if vars:
            self.params = None
        else:
            vars = self.params2vars(kwargs.get('params'))
        self.data = kwargs.get('data')
        vnames = []
        for x, y in vars:
            vnames.append(str(x))

        self._eqn = sympy.S(eqn)
        self.vars = vars
        self.vnames = vnames
        self._reinit_()

    def _reinit_(self):
        self.vnames = list(map(str, self.vnames))
        v = sympy.symbols(self.vnames)
        self.eval = lambdify(v, self._eqn, dummify=False)

    @property
    def eqn(self):
        return self._eqn

    @eqn.setter
    def eqn(self, value):
        self._eqn = value
        v = sympy.symbols(self.vnames)
        self.eval = lambdify(v, self._eqn, dummify=False)

    def _plot1(self, *args, **kwargs):
        p = Function._plot1(self, *args, **kwargs)
        plt.title('Response Plot')
        if self.data is not None:
            # scatter plot actual data
            plt.scatter(self.data[:, 0], self.data[:, 1], color='black')
        return p

    def _plot2(self, *args, **kwargs):
        ax = Function._plot2(self, *args, **kwargs)
        if self.data is not None:
            # scatter plot actual data
            ax.scatter(self.data[:, 0], self.data[:, 1], self.data[:, 2], color='black')
        return ax

    def simplify(self, sig=1e-6, debug=False):
        """
        Simplify a polynomial response function by removing less significant terms.
        This returns a new copy of the response function and does not update the
        original one.

        Args:
          sig(float): Significance.  Default is 1.0e-6.
        Returns:
          New response equation.

        .. note::
            May reduce accuracy of response surface.  Use
            with care.
        """
        import itertools
        if not self.eqn.is_polynomial():
            return self.eqn
        ranges = [y for _x, y in self.vars]
        terms = []
        if not isinstance(self.eqn, sympy.Add):
            return self.eqn
        for term in self.eqn.args:
            mabs = 0
            for p in itertools.product(*ranges):
                res = abs(term.subs(zip(self.vnames, p)))
                if res > mabs:
                    mabs = res
            if debug:
                print("%s\t has maximum of %s" % (term, mabs))
            terms.append((term, mabs))
        maxval = max([val for _t, val in terms])
        eqn = sympy.Add(*[t for t, val in terms if val/maxval > sig])
        return sympy.simplify(eqn)

    def trunc(self, digits=6):
        """
        Truncates coefficients of the response equation to a certain number of digits.
        This returns a new copy of the response function and does not update the
        original one.

        Args:
          digits: How many significant digits to keep.
          Default is 6.

        Returns:
          New response equation.

        .. note::
            May reduce accuracy of response surface.  Use with care.
        """
        if not isinstance(self._eqn, sympy.Add):
            return self._eqn
        print([t.as_coeff_Mul() for t in self._eqn.args])
        print([(t.as_coeff_Mul()[0].evalf(digits), t.as_coeff_Mul()[1]) for t in self._eqn.args])
        return sympy.Add(*[sympy.Mul(t.as_coeff_Mul()[0].evalf(digits), t.as_coeff_Mul()[1]) for t in self._eqn.args])

    def rmse(self):
        """
        Calculates the Root Mean Square Error (or Deviation),
        and the Normalized RMSE expressed as a percent.
        A good fit will have an RMSE Percentage near 0%
        """

        if self.data is None:
            return None

        # actual results
        results = self.data[:, -1]

        # rs will contain the results calculated from the response function
        rs = self.evala(self.data[:, :-1])
        rmse = np.sqrt(np.mean((results - rs)**2))
        if np.max(results) == np.min(results):
            rmsep = 100.0*rmse
        else:
            rmsep = 100.0*rmse/(np.max(results) - np.min(results))
        return rmse, rmsep

    def to_sampled(self):
        """
        Returns a new SampledFunc() from the ResponseFunc(), if possible.
        """
        if self.data is None:
            raise ValueError("Data must be included in the ResponseFunc() to convert it to a SampledFunc()")
        if self.params is None:
            sf = SampledFunc(*[d for d in self.data.T], vars=self.vars)
        else:
            sf = SampledFunc(*[d for d in self.data.T], params=self.params)
        sf.eqn = self.eqn
        return sf


class SampledFunc(Function):
    def __init__(self, *pts, **kwargs):
        if pts is None or len(pts) == 0:
            raise ValueError("Need points.")
        self.pts = pts
        vars = kwargs.get('vars')
        if vars:
            self.params = None
        else:
            vars = self.params2vars(kwargs.get('params'))
        self.vars = vars
        self.rbfunc = kwargs.get('rbf', 'multiquadric')
        self.eps = kwargs.get('eps')
        self._reinit_()
        self.eps = self._interp_func.epsilon

    def _plot1(self, *args, **kwargs):
        p = Function._plot1(self, *args, **kwargs)
        plt.title('Response Plot')
        plt.scatter(*self.pts, color='black')
        return p

    def _plot2(self, *args, **kwargs):
        ax = Function._plot2(self, *args, **kwargs)
        plt.title('Response Plot')
        ax.scatter(*self.pts, color='black')
        return ax

    def _reinit_(self):
        # print "REINIT SampledFunc", type(self.pts) is np.ndarray
        self.rbfunc = str(self.rbfunc)

        # backwards compatability Mar 2013.
        if type(self.pts) is np.ndarray:
            self.pts = [x for x in self.pts.T]

        if self.eps is None:
            self._interp_func = Rbf(*self.pts, function=self.rbfunc)
        else:
            self._interp_func = Rbf(*self.pts, function=self.rbfunc, epsilon=self.eps)

    def get_epsilon(self):
        return self.eps

    def set_epsilon(self, eps):
        # print "Setting epsilon to %s" % eps
        self.eps = eps
        self._reinit_()
    epsilon = property(get_epsilon, set_epsilon, None, None)

    def get_rbf(self):
        return self.rbfunc

    def set_rbf(self, rbf):
        # print "Setting rbf to %s" % rbf
        self.rbfunc = rbf
        self._reinit_()
    rbf = property(get_rbf, set_rbf, None, None)

    # Evaluate a SampledFunc at certain points using Radial Basis Functions
    def eval(self, *pts, **kwargs):
        if kwargs:
            pts = [kwargs[x[0]] for x in self.vars]
        pts = np.broadcast_arrays(*pts)
        return self._interp_func(*pts)

    def to_response(self):
        """
        Returns a new ResponseFunc() from the SampledFunc(), if possible.
        """
        if self.eqn is None:
            raise ValueError("Equation required to convert it to a ResponseFunc()")

        if self.params is None:
            rf = ResponseFunc(self.eqn, vars=self.vars, data=np.column_stack((self.pts)))
        else:
            rf = ResponseFunc(self.eqn, params=self.params, data=np.column_stack((self.pts)))
        return rf
