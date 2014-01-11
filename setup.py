from setuptools import setup
from distutils.extension import Extension

try:
    from numpy.distutils.misc_util import get_numpy_include_dirs
    incdirs = get_numpy_include_dirs()
except:
    print 'Numpy must be installed!'
    import sys
    sys.exit(1)


vt = open('puq/version.py').read()
puq_version = str(vt.split("'")[1])

setup(
    name='puq',
    version=puq_version,
    author='Martin Hunt',
    author_email='mmh@purdue.edu',
    packages=['puq', 'puqutil'],
    package_data={'': ['*.rst'], 'puqutil': ['*.f90', '*.h']},
    scripts=['bin/puq'],
    url='http://memshub.org/site/memosa_docs/puq/index.html',
    license=open('LICENSE.rst').read(),
    description='PUQ Uncertainty Quantification Tool',
    long_description=open('README.rst').read(),
    test_suite='nose.collector',
    zip_safe=False,
    ext_modules=[
        Extension("sparse_grid_cc",
            sources=["src/sg.cpp", "src/sparse_grid_cc.cpp"],
            include_dirs=incdirs,
            language="c++",
            libraries=["stdc++"]),
    ],
    install_requires=[
        "h5py >= 1.3",
        "SciPy >= 0.8",
        "PyMC == 2.2",
        "jsonpickle",
        # "matplotlib >= 1.1",
        "nose",
        "poster",
        # "sympy >= 0.7.1"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Scientific/Engineering :: Information Analysis"
    ]
)
