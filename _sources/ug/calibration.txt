Calibration of Input Variables
==============================

Frequently computer models will have input parameters that cannot be measured and are not well known.
In this case, Bayesian calibration can be used to estimate the input parameters.  To do this,
experimental data is required for the output and for all known input variables.  The calibration process
adjusts the unknown parameters to fit the observed data.

Using PUQ for Calibration
-------------------------

To use PUQ to do calibration, you will have to add experimental data to all the known
input parameters.  For the TestProgram, you will need to add experimental data and (optionally)
a measurement error.  The measurement error is a standard deviation.

The presence of experimental data tells PUQ to do calibration.  The steps are as follows:

	1. Build a response surface over the range of the input paramaters.
	2. Do Bayesian calibration using the response surface for the likelihood function.
	3. Manually adjust calibrated input parameter PDFs, if necessary.  For example,  truncate PDFs that go negative.
	4. Generate output PDF.

Example
-------
test2 in puq/examples/calibrate calibrates *z*.  The experimental data was generated using a
*z* with a Normal distribution of 12 and deviation of 2.  Some noise was added with a sigma of
0.1.  For calibration we use a uniform prior [5, 20] for *z*.

.. literalinclude:: ../../../examples/calibrate/test2.py
    :linenos:
    :language: python

::

	~/puq/examples/calibrate> puq start test2.py
	Saving run to sweep_85212814.hdf5

	Processing <HDF5 dataset "f": shape (25,), type "<f8">
		Surface   = 1.0*x**2 + 1.0*x*y + 0.75*y**2 + 2.0*y - 7.0*z + 2.0
		RMSE      = 2.15e-11 (1.74e-11 %)

	SENSITIVITY:
	Var      u*            dev
	-----------------------------
	z    1.0500e+02    1.8394e-11
	y    1.8630e+01    1.1297e+00
	x    1.6505e+01    1.0054e+00
	Performing Bayesian Calibration...
	[****************100%******************]  12000 of 12000 complete
	Calibrated z to Normal(12.0786402402, 2.2152608414).

