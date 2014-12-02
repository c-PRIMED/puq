"""
This file is part of PUQ
Copyright (c) 2013-2104 PUQ Authors
See LICENSE file for terms.
"""

import puq
import numpy as np
import copy


def PymcPDFNode(name, pdf):
    import pymc

    def logp(value):
        p = pdf.pdf(value)
        if p <= 0:
            return -np.inf
        return np.log(p)

    def random():
        return pdf.random(1)[0]

    value = (pdf.x[0] + pdf.x[-1])/2.0

    return pymc.Stochastic(
        logp=logp,
        doc='Custom Pymc PDF Node',
        name=name,
        parents={},
        random=random,
        trace=True,
        value=value,
        dtype=type(value),
        observed=False,
        cache_depth=2,
        plot=True,
        verbose=0)


def calibrate(params, caldata, err, func, num_samples=100000):
    """
    Performs Bayesian calibration for a variable or variables.

    Args:
      params (list): Input parameters. Parameters which have caldata
      included are not calibrated. Parameters without caldata must
      have a caltype. See XXX.

      caldata (list or array): Experimental output values.

      err (float or array of floats): Standard deviation of the measurement
          error in **caldata**.  If this is a scalar, then use the same error
          for every data point.

      func: Response function.

    Returns:
      A copy of **params** modified with the calibrated variables.
    """
    import pymc
    print "Performing Bayesian Calibration..."

    v = {}
    means = {}
    devs = {}
    dlen = caldata.shape[0]

    num_burn = num_samples / 5
    num_thin = num_samples / 10000

    # For each PUQ parameter
    for p in params:
        p.name = str(p.name)
        if hasattr(p, 'caldata') and p.caldata is not None:
            # noncalibration parameter with measurements and errors
            v[p.name] = p.caldata
        else:
            if p.caltype == 'S' or p.caltype is None:
                means[p.name] = PymcPDFNode(p.name + '_mean', p.pdf)

                def logp(value):
                    if value <= 0:
                        return -np.inf
                    return -np.log(value)

                devs[p.name] = pymc.Stochastic(
                    name=p.name + '_dev',
                    logp=logp,
                    doc='',
                    parents={},
                    value=p.pdf.dev)
                values = np.linspace(p.pdf.x[0], p.pdf.x[-1], dlen)
                v[p.name] = pymc.Normal(
                    p.name,
                    mu=means[p.name],
                    tau=1.0 / devs[p.name] ** 2,
                    value=values)
            elif p.caltype == 'D':
                v[p.name] = PymcPDFNode(p.name + '_mean', p.pdf)
            else:
                msg = "Calibration type of '%s' undefined. Must be 'S' or 'D'" % p.caltype
                raise ValueError(msg)


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
    model = pymc.Model(v)

    # use MAP to set starting points
    map_ = pymc.MAP(model)
    map_.fit()

    # do the MCMC
    mcmc = pymc.MCMC(model)
    #mcmc.use_step_method(pymc.AdaptiveMetropolis, mean.values() + dev.values())
    mcmc.sample(iter=num_samples, burn=num_burn, thin=num_thin, tune_interval=100, tune_throughout=True, progress_bar=True)

    newparams = copy.copy(params)
    for i, p in enumerate(newparams):
        if hasattr(p, 'caldata') and p.caldata is not None:
            continue
        vals = v[p.name].trace[:].ravel()
        print "Calibrated %s to a PDF with mean=%s and dev=%s" % (p.name, np.mean(vals), np.std(vals))
        pdf = puq.ExperimentalPDF(vals, fit=True)
        newparams[i] = puq.CustomParameter(newparams[i].name,
                                           newparams[i].description,
                                           pdf=pdf,
                                           use_samples=True)
        try:
            newparams[i].values = copy.copy(p.values)
        except:
            pass
        newparams[i].original_parameter = p

    return newparams
