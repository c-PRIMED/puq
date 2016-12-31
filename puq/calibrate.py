"""
This file is part of PUQ
Copyright (c) 2013-2106 PUQ Authors
See LICENSE file for terms.
"""
from __future__ import absolute_import, division, print_function

import sys
import puq
import numpy as np
import copy
import pymc
from scipy.stats.kde import gaussian_kde


class Calibrate(object):
    """
    Bayesian calibration of variables.

    Args:
      model(string or function): An expression or function.
      The standard python math functions defined at
      https://docs.python.org/2/library/math.html are implemented.
      'pi' and 'e' are not defined.

      cvars(dict): Dictionary containing calibration variable
        prior PDFs and calibration types.  Example:
        {
            'a': {'prior': 'Uniform(5,20)', 'type': 'D'},
            'b': {'prior': 'Normal(1,100)', 'type': 'S'},
        }

      nvars(dict): A dictionary of variable names
        and data arrays representing observed values.
        Example: {'x': xdata, 'y': ydata} where
        the data arrays are nx2 (two- column) with the first
        column values and the second column deviations (measurement errors).

      outvar(dict): Dictionary with one entry containing the
        observed output data and uncertainty as a two-column array.

    Returns: A Calibrate object. You should use it to call the run method
      to do the actual MCMC calibration.

    -------------------

    Prior PDFs:
      Normal(mean,dev) : For example, "Normal(100,1)"
      Uniform(min,max) : For example, "Uniform(100,120)"

    Calibration Types:
        'D': Deterministic. Calibrate for a fixed value.
        'S': Stochastic. Calibrate the variable mean and deviation.
    """

    # model can be response surface, equation, python function

    def __init__(self, model, cvars, nvars, outvar, MAP='fmin_powell'):

        out_var_name = list(outvar.keys())[0]

        if callable(model):
            # model is a python function
            self.model = model
        else:
            try:
                if model.find('=') != -1:
                    m = model.split('=')
                    if m[0].strip() == out_var_name:
                        model = m[1].strip()
                    elif m[1].strip() == out_var_name:
                        model = m[0].strip()
                    else:
                        raise
                model = sympy.sympify(model, _clash)
            except:
                err = "Model expression must be of form 'varname=expression'\
                and varname must have measured data in the data table."
                raise ValueError(err)

            # find our variable names
            val_names = list(map(str, model.free_symbols))

            # all variables in the model must be defined
            if set(val_names) != set(nvars.keys()).union(set(cvars.keys())):
                missing = list(set(val_names).difference(set(nvars.keys()).union(set(cvars.keys()))))
                if missing == []:
                    errstr = 'Error: Model did not use all parameters'
                else:
                    errstr = "Error: Not all parameters in the model were defined."
                    errstr += "\'%s\' not defined." % missing[0]
                raise ValueError(errstr)

            # turn our symbolic expression into a fast, safe function call
            self.model = lambdify(model.free_symbols, model, dummify=False, modules=['numpy', 'mpmath', 'sympy'])

        out_var = outvar[out_var_name]
        var = {}
        means = {}
        devs = {}
        dlen = out_var.shape[0]
        self.num_samples = 100000
        self.num_burn = 20000
        self.num_thin = 8

        # Calibration variables
        for v in cvars.keys():
            v = str(v)  # pymc doesn't like unicode
            # convert to lowercase and parse
            d = cvars[v]['prior'].lower().replace('(', ',').replace(')', '').split(',')
            d[1] = float(d[1])
            d[2] = float(d[2])
            if cvars[v]['type'] == 'S':
                if d[0] == 'normal':
                    # normal prior with mean d[1] and deviation d[2]
                    means[v] = pymc.Normal(v + '_mean', mu=d[1], tau=1 / d[2] ** 2, value=d[1])
                    values = np.linspace(d[1] - 3 * d[2], d[1] + 3 * d[2], out_var.shape[0])
                    dval = d[2]
                elif d[0] == 'uniform':
                    # uniform prior from d[1] to d[2]
                    means[v] = pymc.Uniform(v + '_mean', d[1], d[2], value=(d[1] + d[2]) / 2.0)
                    values = np.linspace(d[1], d[2], out_var.shape[0])
                    dval = 1
                else:
                    start_val = (d[1] + d[2]) / 2.0
                    values = np.linspace(d[1], d[2], out_var.shape[0])
                    dval = 1
                    means[v] = pymc.Stochastic(name=v + '_mean',
                                               logp=lambda value: -np.log(value),
                                               doc='',
                                               parents={},
                                               value=start_val)

                # Jeffrey prior for deviation
                devs[v] = pymc.Stochastic(name=v + '_dev',
                                          logp=lambda value: -np.log(value),
                                          doc='',
                                          parents={},
                                          value=dval)

                # to get a reliable deviation, we need more samples
                if self.num_samples < 1000000:
                    self.num_samples *= 10
                    self.num_burn *= 10
                    self.num_thin *= 10
                # create a stochastic node for pymc with the mean and
                # dev from above and some initial values to try
                var[v] = pymc.Normal(v, mu=means[v], tau=1.0 / devs[v] ** 2, value=values)
            else:
                if d[0] == 'normal':
                    var[v] = pymc.Normal(v, mu=d[1], tau=1 / d[2] ** 2)
                elif d[0] == 'uniform':
                    var[v] = pymc.Uniform(v, lower=d[1], upper=d[2])
                elif d[0] == 'jeffreys':
                    start_val = (d[1] + d[2]) / 2.0
                    var[v] = pymc.Stochastic(name=v, doc='',
                                             logp=lambda value: -np.log(value),
                                             parents={},
                                             value=start_val)
                else:
                    print('Unknown probability distribution: %s' % d[0])
                    return None
        for v in nvars.keys():
            var[v] = nvars[v][:, 0]

        results = pymc.Deterministic(
            eval=self.model,
            name='results',
            parents=var,
            doc='',
            trace=True,
            verbose=0,
            dtype=float,
            plot=False,
            cache_depth=2)

        mdata = out_var[:, 0]
        mdata_err = out_var[:, 1]

        mcmc_model_out = pymc.Normal('model_out', mu=results, tau=1.0 / mdata_err ** 2, value=mdata, observed=True)
        self.mcmc_model = pymc.Model(list(var.values()) + list(means.values()) + list(devs.values()) + [mcmc_model_out])

        if MAP is not None:
            # compute MAP and use that as start for MCMC
            map_ = pymc.MAP(self.mcmc_model)
            map_.fit(method=MAP)

            print('\nmaximum a posteriori (MAP) using', MAP)
            for v in cvars.keys():
                print('%s=%s' % (v, var[v].value))
            print()

        # NOT calibration variables
        for v in nvars.keys():
            data = nvars[v][:, 0]
            err = nvars[v][:, 1]
            if np.all(err <= 0.0):
                var[v] = data
            else:
                err[err == 0] = 1e-100
                # norm_err = pymc.Normal(v + '_err', mu=0, tau=1.0 / err ** 2)
                # var[v] = data + norm_err
                var[v] = pymc.Normal(v + '_err', mu=data, tau=1.0 / err ** 2)

        results = pymc.Deterministic(
            eval=self.model,
            name='results',
            parents=var,
            doc='',
            trace=True,
            verbose=0,
            dtype=float,
            plot=False,
            cache_depth=2)

        self.mcmc_model = pymc.Model(list(var.values()) + list(means.values()) + list(devs.values()) + [mcmc_model_out])
        self.cvars = cvars
        self.var = var
        self.dlen = dlen
        self.means = means
        self.devs = devs

    def run(self, samples=None, progress=True):
        """
        Perform MCMC calibration. Returns pdfs and MCMC traces.

        Args:
          samples(integer or tuple): A tuple containing the
            number of samples, the number to burn, and the number to thin.
            If samples is an integer, burn will be 20% of the samples and
            thin will be 8.  Default will use between 10000 and 1000000
            samples, depending on the number of stochastic variables
            being calibrated.

          progress(boolean): If True, will display a progress bar.

        Returns(tuple):
          Returns a tuple containing cvars and a pdf.
          cvars is modified to include key 'trace'
          which will be an array.  It will also have a key 'pdf' which
          will be a PDF function.  For GAUSSIAN type, it will also
          include traces 'mtrace' and 'dtrace' and 'jpdf' corresponding
          to the mean and deviation traces and the joint PDF.

        """
        if samples is None:
            num_samples = self.num_samples
            num_burn = self.num_burn
            num_thin = self.num_thin
        else:
            if type(samples) == tuple:
                if len(samples) != 3:
                    raise ValueError("Error: samples should be a number or tuple of length 3.")
                num_samples, num_burn, num_thin = samples
            else:
                num_samples = samples
                num_burn = int(samples * 0.20)
                num_thin = 8

        Calibrate.mcmc = pymc.MCMC(self.mcmc_model)
        Calibrate.mcmc.sample(
            iter=num_samples,
            burn=num_burn,
            thin=num_thin,
            tune_interval=10000,
            tune_throughout=True,
            progress_bar=progress)

        if Calibrate.mcmc is None:
            return None

        for v in self.cvars.keys():
            t = self.var[v].trace[:]
            if len(t.shape) == 2:
                self.cvars[v]['ntraces'] = t.shape[1]
            else:
                self.cvars[v]['ntraces'] = 1
            self.cvars[v]['trace'] = t.ravel()

        for v in self.means.keys():
            self.cvars[v]['mtrace'] = self.means[v].trace[:]
            self.cvars[v]['dtrace'] = self.devs[v].trace[:]

        # collect all the independent variables and compute KDE
        col_count = max([self.cvars[v]['ntraces'] for v in self.cvars])
        for cv in self.cvars.keys():
            if self.cvars[cv]['type'] == 'S':
                data = np.column_stack((self.cvars[cv]['dtrace'], self.cvars[cv]['mtrace']))
                try:
                    self.cvars[cv]['jpdf'] = gaussian_kde(data.T)
                except:
                    self.cvars[cv]['jpdf'] = None
            # multidimensional traces get flattened and others
            # get repeated to match size.
            if self.cvars[cv]['ntraces'] == col_count:
                n = 1
            else:
                n = col_count
            try:
                self.cvars[cv]['pdf'] = gaussian_kde(self.cvars[cv]['trace'].ravel())
            except:
                self.cvars[cv]['pdf'] = None
            self.cvars[cv]['trace'] = self.cvars[cv]['trace'].ravel().repeat(n)

        data = np.column_stack([self.cvars[v]['trace'] for v in sorted(self.cvars.keys())])
        try:
            k = gaussian_kde(data.T)
        except:
            k = None

        return (self.cvars, k)


def calibrate(params, caldata, err, func, num_samples=None):
    """
    Performs Bayesian calibration for a variable or variables.  This
    function provides a convenient interface for use with PUQ.

    Args:
      params (list): PUQ input parameters. Parameters which have caldata
      included are not calibrated. Parameters without caldata must
      have a caltype.

      caldata (list or array): Experimental output values.

      err (float or array of floats): Standard deviation of the measurement
          error in **caldata**.  If this is a scalar, then use the same error
          for every data point.

      func: Response function.

      num_samples:  A tuple containing the number of samples, the number
        to burn, and the number to thin.  If samples is an integer, burn
        will be 20% of the samples and thin will be 8.  Default will use
        between 10000 and 1000000 samples, depending on the number of
        stochastic variables being calibrated.

    Returns:
      A copy of **params** modified with the calibrated variables.
    """
    print("Performing Bayesian Calibration...")

    cvars = {}
    nvars = {}
    ovar = {}

    err = np.broadcast_to(err, caldata.shape)
    ovar['out'] = np.column_stack((caldata, err))

    # For each PUQ parameter
    for p in params:
        p.name = str(p.name)
        if hasattr(p, 'caldata') and p.caldata is not None:
            # noncalibration parameter with measurements and errors
            if len(p.caldata.shape) != 2:
                print('\nWarning: caldata for %s should have two columns.' % p.name)
                print('Column 1 is the data and column 2 is the error.')
                print("Assuming error is zero and continuing.\n")
                err = np.broadcast_to(0, p.caldata.shape)
                p.caldata = np.column_stack((p.caldata, err))
            nvars[p.name] = p.caldata
        else:
            if isinstance(p, puq.NormalParameter):
                prior = 'Normal(%s,%s)' % (p.pdf.mean, p.pdf.dev)
            elif isinstance(p, puq.UniformParameter):
                prior = 'Uniform(%s,%s)' % (p.pdf.range[0], p.pdf.range[1])
            else:
                print('\nWARNING: Only Normal and Uniform priors are currently supported.')
                print('\tContinuing using Uniform\n')
                prior = 'Uniform(%s,%s)' % (p.pdf.range[0], p.pdf.range[1])
            cvars[p.name] = {'prior': prior, 'type': p.caltype}

    c = Calibrate(func, cvars, nvars, ovar)
    cvars, kpdf = c.run(samples=num_samples)

    newparams = copy.copy(params)
    for i, p in enumerate(newparams):
        if hasattr(p, 'caldata') and p.caldata is not None:
            continue

        vals = cvars[p.name]['trace']
        print("Calibrated %s to a PDF with mean=%s and dev=%s" % (p.name, np.mean(vals), np.std(vals)))
        pdf = puq.ExperimentalPDF(vals, fit=True)
        newparams[i] = puq.CustomParameter(newparams[i].name,
                                           newparams[i].description,
                                           pdf=pdf,
                                           use_samples=True)
        try:
            newparams[i].values = copy.copy(p.values)
        except:
            pass
        newparams[i].trace = vals
        newparams[i].original_parameter = p

    return newparams, kpdf
