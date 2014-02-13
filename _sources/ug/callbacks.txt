Callbacks
=========

Each UQ method can call a function after a sweep. This
callback function returns a boolean.  If it returns True,
the sweep is over.  Otherwise, sweep parameters can be changed and
the sweep continued.  The same thing could be done with a script, but
the callback function makes it more convenient.

A good example of this is examples/iter/rosen_sm.py

.. literalinclude:: ../../../examples/iter/rosen_sm.py
    :linenos:
    :language: python

::

    ~/puq/examples/iter> puq start rosen_sm
    Saving run to sweep_46691621.hdf5

    Processing <HDF5 dataset "z": shape (5,), type "<f8">
    	Surface   = -1.99999999999997*x + 669.0
    	RMSE      = 6.84e+02 (4.26e+01 %)

    SENSITIVITY:
    Var      u*            dev
    -----------------------------
    x    3.2080e+03    3.2080e+03
    y    8.0000e+02    8.0000e+02
    callback: rmse=42.5626179426%
    Extending Smolyak to level 2

    Processing <HDF5 dataset "z": shape (13,), type "<f8">
    	Surface   = 300.99999999956*x**2 - 1.59872115546023e-14*x*y ...
    	RMSE      = 7.40e+02 (2.05e+01 %)

    SENSITIVITY:
    Var      u*            dev
    -----------------------------
    x    3.9402e+03    5.2374e+03
    y    2.0828e+03    1.8510e+03
    callback: rmse=20.4983861252%
    Extending Smolyak to level 3

    Processing <HDF5 dataset "z": shape (29,), type "<f8">
    	Surface   = 3.10862446895043e-13*x**3 - 199.999999998686*x**2*y ...
    	RMSE      = 2.40e+02 (6.66e+00 %)

    SENSITIVITY:
    Var      u*            dev
    -----------------------------
    x    4.8307e+03    6.5106e+03
    y    2.0022e+03    1.7623e+03
    callback: rmse=6.66126889943%
    Extending Smolyak to level 4

    Processing <HDF5 dataset "z": shape (65,), type "<f8">
    	Surface   = 100.000000001004*x**4 - 8.16013923099492e-14*x**3*y ...
    	RMSE      = 9.29e-09 (2.57e-10 %)

    SENSITIVITY:
    Var      u*            dev
    -----------------------------
    x    5.0835e+03    6.9637e+03
    y    1.9661e+03    1.7441e+03
    callback: rmse=2.57395820254e-10%

