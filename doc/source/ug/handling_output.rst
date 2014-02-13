Handling Output
===============

The Standard Way
----------------

In our previous examples, we wrote test programs that used
the functions in :doc:`../reference/puqutil` to output data.
What these functions do is to simply format the data written to standard output
in such a way that PUQ can automatically recognize the data it is supposed to save.
Anything else written to stdout, as well as other files, is skipped.

When looking at stdout, you will see lines like this::

	HDF5:{'name':'z','value':1.0,'desc':'f(x,y)'}:5FDH

This tells PUQ that it should save the value "1.0" in the HDF5 file under
'output/data/z'. Actually it will save the results from all jobs in the sweep
as an array of output values under 'output/data/z'.

If you write the same variable more than once in a job, it will confuse PUQ.
It expects one value per variable per job. And by default it will run the UQ
method on each output variable. So it you output three variables, you will
get three output PDFs.

However, each output variable can be an array of values. For example, you can output
a 10x10 array (or an n-dimensional array!). In 'output/data/varname' will be an array of 10x10 arrays.
And by default, PUQ will generate a 10x10 array of output PDFs. And 'puq plot' will plot all 100 PDFs.
See puq/examples/test1 for an example of outputting arrays of data.

When the Standard Way Doesn't Work
----------------------------------

This is all very good, but what if your test program is some huge binary that cannot be modified to output
data in PUQ's format?

One solution would be to write a wrapper in a scripting language like Python, Tcl, or Ruby.
The wrapper might modify the parameters, pass them to the the big test program, capture the
output and reformat it for PUQ.

Wrappers
--------

What do you do when you have a complex simulation that cannot be easily modified to
support PUQs input and output requirements?  Perhaps it is commercial simulation
code that cannot be modified.  In these cases, you must write a *wrapper*; a small program
that translates between PUQs I/O requirements and those of the wrapped simulation code.

Example wrapper scripts are in puq/examples/wrapper.
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


