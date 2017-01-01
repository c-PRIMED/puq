#!/usr/bin/env python
"""
Take two distributions, normal or uniform and simply add them together.
Tests Smolyak, MonteCarlo, and LHS

Usage: add_dist.py
"""
from puq import *
import h5py
import math
import os
from numpy import allclose
from puq.jpickle import unpickle


options['verbose'] = False
fname = 'add_dist.hdf5'

dname = os.path.dirname(os.path.realpath(__file__))
progname = 'python ' + os.path.join(dname, 'vel_add.py')

# Two Normal distributions, Smolyak
def run(progname):
    v1 = Parameter('v1', 'velocity1', mean=10, dev=2)
    v2 = Parameter('v2', 'velocity2', mean=100, dev=3)
    uq = Smolyak([v1, v2], 2)
    return Sweep(uq, InteractiveHost(), progname)

# Two Normal distributions, Monte Carlo
def runMC(progname):
    v1 = Parameter('v1', 'velocity1', mean=10, dev=2)
    v2 = Parameter('v2', 'velocity2', mean=100, dev=3)
    uq = MonteCarlo([v1, v2], 500)
    return Sweep(uq, InteractiveHost(), progname)

# Two Uniform distributions, Smolyak
def run_uniform(progname):
    v1 = Parameter('v1', 'velocity1', mean=10, max=12)
    v2 = Parameter('v2', 'velocity2', mean=100, max=110)
    uq = Smolyak([v1, v2], 2)
    return Sweep(uq, InteractiveHost(), progname)

# Two Uniform distributions, Monte Carlo
def run_uniformMC(progname):
    v1 = Parameter('v1', 'velocity1', mean=10, max=12)
    v2 = Parameter('v2', 'velocity2', mean=100, max=110)
    uq = MonteCarlo([v1, v2], 500)
    return Sweep(uq, InteractiveHost(), progname)

def test_add_norm_dist():
    sw = run(progname)
    sw.run(fname, overwrite=True)
    sw.analyze()

    h5 = h5py.File(fname)
    tv = unpickle(h5['/smolyak/total_velocity/response'].value)

    s1, s2 = unpickle(h5['/smolyak/v1/sensitivity'].value)
    assert(s2[0] == 'v2')
    assert(s2[1]['ustar'] == 0)

    s1, s2 = unpickle(h5['/smolyak/v2/sensitivity'].value)
    assert(s2[0] == 'v1')
    assert(s2[1]['ustar'] == 0)

    pdf = tv.pdf()
    assert(allclose(pdf.mean, 110., atol=.03))
    dev = math.sqrt(13)
    assert(allclose(pdf.dev, dev, atol=.15))
    h5.close()
    os.remove(fname)

def test_add_unif_dist():
    sw = run_uniform(progname)
    sw.run(fname, overwrite=True)
    sw.analyze()

    h5 = h5py.File(fname)
    tv = unpickle(h5['/smolyak/total_velocity/response'].value)

    s1, s2 = unpickle(h5['/smolyak/v1/sensitivity'].value)
    assert(s2[0] == 'v2')
    assert(s2[1]['ustar'] == 0)

    s1, s2 = unpickle(h5['/smolyak/v2/sensitivity'].value)
    assert(s2[0] == 'v1')
    assert(s2[1]['ustar'] == 0)

    pdf = tv.pdf()
    assert(allclose(pdf.mean, 110., atol=.2))

    # 5.88784057755
    dev = math.sqrt((20*20 + 4*4) / 12.0)
    assert(allclose(pdf.dev, dev, atol=.2))
    h5.close()
    os.remove(fname)

def test_add_norm_distMC():
    sw = runMC(progname)
    sw.run(fname, overwrite=True)
    sw.analyze()

    h5 = h5py.File(fname)
    assert(allclose(h5['/montecarlo/total_velocity/mean'].value, 110., atol=3))
    dev = math.sqrt(13)
    assert(allclose(h5['/montecarlo/total_velocity/dev'].value, dev, atol=1))
    h5.close()
    os.remove(fname)

def test_add_unif_distMC():
    sw = run_uniformMC(progname)
    sw.run(fname, overwrite=True)
    sw.analyze()

    h5 = h5py.File(fname)
    assert(allclose(h5['/montecarlo/total_velocity/mean'].value, 110., atol=3))

    # 5.88784057755
    dev = math.sqrt((20*20 + 4*4) / 12.0)
    assert(allclose(h5['/montecarlo/total_velocity/dev'].value, dev, atol=1))
    h5.close()
    os.remove(fname)

if __name__ == "__main__":
    options['verbose'] = True
    test_add_norm_dist()
    test_add_unif_dist()
    test_add_norm_distMC()
    test_add_unif_distMC()
