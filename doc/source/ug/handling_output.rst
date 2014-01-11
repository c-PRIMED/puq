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
output and reformat it for PUQ. However, there is another option.

.. _datafilter:

A Custom Approach using the Datafilter
--------------------------------------

If PUQ finds a function named *datafilter*, it will call that function before doing UQ analysis.

.. note::

	Phases in PUQ
	
 	1. Read the control script and launch jobs.
 	2. When jobs complete, collect all the output from the jobs into the HDF5 output file.
 	3. Call the datafilter() function, if defined.
 	4. Analyze the data in the HDF5 file under 'output/data'
 
Here's an example of a datafilter function.

.. literalinclude:: ../../../examples/test2/df.py
    :linenos:
    :language: python

This example is from puq/examples/test2. In that case, the test program wrote data
in a format PUQ could read, but we decided further processing was required before
the UQ code analyzed it. The example above reads from the hdf5 file and changes
what was in 'output/data'.

The datafilter can do a lot more than that.  It can do anything Python can do and it
has access to the hdf5 file containing all the information from the sweep.

If data was written to stdout in some format PUQ did not recognize (for example, lammps),
you could have the datafilter search through 'output/jobs/#/stdout', extract the
data, and write it to 'output/data'.

If data was written to a file or files, it can open them, grab the data, and
put it it 'output/data'

puq/examples/test2
^^^^^^^^^^^^^^^^^^

Let's take a closer look at the test2 example. You might want to copy the directory
and try it yourself.

Run the sweep::

   ~/memosa/src/puq/examples/test2> puq start -f test2.hdf5 test2
   Saving run to test2.hdf5
   NOW IN DATA FILTER
   
   Processing <HDF5 dataset "x": shape (5,), type "<f8">
      Surface   = 2.0*m**2
      RMSE      = 5.36e-08 (4.35e-10 %)
   
   SENSITIVITY:
   Var      u*            dev
   -----------------------------
   m    1.2317e+04    1.2389e+03


But what if we made a mistake in the datafilter and wish to change it?  
Just edit test2.py and do::

	puq analyze test2.hdf5 --filter=test2.py
   
This reruns the datafilter without rerunning the sweep. You can also put the datafilter in a separate file::

   ~/memosa/src/puq/examples/test2> puq analyze test2.hdf5 --filter=df.py
   NOW IN DATA FILTER 2
   
   Processing <HDF5 dataset "x": shape (5,), type "<f8">
      Surface   = 4.0*m**2
      RMSE      = 1.07e-07 (4.35e-10 %)
   
   SENSITIVITY:
   Var      u*            dev
   -----------------------------
   m    2.4635e+04    2.4778e+03

It runs the datafilter in 'df.py' instead of the original one in 'test2.py'.
Note the change in the response surface.


