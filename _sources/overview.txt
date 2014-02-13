===============================
Overview
===============================

PUQ is a general purpose parameter sweep framework, which can perform uncertainty quantification (UQ),
do sensitivity analysis, and build response surfaces.

You provide a program that takes parameters as arguments. This is called the *Test Program*
or simulation.
It can be written in any language as long as it can take command line arguments. PUQ treats
the test program like a "black box". It need not know anything about it except how to send it
inputs and how to get the outputs.

Then you tell the framework details about the input parameters (name, mean, deviation, PDF, etc).
You also need to either have the test program write data in a standard format readable by PUQ,
or you need to supply a bit of code to PUQ that can process the output of the test program.

Finally you must tell PUQ what kind of sweep to perform (Smolyak Sparse Grid, Monte Carlo, etc) and what host to run it on.
This might change in the future as a more intelligent UQ framework should be able to automatically
select the correct method and find a host to run the sweep.

The framework then launches all the required jobs, providing the proper parameters to your test program.

If there are any problems as the jobs run (such as exceeding the allocated walltime), individual jobs can be modified and restarted.

The framework keeps track of the outputs and, once all jobs have completed, collects the outputs into a single HDF5 file. Then analysis can be performed on the collected data.
That analysis can be repeated as necessary, without rerunning the jobs.  If more data is required, a new sweep can be performed, adding to the existing data.


Goals
---------

 - Easy to use. Tools that are hard to use don't get used, or get used improperly.
 - Expandable. Should be able to handle any necessary UQ or optimization methods.

In Progress
-----------

  - Integration with HUBzero and nanoHUB platforms.

Future Plans
----------------

  - Adaptive response surface builder. Chooses the best method without
    user intervention.  Can refine until it meets a specific accuracy goal.

  - Better job control.

