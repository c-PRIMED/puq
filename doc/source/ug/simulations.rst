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

	~/memosa/src/puq/examples/rosen> gcc -o rosen_cprog rosen_cprog.c
	~/memosa/src/puq/examples/rosen> ./rosen_cprog -x 0 -y 1
	HDF5:{'name':'z','value':1.0100000000000000e+02,'desc':'f(x,y)'}:5FDH

It works the same as the python version.  To use it, we need to make a
simple change to our control script.

.. literalinclude:: ../../../examples/rosen/rosen_c.py
    :linenos:
    :language: python

The important line is where it says::

	exe="./rosen_cprog -x %1 -y %2"

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

	~/memosa/src/puq/examples/rosen> octave -q --eval 'rosen(1,.5)'
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

Wrappers
--------

What do you do when you have a complex simulation that cannot be easily modified to
support PUQs input and output requirements?  Perhaps it is commercial simulation
code that cannot be modified.  In these cases, you must write a *wrapper*; a small program
that translates between PUQs I/O requirements and those of the wrapped simulation code.

Example wrapper scripts are in memosa/src/puq/examples/wrapper.
Examples include:

:sim.py: Simulation. Reads parameters on the command line and
	writes the output embedded in some text.
:sim_file.py: Like the previous, but reads parameters from a file and writes output to a file.

-----

:sim_wrap.py: Example python wrapper for sim.py.
:sim_wrap.sh: Example bash wrapper for sim.py.
:sim_file_wrap.py: Example python wrapper for sim_file.py.
:sim_file_wrap.sh: Example bash wrapper for sim_file.py.

-----

:quad.py: Control script for PUQ that uses sim_wrap wrappers.
:quad_file.py: Control script for PUQ that uses sim_file_wrap wrappers.

-----

*sim.py* and *sim_file.py* are treated as black box simulations.  They have particular ways they work and the wrapper
scripts need to wrap them.

The python and bash example wrappers are interchangeable.  You can write wrappers in any language.

The control scripts interact with the wrappers through the :doc:`../reference/testprogram` class.  They control how
parameters are passed on the command line.  They also can cause every job to be run in a separate directory, and
can have certain common datafile copied into those directories.

