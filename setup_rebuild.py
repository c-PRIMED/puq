"""
This setup file used by developers to rebuild Cython files.
"""

from setuptools import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

try:
    from numpy.distutils.misc_util import get_numpy_include_dirs    
except:
    print 'Numpy must be installed!'
    
incdirs = get_numpy_include_dirs()

setup(
    name='PUQ',
    version='2.1.0',
    author='Martin Hunt',
    author_email='mmh@purdue.edu',
    packages=['puq', 'puqutil'],
    package_data = {'' : ['../puqutil/dump_hdf5*']},
    scripts=['bin/puq'],
    url='http://memshub.org/site/memosa_docs/puq/index.html',
    license=open('LICENSE.rst').read(),
    description='PUQ Uncertainty Quantification Tool',
    long_description=open('README.rst').read(),
    cmdclass = {'build_ext': build_ext},
    ext_modules=[
        Extension("sparse_grid_cc",
                  sources=["src/sg.pyx", "src/sparse_grid_cc.cpp"],
                  include_dirs=incdirs,
                  language="c++",
                  libraries=["stdc++"]),
        ],
    install_requires=[
        "h5py >= 2.0",
        "SciPy >= 0.9",
        "PyMC >= 2.2",
        "jsonpickle",
        "matplotlib >= 1.1",
        "nose",
        "poster",
        "NumPy >= 1.6.1",                      
        "sympy >= 0.7.2"
    ],
)
