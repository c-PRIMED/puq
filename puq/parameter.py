'''
The parameter module implements the different parameter types and
their PDFs.

This file is part of PUQ
Copyright (c) 2013 PUQ Authors
See LICENSE file for terms.
'''
from puq.pdf import NormalPDF, UniformPDF, ExperimentalPDF, WeibullPDF, RayleighPDF, ExponPDF, PDF
from logging import debug
import sys, matplotlib, sympy
if sys.platform == 'darwin':
    matplotlib.use('macosx', warn=False)
else:
    matplotlib.use('tkagg', warn=False)
import matplotlib.pyplot as plt
import numpy as np

# return an array of parameter samples
def get_psamples(params, psamples=None, num=None):
    xseed = None

    use_samples = False
    for p in params:
        if hasattr(p, 'use_samples') and p.use_samples:
            use_len = len(p.pdf.data)
            use_samples = True
            break

    if use_samples and psamples is not None:
        raise ValueError("Can't use both samples from a CVS file and from PDFs.")

    if psamples:
        num_samples = len(psamples[psamples.keys()[0]])
    elif use_samples:
        num_samples = use_len
    elif num is not None:
        num_samples = num
    else:
        num_samples = 10000

    if xseed is None and not hasattr(p,'pdf'):
        return None

    for p in params:
        if hasattr(p, 'use_samples') and p.use_samples:
            if xseed is None:
                xseed = p.pdf.data.reshape(-1, 1)
            else:
                xseed = np.column_stack((xseed, p.pdf.data))
        elif psamples and p.name in psamples:
            print 'Using CSV data for %s' % p.name
            if xseed is None:
                xseed = psamples[p.name].reshape(-1, 1)
            else:
                xseed = np.column_stack((xseed, psamples[p.name]))
        else:
            if xseed is None:
                xseed = p.pdf.ds(num_samples).reshape(-1, 1)
            else:
                xseed = np.column_stack((xseed, p.pdf.ds(num_samples)))
    return xseed

class Parameter(object):
    '''
    Superclass for all Parameter subclasses. For backwards compatibility it
    can be called directly and will return the proper subclass.

    :class:`NormalParameter` is returned if 'dev' is set.
    :class:`UniformParameter` is returned if either 'min' or 'max' is set.
    :class:`CustomParameter` is returned if 'pdf' or 'caldata' is set.

    - *name* : Name of the parameter. This should be a short name, like a variable.
    - *description* :  A longer description of the parameter.
    - *kargs* : Keyword args defined by the distribution.

    .. seealso::
       :class:`NormalParameter`, :class:`UniformParameter`, :class:`CustomParameter`
    '''

    def __new__(cls, *args, **kw):
        if cls.__name__ != 'Parameter':
            debug('Parameter cls=%s' % cls)
            return object.__new__(eval(cls.__name__))
        debug('Parameter: cls=%s kwargs=%s' % (cls, kw))
        if 'dev' in kw:
            klass = NormalParameter
        elif 'values' in kw:
            klass = DParameter
        elif 'min' in kw or 'max' in kw:
            klass = UniformParameter
        elif 'pdf' in kw or 'caldata' in kw:
            klass = CustomParameter
        else:
            raise Exception('Unable to determine PDF type')
        return klass.__new__(klass, *args, **kw)

    def __init__(self, *args, **kargs):
        debug(args)

    def check_name(self, name):
        try:
            e = sympy.S(name)
            assert str(e.evalf()) == name
            return name
        except:
            pass
        print "Parameter name %s conflicts with internal variables.\nPlease use a different name." % name
        sys.exit(0)

    def plot(self, **kwargs):
        self.pdf.plot(kwargs)
        plt.xlabel(self.name)
        if self.description and self.description != self.name:
            plt.title('%s (%s)' % (self.name, self.description))
        else:
            plt.title('%s' % self.name)

    # ipython pretty print method
    def _repr_pretty_(self, p, cycle):
        if cycle:
            return
        self.plot()
        p.text(self.pdf.__str__())

class DParameter(Parameter):
    '''
    Class implementing a Discrete Parameter which contains values from a list or array.

    - *name* : Name of the parameter. This should be a short name, like a variable.
    - *description* :  A longer description of the parameter.
    - *values* :   A 1D list or array of values for the parameter.
    '''
    def __init__(self, name, description, values=None):
        self.name = self.check_name(name)
        self.description = description
        if values is None:
            self.values = None
        else:
            self.values = np.array(values)

    # This is what you see when the object is printed
    def __str__(self):
        return "DParameter %s (%s)\n\tvalues=%s" % (self.name, self.description, self.values)

class NormalParameter(Parameter):
    '''
    Class implementing a Parameter with a Normal distribution.

    - *name* : Name of the parameter. This should be a short name, like a variable.
    - *description* :  A longer description of the parameter.
    - *args* : Keyword args.  Valid args are:

    ======== ============================
    Arg      Description
    ======== ============================
    mean     The mean of the distribution
    dev      The standard deviation
    ======== ============================

    '''
    def __init__(self, name, description, **args):
        debug("name:%s desc:%s args:%s" % (name, description, args))
        self.name = self.check_name(name)
        self.description = description
        self.caldata = args.pop('caldata', None)
        self.pdf = NormalPDF(**args)

    # This is what you see when the object is printed
    def __str__(self):
        return "NormalParameter %s (%s)\n\t%s" % (self.name, self.description, self.pdf.__str__())

class RayleighParameter(Parameter):
    '''
    Class implementing a Parameter with a Rayleigh distribution.

    - *name* : Name of the parameter. This should be a short name, like a variable.
    - *description* :  A longer description of the parameter.
    - *args* : Keyword args.  Valid args are:

    ======== ============================
    Arg      Description
    ======== ============================
    scale    The scale. Must be > 0.
    ======== ============================

    .. seealso::
       :class:`RayleighPDF`
    '''
    def __init__(self, name, description, **args):
        debug("name:%s desc:%s args:%s" % (name, description, args))
        self.name = self.check_name(name)
        self.description = description
        self.caldata = args.pop('caldata', None)
        self.pdf = RayleighPDF(**args)

    # This is what you see when the object is printed
    def __str__(self):
        return "RayleighParameter %s (%s)\n\t%s" % (self.name, self.description, self.pdf.__str__())

class ExponParameter(Parameter):
    '''
    Class implementing a Parameter with an Exponential distribution.

    - *name* : Name of the parameter. This should be a short name, like a variable.
    - *description* :  A longer description of the parameter.
    - *args* : Keyword args.  Valid args are:

    ======== =================================
    Arg      Description
    ======== =================================
    rate     The rate parameter. Must be > 0.
    ======== =================================

    .. seealso::
       :class:`ExponPDF`
    '''
    def __init__(self, name, description, **args):
        debug("name:%s desc:%s args:%s" % (name, description, args))
        self.name = self.check_name(name)
        self.description = description
        self.caldata = args.pop('caldata', None)
        self.pdf = ExponPDF(**args)

    # This is what you see when the object is printed
    def __str__(self):
        return "ExponParameter %s (%s)\n\t%s" % (self.name, self.description, self.pdf.__str__())

class WeibullParameter(Parameter):
    '''
    Class implementing a Parameter with a Weibull distribution.

    - *name* : Name of the parameter. This should be a short name, like a variable.
    - *description* :  A longer description of the parameter.
    - *args* : Keyword args.  Valid args are:

    ======== ============================
    Arg      Description
    ======== ============================
    shape    The shape. Must be > 0.
    scale    The scale. Must be > 0.
    ======== ============================

    .. seealso::
       :class:`WeibullPDF`
    '''
    def __init__(self, name, description, **args):
        debug("name:%s desc:%s args:%s" % (name, description, args))
        self.name = self.check_name(name)
        self.description = description
        self.caldata = args.pop('caldata', None)
        self.pdf = WeibullPDF(**args)

    # This is what you see when the object is printed
    def __str__(self):
        return "WeibullParameter %s (%s)\n\t%s" % (self.name, self.description, self.pdf.__str__())


class CustomParameter(Parameter):
    '''
    Class implementing a Parameter with a Custom distribution.

    - *name* : Name of the parameter. This should be a short name, like a variable.
    - *description* :  A longer description of the parameter.
    - *args* : Keyword args.  Valid args are:

    ============ ===============================================
    Arg          Description
    ============ ===============================================
    pdf          :class:`puq.PDF`
    use_samples  Use data samples attached to pdf (if available)
    ============ ===============================================
    '''
    def __init__(self, name, description, **args):
        #Parameter.__init__(self, args)
        self.name = self.check_name(name)
        self.description = description
        self.use_samples = args.get('use_samples')
        self.pdf = args.get('pdf')
        self.caldata = args.get('caldata')

        if self.pdf is None and self.caldata is None:
            self.usage(0)

        if self.pdf is not None and (isinstance(self.caldata, list) or isinstance(self.caldata, PDF)):
            self.usage(1)

        # If calibration data was supplied and nothing else, fit it to a PDF.
        if self.caldata is not None and self.pdf is None:
            self.pdf = self.caldata

        if self.caldata is not None:
            if isinstance(self.caldata, list):
                # A list of PDFs.  Sample from all of them to produce a PDF
                d = np.array([x.ds(200) for x in self.caldata]).flatten()
                self.pdf = ExperimentalPDF(fit=1, data=d)
            elif isinstance(self.caldata, PDF):
                self.pdf = self.caldata

        # if pdf was an array or list of PDFs, fix it
        if isinstance(self.pdf, np.ndarray):
            self.pdf = ExperimentalPDF(self.pdf, fit=1)
        elif isinstance(self.pdf, list):
            # A list of PDFs.  Sample from all of them to produce a PDF
            d = np.array([x.ds(200) for x in self.pdf]).flatten()
            self.pdf = ExperimentalPDF(fit=1, data=d)

    def usage(self, msg):
        if msg == 0:
            raise ValueError("Error: You must specify a pdf, data, or caldata.")
        elif msg == 1:
            raise ValueError("Error: You specified a pdf and caldata consisting of a PDF or list of PDFs.")

    # This is what you see when the object is printed
    def __str__(self):
        return "CustomParameter %s (%s)\n%s" %\
            (self.name, self.description, self.pdf.__str__())

class UniformParameter(Parameter):
    '''
    Class implementing a Parameter with a Uniform distribution.

    - *name* : Name of the parameter. This should be a short name, like a variable.
    - *description* :  A longer description of the parameter.
    - *args* : Keyword args.  Valid args are:

    ======== ============================
    Property Description
    ======== ============================
    mean     The mean of the distribution
    max      The maximum
    min      The minimum
    ======== ============================

    You **must** specify two of the above properties. If you
    give all three, they will be checked for consistency.
    :math:`mean = (min + max)/2`
    '''
    def __init__(self, name, description, **args):
        self.name = self.check_name(name)
        self.description = description
        self.caldata = args.pop('caldata', None)
        self.pdf = UniformPDF(**args)

    def __str__(self):
        return "UniformParameter %s (%s)\n\t%s" %\
            (self.name, self.description, self.pdf.__str__())
