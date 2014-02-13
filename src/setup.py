from distutils.core import setup
from Cython.Build import cythonize

from numpy.distutils.misc_util import get_numpy_include_dirs
incdirs = get_numpy_include_dirs()

setup(
  name = 'sparse_grid_cc',
  ext_modules= cythonize(["*.pyx"]),
  )

