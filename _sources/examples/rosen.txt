rosen
=====

.. module:: puq

The rosen test directory has examples of the *Rosenbrock* function
which is :math:`f(x,y) = 100(y-x^2)^2 + (1-x)^2`

Because the Rosenbrock function is a simple polynomial, the Smolyak
method provides the best approach.  However, Monte Carlo and Latin Hypecube
examples are provided for comparison.

Different test programs which implement the Rosenbrock function are provided
as examples of using Python, C, and Matlab code.

Contents
--------

**rosen.py**
	Example using :class:`Smolyak`

**rosen_c.py**
	Example using rosen_cprog with :class:`Smolyak`

**rosen_ml.py**
	Example using rosen.m with :class:`Smolyak`

**rosen_mc.py**
	Example using :class:`MonteCarlo`

**rosen_lhs.py**
	Example using :class:`LHS`

------

**rosen_prog.py**
	Test program written in Python

**rosen_cprog.c**
	Test program written in C.

**rosen.m**
	Test program for Matlab or Octave.

------

**Makefile**
	Makefile for rosen_cprog

