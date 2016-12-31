"""
Latin Hypercube Sampling and Descriptive Sampling

This file is part of PUQ
Copyright (c) 2013 PUQ Authors
See LICENSE file for terms.
"""
from __future__ import absolute_import, division, print_function

import sys
import numpy as np
from puq.util import process_data
from puq.psweep import PSweep
from logging import debug
from .response import SampledFunc
from puq.jpickle import pickle
from puq.pdf import UniformPDF


class LHS(PSweep):
    """
    Class implementing Latin hypercube sampling (LHS).

    Args:
      params: Input list of :class:`Parameter`\s.
      num: Number of samples to use.
      ds(boolean): Use a modified LHS which always picks the center
        of the Latin square.
      response(boolean): Generate a response surface using the sample
        points.
      iteration_cb(function): A function to call after completion.
    """
    def __init__(self, params, num, ds=False, response=True, iteration_cb=None):
        PSweep.__init__(self, iteration_cb)
        self.params = params
        num = int(num)
        self.num = num
        self.ds = ds
        self.response = response
        self._start_at = 0

        if self.response:
            # To generate a complete response surface, use Uniform distributions
            # with the same range as the original distributions.
            for p in self.params:
                if ds:
                    p.values = UniformPDF(*p.pdf.range).ds(num)
                else:
                    p.values = UniformPDF(*p.pdf.range).lhs(num)
        else:
            for p in self.params:
                if ds:
                    p.values = p.pdf.ds(num)
                else:
                    p.values = p.pdf.lhs(num)

    # Returns a list of name,value tuples
    # For example, [('t', 1.0), ('freq', 133862.0)]
    def get_args(self):
        for i in range(self._start_at, self.num):
            yield [(p.name, p.values[i]) for p in self.params]

    def _do_pdf(self, hf, data):
        if self.response:
            # The response surface was built using Uniform distributions.
            # We are interested in the mean and deviation of the data
            # that would have been produced using the real PDFs. For this,
            # we need to compute a weighted mean and deviation
            weights = np.prod([p.pdf.pdf(p.values) for p in self.params], 0)
            tweight = np.sum(weights)
            mean = np.average(data, weights=weights)
            dev = np.sqrt(np.dot(weights, (data - mean)**2) / tweight)

            print("Mean   = %s" % mean)
            print("StdDev = %s" % dev)

            rsd = np.vstack(([p.values for p in self.params], data))
            rs = pickle(SampledFunc(*rsd, params=self.params))
            return [('response', rs), ('mean', mean), ('dev', dev)]

        else:
            print("Mean   = %s" % np.mean(data))
            print("StdDev = %s" % np.std(data))
            return [('samples', data), ('mean', np.mean(data)), ('dev', np.std(data))]

    def analyze(self, hf):
        debug('')
        process_data(hf, 'lhs', self._do_pdf)

    # extend the sample size by a factor of 3
    # This works for DS because it always chooses the center of the probability bins.
    # This means we can extend by using 3 times the bins.
    # |     *     |     *     |
    # | * | * | * | * | * | * |

    def extend(self, num=None):
        if not hasattr(self, 'ds') or not self.ds:
            print("You must use Descriptive Sampling to extend.")
            sys.exit(1)

        print("Extending Descriptive Sampling run to %s samples." % (self.num * 3))
        for p in self.params:
            if self.response:
                v = np.sort(UniformPDF(*p.pdf.range).ds(self.num * 3))
            else:
                v = np.sort(p.pdf.ds(self.num * 3))
            # remove the ones we already did
            v = np.concatenate((v[0::3], v[2::3]))
            p.values = np.concatenate((p.values, np.random.permutation(v)))
        self._start_at = self.num
        self.num *= 3
