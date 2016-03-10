"""
This file is part of PUQ
Copyright (c) 2013 PUQ Authors
See LICENSE file for terms.
"""
import os
import shutil


class TestProgram(object):
    """
    Class implementing a TestProgram object representing the
    simulation to run.

    Args:
      name(string): Name of the program. This is the executable if
        no *exe* is defined.
      exe(string): An executable command template to run. Strings of
        the form '$var' are replaced with the value of *var*.
        See python template strings
        (`<http://docs.python.org/2/library/string.html#template-strings>`_)
      desc: Optional description of the test program.
      newdir(boolean): Run each job in its own directory.  Necessary
        if the simulation generates output files.  Default is False.
      infiles(list): If *newdir* is True, then this is an optional
        list of files that should be copied to each new directory.
      outfiles(list): An optional list of files that will be saved
        into the HDF5 file upon completion. The files will be in
        /output/jobs/n where 'n' is the job number.

    Example1::

      p1 = UniformParameter('x', 'x', min=-2, max=2)
      p2 = UniformParameter('y', 'y', min=-2, max=2)

      prog = TestProgram('./rosen_prog.py', desc='Rosenbrock Function')

      # or, the equivalent using template strings

      prog = TestProgram(exe='./rosen_prog.py --x=$x --y=$y',
        desc='Rosenbrock Function')


    Example2::

      # Using newdir and infiles. Will run each job in a new directory
      # with a copy of all the infiles.

      prog = TestProgram('PM2', newdir=True, desc='MPM Scaling',
        infiles=['pm2geometry', 'pm2input', 'pmgrid_geom.nc',
        'pmpart_geom.nc'])

    """

    def __init__(self, name='', exe='', newdir=False, infiles='', desc='', outfiles=''):
        self.name = name
        self.newdir = newdir
        self.infiles = infiles
        self.outfiles = outfiles
        self.exe = exe
        if self.name == '' and self.exe == '':
            raise ValueError("name or exe must be set.")
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
                name, val = args[i-1]
                mstr = '%%%d' % i
                exe = exe.replace(mstr, str(val))
        else:
            from string import Template
            t = Template(exe)
            exe = t.substitute(dict(args))
        return exe
