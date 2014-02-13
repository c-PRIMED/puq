from setuptools import setup
from distutils.extension import Extension
import sys

def check_dep(mv):
    import re
    """
    Can't get install_requires to always do the right thing, so
    we do this the hard way.  Just check dependencies and abort
    if all is not well.
    """
    ok = True
    for p,v in mv.iteritems():
        vn = map(int, re.findall(r'([\d]+)', v))
        try:
            if p == 'poster':
                ver = str(__import__(p, [], [], ['version']).version)
            elif p == 'h5py':
                ver = str(__import__(p, [], [], ['version']).version.version)
            else:
                ver = __import__(p, [], [], ['__version__']).__version__
            vern = map(int, re.findall(r'([\d]+)', ver))
            for v1,v2 in zip(vn, vern):
                if v1 > v2:
                    print 'Error: Package %s needs version %s and found %s.' % (p, v, ver)
                    ok = False
                    break
                if v2 > v1:
                    break
        except:
            print 'Error: Package %s not found. Please install it.' % (p)
            ok = False
            ver = []
        # print p, v, ver
    return ok



if __name__ == "__main__":
    if sys.version_info.major == 3:
        print 'PUQ is not yet working with Python 3.'
        sys.exit(-1)
    if sys.version_info.minor < 6:
        print 'PUQ requires Python >= 2.6.'
        sys.exit(-1)

    mvers = {
    'numpy' : '1.6',
    'scipy' : '0.8',
    'h5py' : '1.3',
    'jsonpickle' : '0.4',
    'matplotlib' : '1.1',
    'sympy' : '0.7.1',
    'nose' : '0.11',
    'poster' : '0.8'
    }
    if not check_dep(mvers):
        sys.exit(-1)

    from numpy.distutils.misc_util import get_numpy_include_dirs
    incdirs = get_numpy_include_dirs()

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
        url='https://github.com/martin-hunt/puq',
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
        classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Scientific/Engineering :: Information Analysis"
        ]
        )
