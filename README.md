Introduction
============

Version
:   2.2

Authors
:   Martin Hunt

Web site
:   
Documentation
:   <http://memshub.org/site/memosa_docs/puq/index.html>

Copyright
:   This document has been placed in the public domain.

License
:   MIT License.

Purpose
-------

PUQ is a framework for building response surfaces and performing
Uncertainty Quantification (UQ) and sensitivity analysis. It was created
with the goal of making an easy to use framework that could be easily
integrated and extended.

Features
--------

-   Implemented as a Python library but can be used from the command
    line with a minimum of Python knowledge.

-   Collects all results into a single HDF5 file.

-   Implements Monte Carlo and Latin Hypercube sampling.

-   For better scalability, includes a Smolyak sparse grid method.

-   Builds response surfaces from sample points.

-   Includes GUIs to visualize and compare PDFs and response surfaces.

-   Can use PyMC to perform Bayesian calibration on input parameters.

What's new in version 2.2
-------------------------

-   Improved variable substitution for TestProgram().

-   Add DParameter class.

-   Add SimpleSweep() examples.

-   Add SubmitHost(), support for hub's submit command.

What's new in version 2.1
-------------------------

-   When experimental data is available, can perform Bayesian
    Calibration on input parameters.

-   Added better scripting examples.

History
-------

PUQ is based upon work supported by the Department of Energy [National
Nuclear Security Administration] under Award Number DE-FC52-08NA28617.”
