"""
.. module:: pdf
    :synopsis: This module implements Probability Density Functions (PDFs)."

.. moduleauthor:: Martin Hunt <mmh@Purdue.edu>

This file is part of PUQ
Copyright (c) 2013 PUQ Authors
See LICENSE file for terms.
"""
from __future__ import absolute_import, division, print_function

import numpy as np
import math
from scipy import trapz, interpolate
import scipy.stats
from puq.options import options
from scipy.stats import gaussian_kde
from logging import info, debug, exception, warning, critical
import sys, matplotlib
if sys.platform == 'darwin':
    matplotlib.use('macosx', warn=False)
else:
    matplotlib.use('tkagg', warn=False)
import matplotlib.pyplot as plt

# Python 3
if sys.version[0] == "3":
    import builtins
else:
    import __builtin__ as builtins

"""
Class implementing a PDF (Probability Density Function).
"""

class PDF(object):
    """
    Create a PDF (Probability Density Function) object.

    Use this to create a PDF object given a list or array
    of x values the corresponding PDF values.

    Args:
      xvals (1D array or list): x values
      yvals (1D array or list): values for PDF(x)
    """

    def __init__(self, xvals, yvals):
        # if order is reversed, flip it
        if xvals[0] > xvals[-1]:
            xvals = xvals[::-1]
            yvals = yvals[::-1]

        # number of intervals to partition our range
        nsamp = options['pdf']['numpart']

        # for pdfs with tails, set the range for sampling
        _range = options['pdf']['range']
        range = [(1.0 - _range)/2.0, (1.0 + _range)/2.0]

        self.x = xvals

        if len(xvals) == 1 or xvals[0] == xvals[-1]:
            self.x = [xvals[0]]
            self.y = [1]
            self.cdfy = [1]
            self.mean = xvals[0]
            self.dev = 0
            return

        self.cdfy = np.append([0.0], np.cumsum((np.diff(yvals)/2.0 + yvals[:-1])*np.diff(xvals)))
        self.cdfy /= self.cdfy[-1]

        # Trim tails that have grown to 10% of the range of the PDF
        resample = False
        mmin, mmax = self.ppf([0, 1])
        dist = mmax - mmin

        if dist == 0.0:
            self.x = [xvals[0]]
            self.y = [1]
            self.cdfy = [1]
            self.mean = xvals[0]
            self.dev = 0
            return

        # print "range of pdf = [%s - %s]" % (mmin, mmax)
        # print "range of PDF = [%s - %s]" % (xvals[0], xvals[-1])
        # print "dist=%s" % (dist)
        # print "proposed range = [%s - %s]" % (self.ppf(range[0]), self.ppf(range[1]))

        if np.isnan(mmin) or abs((mmin - self.ppf(range[0])) / dist) > .1:
            mmin = self.ppf(range[0])
            resample = True
        else:
            mmin = xvals[0]

        if np.isnan(mmax) or abs((mmax - self.ppf(range[1])) / dist) > .1:
            mmax = self.ppf(range[1])
            resample = True
        else:
            mmax = xvals[-1]

        # resample if not even spacing
        if not resample:
            resample = not np.allclose(np.diff(xvals)[0], np.diff(xvals))

        # resample if number of intervals is 10% too large or small
        if not resample:
            resample = np.abs(len(xvals) - nsamp) > (nsamp * .1)

        if resample:
            self.x = np.linspace(mmin, mmax, nsamp)
            self.y = np.interp(self.x, xvals, yvals)
            self.y = np.abs(self.y / trapz(self.y, self.x))
            self.cdfy = np.append([0.0], np.cumsum((np.diff(self.y)/2.0 + self.y[:-1])*np.diff(self.x)))
        else:
            # normalize (integral must be 1.0)
            self.y = yvals / trapz(yvals, self.x)

        self.mean = trapz(self.x * self.y, self.x)
        self.dev = np.sqrt(np.abs(trapz(self.y * (self.x - self.mean)**2, self.x)))

    @property
    def range(self):
        """
        The range for the PDF. For PDFs with long tails,
        it is truncated to 99.99% by default.  You can
        customize this by setting options['pdf']['range'].

        Returns:
          A tuple containing the min and max.
        """
        return (self.x[0], self.x[-1])

    @property
    def srange(self):
        """
        The small range for the PDF. For PDFs with long tails,
        it is truncated to 99.8% by default.  You can
        customize this by setting options['pdf']['srange'].

        Returns:
          A tuple containing the min and max.
        """
        _range = options['pdf']['srange']
        range = [(1.0 - _range)/2.0, (1.0 + _range)/2.0]

        mmin, mmax = self.ppf([0, 1])
        dist = mmax - mmin

        if np.isnan(mmin) or abs((mmin - self.ppf(range[0])) / dist) > .1:
            mmin = self.ppf(range[0])
        else:
            mmin = self.x[0]

        if np.isnan(mmax) or abs((mmax - self.ppf(range[1])) / dist) > .1:
            mmax = self.ppf(range[1])
        else:
            mmax = self.x[-1]

        return (mmin, mmax)

    def _cdf(self, yvals, delta):
        y = (yvals + yvals[0]) / 2.0
        return delta * (yvals.cumsum() - y)

    def pdf(self, arr):
        """
        Computes the Probability Density Function (PDF) for some values.

        Args:
          arr: Array of x values.
        Returns:
          Array of pdf(x).
        """
        return np.interp(arr, self.x, self.y, left=0.0, right=0.0)

    def cdf(self, arr):
        """
        Computes the Cumulative Density Function (CDF) for some values.

        Args:
          arr: Array of x values.
        Returns:
          Array of cdf(x).
        """
        return np.interp(arr, self.x, self.cdfy, left=0.0, right=1.0)

    def ppf(self, arr):
        """
        Percent Point Function (inverse CDF)

        Args:
          arr: Array of x values.
        Returns:
          Array of ppf(x).
        """
        return np.interp(arr, self.cdfy, self.x)

    def lhs1(self, num):
        """
        Latin Hypercube Sample in [-1,1] for this distribution.

        The order of the numbers
        in the array is random, so it can be combined with other arrays
        to form a latin hypercube. Note that this can return values
        outside the range [-1,1] for distributions with long tails.
        This method is used by :mod:`puq.Smolyak`.

        Args:
          num: Number of samples to generate.
        Returns:
          1D array of length *num*.
        """
        pmin, pmax = self.range
        return (2. * self.lhs(num) - (pmax + pmin)) / (pmax - pmin)

    def ds1(self, num):
        '''
        Generates a descriptive sample in [-1,1] for this distribution.

        The order of the numbers
        in the array is random, so it can be combined with other arrays
        to form a latin hypercube. Note that this *can* return values
        outside the range [-1,1] for distributions with long tails.
        This method is used by :mod:`puq.Smolyak`.

        :param num: Number of samples to generate.
        :returns: 1D array of length *num*.
        '''
        pmin, pmax = self.range
        return (2. * self.ds(num) - (pmax + pmin)) / (pmax - pmin)

    def lhs(self, num):
        '''
        Latin Hypercube Sample for this distribution.

        The order of the numbers in the array is random, so it can be
        combined with other arrays to form a latin hypercube.
        This method is used by :class:`LHS`.

        :param num: Number of samples to generate.
        :returns: 1D array of length *num*.
        '''
        return np.random.permutation(self.ppf((np.arange(0, num) + np.random.uniform(0, 1, num))/num))

    def ds(self, num):
        '''
        Generates a descriptive sample for this distribution.

        The order of the numbers
        in the array is random, so it can be combined with other arrays
        to form a latin hypercube.
        This method is used by :class:`LHS`.

        :param num: Number of samples to generate.
        :returns: 1D array of length *num*.
        '''
        return np.random.permutation(self.ppf(np.arange(0.5, num)/num))

    def random(self, num):
        """
        Generate random numbers fitting this parameter's distribution.

        This method is used by :class:`MonteCarlo`.

        :param num: Number of samples to generate.
        :returns: 1D array of length *num*.
        """
        return self.ppf(np.random.uniform(0, 1, num))

    def __neg__(self):
        return PDF(-self.x[::-1], self.y[::-1])

    def __radd__(self, b):
        # print "__radd %s %s" % (self,b)
        return self._nadd(b)

    def _nadd(self, b):
        # print "_nadd %s" % (b)
        # add a scalar to a PDF
        return PDF(b + self.x, self.y)

    def __add__(self, b):
        "Add two PDFs, returning a new one."
        # print "__add__ %s %s" % (self,b)
        if isinstance(b, int) or isinstance(b, float):
            return self._nadd(b)

        if sys.version[0] == "2" and isinstance(b, long):
            return self._nadd(b)

        a = self
        if (a.x[-1] - a.x[0] < b.x[-1] - b.x[0]):
            a, b = b, a

        a0, a1 = a.x[0], a.x[-1]
        b0, b1 = b.x[0], b.x[-1]
        ar = a1 - a0
        br = b1 - b0

        nsamp = options['pdf']['numpart']
        cx = np.linspace(0, ar, nsamp)
        dx = ar/(nsamp-1.0)
        blen = int(math.ceil(br/dx))
        c = np.convolve(a.pdf(cx + a0), b.pdf(cx[:blen] + b0))
        cx = np.linspace(a0 + b0, a1 + b1, num=len(c), endpoint=False)
        return PDF(cx, c)

    def __rsub__(self, b):
        return PDF(b-self.x[::-1], self.y[::-1])

    def __sub__(self, b):
        'Subtract two PDFs, returning a new PDF'
        return self.__add__(-b)

    def __rmul__(self, b):
        return self._nmul(b)

    def _nmul(self, b):
        if b == 0:
            raise ValueError("Multiplying by 0 does not produce a PDF.")
        return PDF(b * self.x, self.y)

    def __mul__(self, b):
        "Multiply two PDFs, returning a new PDF"
        if isinstance(b, int) or isinstance(b, float):
            return self._nmul(b)

        if sys.version[0] == "2" and isinstance(b, long):
            return self._nmul(b)

        a = self
        # if second variable crosses 0, swap the order for best results
        if b.x[0] < 0 and b.x[-1] > 0:
            a, b = b, a
        extremes = np.outer([a.x[0], a.x[-1]], [b.x[0], b.x[-1]])
        zmin, zmax = np.min(extremes), np.max(extremes)
        bx = b.x
        by = b.y.reshape(-1, 1)
        if zmin * zmax <= 0:
            # if the range crosses 0, do not evaluate at 0
            by = by[bx != 0.0]
            bx = bx[bx != 0.0]

        cx = np.linspace(zmin, zmax, options['pdf']['numpart'])
        cy = np.sum(np.abs([a.pdf(cx/x)/x for x in bx]) * by, 0)
        return PDF(cx, cy)

    def _ndiv(self, b):
        if b == 0:
            raise ValueError("Cannot divide a PDF by 0.")
        return PDF(self.x/b, self.y)

    def __rdiv__(self, b):
        if self.x[0]*self.x[-1] <= 0:
            raise ValueError("Cannot divide by PDFs that include 0")
        if b == 0:
            raise ValueError("Dividing 0 by a PDF does not return a PDF")
        extremes = [b/self.x[0], b/self.x[-1]]
        zmin, zmax = np.min(extremes), np.max(extremes)
        nsamp = options['pdf']['numpart']
        cx = np.linspace(zmin, zmax, nsamp)
        return PDF(cx, self.pdf(b/cx)/cx**2)

    def __truediv__(self, b):
        return self.__div__(b)

    def __rtruediv__(self, b):
        return self.__rdiv__(b)

    def __div__(self, b):
        "Divide two PDFs, returning a new PDF"
        if isinstance(b, int) or isinstance(b, float):
            return self._ndiv(b)

        if sys.version[0] == "2" and isinstance(b, long):
            return self._ndiv(b)

        if b.x[0]*b.x[-1] <= 0:
            raise ValueError("Cannot divide by PDFs that include 0")
        a = self
        extremes = np.outer([a.x[0], a.x[-1]], [1.0/b.x[0], 1.0/b.x[-1]])
        zmin, zmax = np.min(extremes), np.max(extremes)
        bx = b.x
        by = b.y.reshape(-1, 1)
        nsamp = options['pdf']['numpart']
        cx = np.linspace(zmin, zmax, nsamp)
        cy = np.sum([a.pdf(x * cx)*x for x in bx] * by, 0)
        return PDF(cx, cy)

    @property
    def mode(self):
        """
        Find the mode of the PDF.  The mode is the x value at which pdf(x)
        is at its maximum.  It is the peak of the PDF.
        """
        if len(self.x) == 1:
            return self.x[0]
        mode = None
        maxy = None
        for x, y in zip(self.x, self.y):
            if mode is None or y > maxy:
                mode = x
                maxy = y
        return mode

    def __str__(self):
        _str = "PDF [%.3g - %.3g] " % (self.x[0], self.x[-1])
        _str += "mean=%.3g  dev=%.3g  mode=%.3g" % (self.mean, self.dev, self.mode)
        return _str

    def plot(self, color='', fig=False):
        """
        Plot a PDF.

        :param color: Optional color for the plot.
        :type color: String.
        :param fig: Create a new matplotlib figure to hold the plot.
        :type fig: Boolean.
        :returns: A list of lines that were added.
        """
        if fig:
            plt.figure()
        if color:
            plt.plot([self.x[0], self.x[0]], [0, self.y[0]], color=color)
            plt.plot([self.x[-1], self.x[-1]], [0, self.y[-1]], color=color)
            return plt.plot(self.x, self.y, color=color)
        else:
            plt.plot([self.x[0], self.x[0]], [0, self.y[0]], color='g')
            plt.plot([self.x[-1], self.x[-1]], [0, self.y[-1]], color='g')
            return plt.plot(self.x, self.y, color='g')

    # ipython pretty print method
    def _repr_pretty_(self, p, cycle):
        if cycle:
            return
        self.plot()
        p.text(self.__str__())


def _get_range(sfunc, min, max):
    " Truncate PDFs with long tails"

    num_tails = int(sfunc.ppf(0) == np.NINF) + int(sfunc.ppf(1) == np.PINF)

    _range = options['pdf']['range']
    if num_tails:
        if num_tails == 2:
            range = [(1.0 - _range)/2, (1.0 + _range)/2]
        else:
            range = [1.0 - _range, _range]

    mmin = sfunc.ppf(0)
    if mmin == np.NINF:
        mmin = sfunc.ppf(range[0])
    mmax = sfunc.ppf(1)
    if mmax == np.PINF:
        mmax = sfunc.ppf(range[1])

    if min is not None:
        min = builtins.max(min, mmin)
    else:
        min = mmin

    if max is not None:
        max = builtins.min(max, mmax)
    else:
        max = mmax

    return min, max


def ExponPDF(rate):
    """
    Creates Exponential Probability Density Function.

    :param rate: The rate parameter for the distribution. Must be > 0.
    :returns: A PDF object

    See http://en.wikipedia.org/wiki/Exponential_distribution
    """
    if rate <= 0:
        raise ValueError("Rate must be greater than 0.")

    sfunc = scipy.stats.expon(loc=0, scale=1.0/rate)

    nsamp = options['pdf']['numpart']
    min, max = _get_range(sfunc, None, None)
    x = np.linspace(min, max, nsamp)
    return PDF(x, sfunc.pdf(x))


def RayleighPDF(scale):
    """
    Creates Rayleigh Probability Density Function.

    :param scale: The scale. Must be > 0.
    :returns: A PDF object

    See http://en.wikipedia.org/wiki/Rayleigh_distribution
    """

    if scale <= 0:
        raise ValueError("Scale must be greater than 0.")

    sfunc = scipy.stats.rayleigh(loc=0, scale=scale)

    nsamp = options['pdf']['numpart']
    min, max = _get_range(sfunc, None, None)
    x = np.linspace(min, max, nsamp)
    return PDF(x, sfunc.pdf(x))


def WeibullPDF(shape, scale):
    """
    Creates Weibull Probability Density Function.

    :param shape: The shape. Must be > 0.
    :param scale: The scale. Must be > 0.
    :returns: A PDF object

    See http://en.wikipedia.org/wiki/Weibull_distribution
    """

    if shape <= 0 or scale <= 0:
        raise ValueError("Shape and Scale must be greater than 0.")

    sfunc = scipy.stats.exponweib(1, shape, scale=scale)

    nsamp = options['pdf']['numpart']
    mmin = None
    if sfunc.pdf(0) == np.PINF:
        mmin = .01
    min, max = _get_range(sfunc, mmin, None)
    x = np.linspace(min, max, nsamp)
    return PDF(x, sfunc.pdf(x))


def NormalPDF(mean, dev, min=None, max=None):
    """
    Creates a normal (gaussian) Probability Density Function.

    :param mean: The mean.
    :param dev: The standard deviation.
    :param min: A minimum value for the PDF (default None).
    :param max: A maximum value for the PDF (default None).
    :returns: A PDF object

    For the normal distribution, you must specify **mean** and **dev**.

    :Example:

    >>> n = NormalPDF(10,1)
    >>> n = NormalPDF(mean=10, dev=1)
    >>> n = NormalPDF(mean=10, dev=1, min=10)
    """

    if dev <= 0:
        raise ValueError("Deviation must be positive.")
    sfunc = scipy.stats.norm(loc=mean, scale=dev)
    min, max = _get_range(sfunc, min, max)
    dev = float(dev)
    a = (min - mean) / dev
    b = (max - mean) / dev
    sfunc = scipy.stats.truncnorm(a, b, loc=mean, scale=dev)
    nsamp = options['pdf']['numpart']
    x = np.linspace(min, max, nsamp)
    return PDF(x, sfunc.pdf(x))


def NetPDF(addr):
    """
    Retrieves a PDF from a remote address.

    :param addr: URI. PDF must be stored in JSON format
    :returns: A PDF object

    :Example:

    >>> u = NetPDF('http://foo.com/myproject/parameters/density')
    """
    from jpickle import NetObj
    p = NetObj(addr)
    if not isinstance(p, PDF):
        raise Exception('Link is not a PDF')
    return p


def UniformPDF(min=None, max=None, mean=None):
    """
    Creates a uniform Probability Density Function.

    :param min: The minimum value
    :param max: The maximum value
    :param mean: The mean value
    :returns: A PDF object

    For the uniform distribution, you must specify two of (min, max, and mean).
    The third parameter will be calculated automatically.

    :Example:

    >>> u = UniformPDF(10,20)
    >>> u = UniformPDF(min=10, max=20)
    >>> u = UniformPDF(min=10, mean=15)
    """

    def usage(match=0):
        if match:
            raise ValueError("mean must be (min+max)/2. Try specifying just min and max.")
        raise ValueError("For uniform distribution, you must specify two of (min, max, and mean).")

    if min is not None and max is not None and mean is not None:
        # check agreement
        if not np.allclose(mean, (min + max)/2.0, atol=1e-6):
            usage(1)

    if mean is None:
        if max is None or min is None:
            usage()
        mean = (max + min) / 2.0
    if max is None:
        if mean is None or min is None:
            usage()
        max = mean + (mean - min)
    if min is None:
        min = mean - (max - mean)
    if min > max:
        raise ValueError("min must not be > mean or max!")

    return PDF([min, max], [1, 1])


def TrianglePDF(min, mode, max):
    """
    Creates a triangle Probability Density Function.

    See http://en.wikipedia.org/wiki/Triangular_distribution

    :param min: The minimum value
    :param mode: The mode
    :param max: The maximum value
    :returns: A PDF object

    You can enter the parameters in any order. They will be sorted so that the mode
    is the middle value.
    """
    min, mode, max = np.sort([min, mode, max])
    return PDF([min, mode, max], [0, 1, 0])


def JeffreysPDF(min, max):
    # untested
    min = float(min)
    max = float(max)
    return PDF([min, max], [1.0 / (min * np.log(max/min)), 1.0 / (max * np.log(max/min))])


def ExperimentalPDF(data, min=None, max=None, fit=False, bw=None, nbins=0, prior=None, error=None, force=False):
    """
    Create an experimental PDF.

    An experimental PDF is derived from the results of an experiment or
    measurement of some parameter.  It has actual data attached to it.
    That data is then used to create a PDF by one of three different methods.

    The PDF can built by binning the data and linearly
    interpolating, using a Gaussian KDE, or using Bayesian Inference.

    :param data: Our quantity of interest.
    :type data: Array of scalars
    :param nbins:  Number of bins (used if fit is false).  Default is
                 2*IQR/n^(1/3) where IQR is the interquartile range
                 of the data.
    :type nbins: int
    :param fit: Use Gaussian KDE (default=False)
    :type fit: True or "Gaussian"
    :param bw: Bandwidth for Gaussian KDE (default=None)
    :type bw: string or float. String must be 'scott' or 'silverman'
    :param prior: Prior PDF to use for Bayesian Inference.
        [default=None (uninformative)]
    :type prior: PDF
    :param error: Error in the data.  For example, the measurement error.
        Required for Bayesian.
    :type error: PDF. Typically a NormalPDF with a mean of 0.
    """
    data = np.array(data).astype(np.float64)
    if not force and min is not None and min > np.min(data):
        raise ValueError('min cannot be set to more than minimum value in the data.')
    if not force and max is not None and max < np.max(data):
        raise ValueError('max cannot be set to less than maximum value in the data.')
    if nbins and nbins <= 1:
        raise ValueError("ERROR: invalid number of bins: %s" % nbins)

    # constant
    if np.min(data) == np.max(data) and not error:
        p = PDF([np.min(data)], [1])
        p.data = data
        return p

    if len(data) < 1 or (len(data) == 1 and not error):
        raise ValueError("ERROR: need at least two data points to build a PDF, or a prior and 1 data point.")

    if error:
        # Bayesian parameter estimation
        if not isinstance(error, PDF):
            raise ValueError("ERROR: error is not a PDF")
        data = data + error
        p = posterior(data, prior)
    elif fit is True or (type(fit) is str and fit.lower() == 'gaussian'):
        # Gaussian KDE
        if np.min(data) == np.max(data):
            raise ValueError("Cannot generate PDF fron non-variable data.")
        gkde = gaussian_kde(data, bw_method=bw)
        dev = np.std(data)
        mean = np.mean(data)
        if min is None:
            min = mean - 5 * dev
        if max is None:
            max = mean + 5 * dev
        x = np.linspace(float(min), float(max), options['pdf']['numpart'])
        p = PDF(x, gkde.evaluate(x))
    else:
        # linear interpolation from histograms
        if nbins == 0:
            iqr = scipy.stats.scoreatpercentile(data, 75) - scipy.stats.scoreatpercentile(data, 25)
            if iqr == 0.0:
                # constant
                p = PDF([np.min(data)], [1])
                p.data = data
                return p
            nbins = int((np.max(data) - np.min(data)) / (2*iqr/len(data)**(1.0/3)) + .5)

        y, bins = np.histogram(data, nbins, normed=True)
        if len(bins) > 2:
            x = bins[:-1] + np.diff(bins) / 2.0
            sp = interpolate.splrep(x, y, s=0, k=1)
            mmin = bins[0]
            mmax = bins[-1]
            if min is not None:
                mmin = min
            if max is not None:
                mmax = max
            x = np.linspace(float(mmin), float(mmax), options['pdf']['numpart'])
            y = interpolate.splev(x, sp, der=0)
            if np.isnan(np.sum(y)):
                # interpolate failed. constant pdf
                p = PDF([np.min(data)], [1])
                p.data = [data[0]]
                return p
            y[y < 0] = 0    # if the extrapolation goes negative...
            p = PDF(x, y)
        else:
            # not enough data. assume uniform over range
            p = PDF([np.min(data), np.max(data)], [1, 1])
    p.data = data
    return p


def HPDF(data, min=None, max=None):
    """
    Histogram PDF - initialized with points from a histogram.

    This function creates a PDF from a histogram.  This is useful when some other software has
    generated a PDF from your data.

    :param data: A two dimensional array. The first column is the histogram interval mean,
        and the second column is the probability.  The probability values do not need to be
        normalized.
    :param min: A minimum value for the PDF range. If your histogram has values very close
        to 0, and you know values of 0 are impossible, then you should set the ***min*** parameter.
    :param max: A maximum value for the PDF range.
    :type data: 2D numpy array
    :returns: A PDF object.
    """
    x = data[:, 0]
    y = data[:, 1]
    sp = interpolate.splrep(x, y)
    dx = (x[1] - x[0]) / 2.0
    mmin = x[0] - dx
    mmax = x[-1] + dx
    if min is not None:
        mmin = builtins.max(min, mmin)
    if max is not None:
        mmax = builtins.min(max, mmax)
    x = np.linspace(mmin, mmax, options['pdf']['numpart'])
    y = interpolate.splev(x, sp)
    y[y < 0] = 0     # if the extrapolation goes negative...
    return PDF(x, y)


def posterior(data, prior=None):
    """
    Computes posterior PDF.

    :param data:    A PDF or list or array of PDFs.
    :param prior:  If no prior is specified, a noninformative prior is used.
    :returns:    A posterior PDF object.

    """
    if prior:
        if not isinstance(prior, PDF):
            raise ValueError("ERROR: prior is not a PDF")
        data = np.append(data, prior)
    else:
        data = np.array(data)

    # The X range needs to be constrained to where all
    # the input PDFS are defined.

    rmin = max([c.x[0] for c in data])
    rmax = min([c.x[-1] for c in data])
    x = np.linspace(rmin, rmax, options['pdf']['numpart'])
    y = np.prod([c.pdf(x) for c in data], 0)
    return PDF(x, y)
