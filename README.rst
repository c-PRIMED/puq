************
Introduction
************

:Version: 2.6
:Authors: Martin Hunt
:Web site: https://github.com/c-PRIMED/puq
:Documentation: http://c-primed.github.io/puq/
:Copyright: This document has been placed in the public domain.
:License: MIT License.

Purpose
=======

PUQ is a framework for building response surfaces and performing Uncertainty
Quantification (UQ) and sensitivity analysis. It was created with the goal of
making an easy to use framework that could be easily integrated and extended.

Features
========

* Implemented as a Python library but can be used from the command line
  with a minimum of Python knowledge.

* Collects all results into a single HDF5 file.

* Implements Monte Carlo and Latin Hypercube sampling.

* For better scalability, includes a Smolyak sparse grid method.

* Builds response surfaces from sample points.

* Includes GUIs to visualize and compare PDFs and response surfaces.

* Can use PyMC to perform Bayesian calibration on input parameters.

Dependencies
============

PUQ is tested to work under Python 2.7+. 

PUQ requires the following Python modules:

- numpy >= 1.6
- scipy >= 0.8
- matplotlib >= 1.1
- sympy >= 0.7.1
- h5py >= 1.3
- jsonpickle
- poster
- pytest
- pymc

Install
=======

This package uses distutils, which is the default way of installing
python modules. To install in your home directory, use::

  python setup.py install --user

To install for all users on Unix/Linux or Mac::

  python setup.py build
  sudo python setup.py install


History
=======

PUQ is based upon work supported by the Department of Energy [National Nuclear Security Administration]
under Award Number DE-FC52-08NA28617.