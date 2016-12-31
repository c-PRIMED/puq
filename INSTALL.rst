INSTALLATION
============

PUQ works on Linux systems.  It has also been run successfully on MacOSX and Windows using
`anaconda`_.  It has been tested with Python 2.7 and 3.5.

To install, you should first install the dependencies listed below.  Then change to the
**puq** directory and ::

   python setup.py install


Dependencies
============

Before installation, the following must be installed.  You may want to install the
other dependencies using the normal package installation process on your system.

* `Python`_ : Version 2.7 or later.
* `NumPy`_ : The fundamental package for scientific computing with Python.
* `HDF5`_ (1.8.0 or newer): A data model, library, and file format for storing and managing data.

The installer will attempt to install the following, if not present.
Due to installer bugs present with some versions, I recommend you install them
before the installation process.

* `SymPy`_ : SymPy is a Python library for symbolic mathematics.  Note: If you get an error when the setup script installs sympy, you may have to run "pip install sympy" by hand.
* `matplotlib`_ : 2D plotting library which produces publication quality figures in a variety of image formats and interactive environments.

In addition, the following packages will be installed, if necessary,
during the installation process.

* `h5py`_ : A Pythonic interface to the HDF5 binary data format. Requires the `HDF5`_ library.
* `SciPy`_ : Library of algorithms for mathematics, science and engineering.
* `pytest`_ : A Python unit testing tool.
* `poster`_ : poster provides a set of classes and functions to faciliate making HTTP POST (or PUT) requests using the standard multipart/form-data encoding.
* `jsonpickle`_ : jsonpickle is a Python library for serialization and deserialization of complex Python objects to and from JSON.
* `PyMC`_ : PyMC is a python module that implements Bayesian statistical models and fitting algorithms, including Markov chain Monte Carlo.


Testing
=======

Run tests with "python setup.py test"


Documentation
=============

The documentation is built with Sphinx and requires the
`napoleon`_ extension.

To build the documentation, cd to the **doc** directory and type:

* make html - to build HTML docs
* make latexpdf - to build a PDF

.. _`anaconda`: https://www.continuum.io/downloads

.. _`Python`: http://www.python.org/

.. _`NumPy`: http://www.scipy.org/NumPy

.. _`matplotlib`: http://matplotlib.sourceforge.net/

.. _`SciPy`: http://www.scipy.org/

.. _`HDF5`: http://www.hdfgroup.org/HDF5/

.. _`nose`: http://somethingaboutorange.com/mrl/projects/nose/

.. _`PyMC`:  https://github.com/pymc-devs/pymc

.. _`jsonpickle`: https://github.com/jsonpickle/jsonpickle

.. _`poster`: http://atlee.ca/software/poster/

.. _`SymPy`: http://sympy.org/en/index.html

.. _`h5py`: http://www.h5py.org/

.. _`napoleon`: https://pypi.python.org/pypi/sphinxcontrib-napoleon
