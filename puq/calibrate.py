"""
This file is part of PUQ
Copyright (c) 2013 PUQ Authors
See LICENSE file for terms.
"""

import numpy as np
from puq.parameter import NormalParameter
from puq.pdf import PDF

def calibrate(params, caldata, err, func, weight=20):
    """
    Calibrate a variable or variables.

    :param params: Input parameters.
    :type params: List
    :param caldata: Experimental output values.
    :type caldata: Array
    :param err: Deviation representing the measurement error in caldata.
    :type err: Float
    :param func: Response function or simulation.
    :type func: Function
    :returns: A copy of *params* modified with the calibrated variables.
    """
    import pymc
    from copy import copy

    print "Performing Bayesian Calibration..."

    v = {}
    dev = {}
    mean = {}
    expand = False

    # First check to see if any parameters have PDFS or lists of PDFs for data and need expanded
    for p in params:
        if hasattr(p, 'caldata') and (isinstance(p.caldata, list) or isinstance(p.caldata, PDF)):
            expand = True
            caldata = np.repeat(caldata, weight)
            break

    # For each PUQ parameter
    for p in params:
        p.name = str(p.name)
        if hasattr(p, 'caldata') and p.caldata is not None:
            # If calibration data is available, save that for pymc
            if expand:
                if isinstance(p.caldata, list):
                    v[p.name] = np.array([x.ds(weight) for x in p.caldata]).flatten()
                elif isinstance(p.caldata, np.ndarray):
                    v[p.name] = np.repeat(p.caldata, weight)
                elif isinstance(p.caldata, PDF):
                    v[p.name] = np.repeat(p.caldata.ds(len(caldata)/weight), weight)
                else:
                    v[p.name] = p.caldata
            else:
                v[p.name] = p.caldata
        else:
            # For now, we calibrate to a Normal.  Priors for mean and dev are uniform over a large range.
            udev = np.sqrt((p.pdf.range[1] - p.pdf.range[0])**2 / 12.0)
            mean[p.name] = pymc.Uniform(p.name+'_mean', *p.pdf.range, value=(p.pdf.range[0] + p.pdf.range[1])/2.0)
            dev[p.name] = pymc.Uniform(p.name+'_dev', udev/1000.0, udev, value=udev/1000.0)
            # create a stochastic node for pymc with the mean and dev from above and some initial values to try
            v[p.name] = pymc.Normal(p.name,
                                    mu=mean[p.name],
                                    tau=1.0/dev[p.name]**2,
                                    value=np.linspace(p.pdf.range[0], p.pdf.range[1], len(caldata)))

    # Create a node for the model output.  This is deterministic because the model output
    # (from the eval function, which is our response surface evaluation func) returns
    # the same value every time for a given set of input parameters.  The parents are
    # a python dictionary containing name, value pairs where the value is either an
    # array of experimental data or a pymc stochastic node.

    results = pymc.Deterministic(
        eval=func,
        name='results',
        parents=v,
        doc='',
        trace=True,
        verbose=0,
        dtype=float,
        plot=False,
        cache_depth=2)

    # create a node for the experimental output data
    pymc.Normal('exp_out', mu=results, tau=1.0/err**2, value=caldata, observed=True)

    # create the model
    model = pymc.Model(mean.values() + dev.values())

    # use MAP to set a starting points
    map_ = pymc.MAP(model)
    map_.fit()

    # do the MCMC
    mcmc = pymc.MCMC(model)
    #mcmc.use_step_method(pymc.AdaptiveMetropolis, mean.values() + dev.values())
    mcmc.sample(iter=50000, burn=10000, tune_interval=100, tune_throughout=True, progress_bar=True)

    print
    for m in mean.values():
        # FIXME. save trace data instead
        pymc.Matplot.plot(m, verbose=0)
    for d in dev.values():
        # FIXME. save trace data instead
        pymc.Matplot.plot(d, verbose=0)

    newparams = copy(params)
    for i, p in enumerate(newparams):
        if hasattr(p, 'caldata') and p.caldata is not None:
            continue
        m = np.mean(mean[p.name].trace[:])
        d = np.mean(dev[p.name].trace[:])
        print "Calibrated %s to Normal(%s, %s)." % (p.name, m, d)
        newparams[i] = NormalParameter(p.name, p.description, mean=m, dev=d)
        try:
            newparams[i].values = copy(p.values)
        except:
            pass
        newparams[i].original_parameter = p

    return newparams
