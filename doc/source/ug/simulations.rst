Making PUQ Work With Your Code
==============================

PUQ makes no assumptions about how your test program (or simulation) code
works.  However it does need a way to pass parameter values into the test program
and read results.

C Programs
----------

In this example, we use a test program compiled in C. The point of
this is to show how to pass parameters to test programs that do
not use the "--varname=value" pattern we have been using.

The test program is  puq/examples/rosen/rosen_cprog.c

.. literalinclude:: ../../../examples/rosen/rosen_cprog.c
    :linenos:
    :language: c

.. note:: dump_hdf5_d() dumps a double in our output format.  It is included in dump_hdf5.h.

	.. seealso:: :doc:`../reference/puqutil`

You can compile it and test it out::

	~/puq/examples/rosen> gcc -o rosen_cprog rosen_cprog.c
	~/puq/examples/rosen> ./rosen_cprog -x 0 -y 1
	HDF5:{'name':'z','value':1.0100000000000000e+02,'desc':'f(x,y)'}:5FDH

It works the same as the python version.  To use it, we need to make a
simple change to our control script.

.. literalinclude:: ../../../examples/rosen/rosen_c.py
    :linenos:
    :language: python

The important line is where it says::

	exe="./rosen_cprog -x $x -y $y"

.. seealso:: :doc:`../reference/testprogram`

Finally, do 'puq start rosen_c' and try it out.

Matlab Programs
---------------

In this example, we use a test program written in Matlab and executed either by Matab or Octave.
The example is very much like the previous one using C.

The test program is  puq/examples/rosen/rosen.m

.. literalinclude:: ../../../examples/rosen/rosen.m
    :linenos:
    :language: matlab

The biggest difference between this and our other example is that we do not (yet)
have a dump_hdf5() function for Matlab. Instead we must write out output variable(s)
in carefully formatted fprintfs. This puts our data in a tagged format such that PUQ can
recognize it.

You should test the test program::

	~/puq/examples/rosen> octave -q --eval 'rosen(1,.5)'
	HDF5:{"name": "z", "value": 25, "desc": ""}:5FDH


It works the same as the python version.  To use it, we need to make a
simple change to our control script.

.. literalinclude:: ../../../examples/rosen/rosen_ml.py
    :linenos:
    :language: python

The syntax to execute a function from the command line differs between Octave and Matlab.
If you have Matlab, you can comment the Octave line out and uncomment the Matlab line.

Finally, do 'puq start rosen_ml' and try it out.

.. seealso:: :doc:`../reference/testprogram`


Fortran Programs
----------------

There is a Fortran version of the Rosenbrock test in
examples/fortran.  It works very much like the C version.

