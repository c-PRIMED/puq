Getting Started
===============

PUQ works on Linux and MacOSX.

nanoHUB Workspaces
------------------

If you have access to a nanoHUB workspace, PUQ is already installed.
If 'puq' is not in your path, use the 'use' command to load it.
::

  ~> which puq
  ~> use -e puq-2.2.1
  ~> which puq
  /apps/share64/debian7/puq/puq-2.2.1/build-debian7/bin/puq

Type 'use' without arguments to see a list of packages.  You should use
the latest version of PUQ.

Installing from PyPI
--------------------

PUQ uses distutils, which is the default way of installing python
modules. Simply do::

  pip install puq

The installer might ask you to install some other packages first.
Just use 'pip' to install them.  For the Mac, we have very
successfully used Anaconda, a free Python distribution containing
all the required components to install PUQ. https://store.continuum.io/cshop/anaconda/


Building and Installing from Sources
------------------------------------

If you are a developer and have a local copy of the sources,

To install in your home directory, use:
::

  python setup.py install --user

To install for all users on Unix/Linux or Mac:
::

  python setup.py build
  sudo python setup.py install

For more information: https://pypi.python.org/pypi/puq/ and
https://github.com/martin-hunt/puq

------

To test that everything is set up properly, just try the **puq** command
without any arguments. Correct output should look something like this::

  > puq

  This program does parameter sweeps for uncertainty
  quantification and optimization.

  Usage: puq [-q|-v] [start|stop|status|resume|analyze|plot]
  Options:
  -q                           Quiet.  Useful for scripts.

  -v                           Verbose. Show even more information.

  -k                           Keep temporary directories.

  start script[.py] [args]     Start PUQ using script 'script'

  status [id]                  Returns the number of jobs remaining in the sweep.

  resume [id]                  Resumes execution of sweep 'id'.

  analyze [options] [id]       Does post-processing.

  extend [id]                  Extend a sweep by adding additional jobs.

  plot [options] [id]          Plots output pdf(s) or response surface. Type
  'puq plot -h' for options.

  read                         Read a parameter or PDF from a python input script,
                               json file, csv file, or URI.  Visualize, modify, and save it.

  strip                        PUQ keeps all stdout from every job.  This command
                               removes output lines not containing data and
                               repacks the HDF5 file, reducing its size.

  dump                         Dumps output data in CSV format.

Requirements
------------

The Control Script
^^^^^^^^^^^^^^^^^^

To get started, you will need to write a control script. This script is actually a small
Python function.  Other parameter sweep frameworks usually use text file or
XML for this. However by using Python,  we can have much more flexibility.  You will not have to
know much about Python to create a simple control script.

The control script must declare three objects::

 1. At least one parameter, which will be swept by the run.
 2. A test program which takes the parameter(s) as a command line argument.
 3. A host, which right now is either the local host running interactively,
 or the PBS batch scheduler, running locally.

These three objects are combined to form a Sweep object which the UQ system will use. Each of the above objects will be explained in detail.

Good examples of control script are found in puq/examples.

Parameters
^^^^^^^^^^

Parameters represent inputs to our test program. Parameters are values that will be
changing in different runs of our test program.

For scaling sweeps or optimization runs, the parameter represents values that can be
changed for different runs.

For uncertainty quantification, parameters are random variables which can be discrete or continuous.

A *discrete* parameter has a finite number of values.

*Continuous* parameters can be *aleatoric* or *epistemic*.

 * *Aleatoric* parameters are variables that contain inherent randomness that cannot be reduced
   by better data. They are specified by a PDF (Probability Density Function).
 * *Epistemic* parameters are values that are uncertain due to a lack of data or understanding.
   You may choose to represent this uncertainty about their value as a PDF and treat them
   as aleatoric. However, there are other ways to model uncertainty of epistemic parameters
   which will be supported in the future.

Parameters are represented as PDFs. They might be approximated by a standard PDF, such as uniform,
or gaussian (normal).  Or they can be created from the results of experiments or measurements.

.. seealso:: :doc:`../reference/parameters`

Test Program
^^^^^^^^^^^^

The test program is a function (typically a simulation) that takes inputs and generates outputs. PUQ requires that the
test program take numerical parameters on the command line. If you have a test program that reads parameters some other way, it may
be necessary to create a wrapper script for it.

Host
^^^^

Jobs can be run sequentially or in parallel on an interactive scheduler.
This would be the typical desktop or workstation.
PBS, TORQUE, and HUBzero submit are also supported for use in cluster
environments.




