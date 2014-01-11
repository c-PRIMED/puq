from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

from numpy.distutils.misc_util import get_numpy_include_dirs
incdirs = get_numpy_include_dirs()

setup(
    name = 'sparse_grid_cc',
    cmdclass = {'build_ext': build_ext},
    ext_modules=[
        Extension("sparse_grid_cc",
                  sources=["sg.pyx", "sparse_grid_cc.cpp"],
                  include_dirs=incdirs,
                  language="c++",
                  libraries=["stdc++"]),
        ],
    )

