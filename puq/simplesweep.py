"""
Simple Sweep Method.

This just does evaluations at a list of sample points.

This file is part of PUQ
Copyright (c) 2013 PUQ Authors
See LICENSE file for terms.
"""
from __future__ import absolute_import, division, print_function

import numpy as np
from logging import debug
from puq.psweep import PSweep
from puq.util import process_data
from puq.jpickle import pickle
from .response import SampledFunc


class SimpleSweep(PSweep):
    def __init__(self, params, valarray=None, response=False, iteration_cb=None):
        PSweep.__init__(self, iteration_cb)
        self.response = response
        self.params = params
        self._start_at = 0
        if valarray is None:
            ok = 0
            try:
                # are all the value arrays the same length?
                ok = len(set([len(p.values) for p in params]))
            except:
                pass
            if ok != 1:
                raise ValueError('Valarray needs to be set or all parameters need to set their values.')
            self.num = len(params[0].values)
        else:
            if type(valarray) == list:
                valarray = np.array(valarray)
            if len(valarray.shape) == 1:
                valarray = valarray.reshape(1, -1)
            if not isinstance(valarray, np.ndarray) or valarray.shape[0] != len(params):
                raise ValueError('Valarray needs to be a 2D array with rows = number of params.')
            self.num = valarray.shape[1]
            for i, p in enumerate(self.params):
                p.values = valarray[i]

    # Returns a list of name,value tuples
    # For example, [('t', 1.0), ('freq', 133862.0)]
    def get_args(self):
        for i in range(self._start_at, self.num):
            yield [(p.name, p.values[i]) for p in self.params]

    def _do_pdf(self, hf, data):
        mean = np.mean(data)
        dev = np.std(data)
        print("Mean   = %s" % mean)
        print("StdDev = %s" % dev)
        if self.response:
            rsd = np.vstack(([p.values for p in self.params], data))
            try:
                rs = pickle(SampledFunc(*rsd, params=self.params))
                return [('response', rs), ('mean', mean), ('dev', dev)]
            except:
                pass
        return [('mean', mean), ('dev', dev)]

    def analyze(self, hf):
        debug('')
        process_data(hf, 'simplesweep', self._do_pdf)

    def extend(self, valarray):
        for i, p in enumerate(self.params):
            p.values = np.concatenate((p.values, valarray[i]))
        self._start_at = self.num
        self.num += valarray.shape[1]
