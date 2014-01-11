"""
This file is part of PUQ
Copyright (c) 2013 PUQ Authors
See LICENSE file for terms.
"""
import os, shutil

class TestProgram(object):
    """
    Class implementing a TestProgram object. User must supply at least a name.

    - *name* : Name of the program. This is the executable if no *exe* is defined.
    - *exe*  : (Optional) An executable command template to run. First some basic \
    substitution is done. '$var' is replaced by the value of variable 'var', etc. \
    See python template strings.
    - *desc* : Optional description of the test program. Saved in the HDF file.
    - *newdir* : Boolean indicating that each job should be run in its own directory.\
    Default is False.
    - *infiles* : If *newdir* is True, then this is an optional list of files\
    that should be copied to each new directory.
    - *outfiles* : An optional list of files that will be copied into the HDF5
    file upon completion. The files will be in /output/jobs/n where 'n' is the
    job number.

    Example1::

      prog = TestProgram('springmassdamper',
               exe="matlab -nodisplay -r 'springmassdamperl(%1, %2, %3, 1.0); quit'")

    Example2::

      prog = TestProgram('PM2', newdir=True, desc='MPM Scaling',
               infiles=['pm2geometry', 'pm2input', 'pmgrid_geom.nc', 'pmpart_geom.nc'])

    """

    def __init__(self, name, exe='', newdir=False, infiles='', desc='', outfiles=''):
        self.name = name
        self.newdir = newdir
        self.infiles = infiles
        self.outfiles = outfiles
        self.exe = exe
        if desc == '':
            desc = 'Output of %s.' % name
        self.desc = desc

    def setup(self, dirname):
        if self.newdir:
            os.makedirs(dirname)
            if self.infiles:
                for src in self.infiles:
                    shutil.copy(src, dirname)
            return dirname
        else:
            return ''

    def cmd(self, args):
        if not self.exe:
            arglist = ' '.join(['--%s=%s' % (p, v) for p, v in args])
            return '%s %s' % (self.name, arglist)
        exe = self.exe
        if exe.find('%1') > 0:
            # old style - deprecated
            for i in range(len(args), 0, -1):
                name, val  = args[i-1]
                mstr = '%%%d' % i
                exe = exe.replace(mstr, str(val))
        else:
            from string import Template
            t = Template(exe)
            exe = t.substitute(dict(args))
        return exe
