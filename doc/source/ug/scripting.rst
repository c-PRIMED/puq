Scripting PUQ
===============

All the examples so far have involved using the 'puq' command
to start a sweep and again to analyze it.  For more complicated
jobs, you can script the whole process in Python.

Running Sweeps
--------------

Example scripts are in puq/examples/scripting. test1.py
runs a level-1 Smolyak sweep, reads the response surface from
the HDF5 file, plots the PDF, then extends the level to 2 and repeats.

.. literalinclude:: ../../../examples/scripting/test1.py
    :linenos:
    :language: python

To run it, simply do::

  ./test1.py

or::

  python test1.py

Reading Results
----------------

The previous example showed how to read a response surface and
sample it to produce a pdf. The full list of python functions
for reading and writing the HDF5 file is
:doc:`../reference/hdf`



