puqutil - Output Functions for PUQ
====================================

.. currentmodule:: puqutil

Output Format
-------------

The purpose of these functions is to provide a simple way to output in the
format PUQ expects.

PUQ expects to see output values written to standard output.  It captures all standard output,
and scans it looking for a pattern at the beginning of every line. Lines which
don't match this pattern are ignored.

**HDF5:{'name': n, 'desc': d, 'value':v}:5FDH**

where

:n: Name of the variable
:d: Description of the variable
:v: Value of the variable




Python Functions
----------------

::

	from puqutil import dump_hdf5

	dump_hdf5('v', v, 'velocity of the swallow')

.. function:: dump_hdf5(name, val[, desc=''])

	Writes data to stdout with formatting so PUQ can automatically
	recognize it and save it.

	:param name: Name of the variable
	:param val: Value of the variable
	:type val: integer, float, or array
	:param desc: A description of the variable. Saved as an attribute for the variable in the HDF file. Used as labels in plots. Default is an empty string.

Functions for C/C++
-------------------

These are included in "dump_hdf5.h"

.. cfunction:: void dump_hdf5_d(char * name, double val, char *desc)

	Writes data to stdout with formatting so PUQ can automatically
	recognize it and save it.

	:param name: Name of the variable
	:type name: C string
	:param val: The value of the variable
	:type val: double
	:param desc: A description of the variable. Saved as an	attribute for the variable in the HDF file. Used as labels in plots. Default is an empty string.
	:type desc: C string

.. cfunction:: void dump_hdf5_l(char * name, long val, char *desc)

	Writes data to stdout with formatting so PUQ can automatically
	recognize it and save it.

	:param name: Name of the variable
	:type name: C string
	:param val: The value of the variable
	:type val: long integer
	:param desc: A description of the variable. Saved as an	attribute for the variable in the HDF file. Used as labels in plots. Default is an empty string.
	:type desc: C string

