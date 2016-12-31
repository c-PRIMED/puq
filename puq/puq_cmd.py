#!/usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, division, print_function

import subprocess, os, sys, glob, shutil
from optparse import OptionParser

import puq
from puq.psweep import PSweep
from puq.util import vprint
from puq.jpickle import unpickle
from puq.options import options

import logging
from logging import info, debug, exception, warning, critical

import numpy as np
import h5py
import matplotlib

np.set_printoptions(precision=16)
logging.basicConfig(format='%(levelname)-10s %(module)s:%(funcName)s:%(lineno)s %(message)s')


__USAGE__ = """
This program does parameter sweeps for uncertainty
quantification and optimization.

Usage: puq [-q|-v|-k] [start|stop|status|resume|analyze|plot]

You can get help for any subcommand by adding "--help" after the subcommand.  For example,
"puq start --help"

Options:
  -q                           Quiet.  Useful for scripts.

  -v                           Verbose. Show even more information.

  -V, --version                Print version and exit.

  -k                           Keep temporary directories.

  start script[.py] [args]     Start PUQ using script 'script'

  status [id]                  Returns the number of jobs remaining in the sweep.

  resume [id]                  Resumes execution of sweep 'id'.

  analyze [options] [id]       Does post-processing.

  extend [id]                  Extend a sweep by adding additional jobs.

  plot [options] [id]          Plots output pdf(s) or response surface. Type
                               'puq plot -h' for options.

  read                         Read a parameter or PDF from a python input script,
                               json file, csv file, or URI.  Visualize, modify, and save it.

  strip                        PUQ keeps all stdout from every job.  This command removes
                               output lines not containing data and repacks the HDF5 file,
                               reducing its size.

  dump                         Dumps output data in CSV format.
"""


def usage():
    print(__USAGE__)
    sys.exit(-1)


# open a sweep file given filename
def open_hdf5_file(fname, mode='r'):
    if type(fname) is tuple and len(fname) > 0:
        fname = fname[0]
    if fname:
        filename = os.path.splitext(fname)[0] + '.hdf5'
    else:
        hdf5_files = glob.glob('*.hdf5')
        if len(hdf5_files) == 0:
            print("ERROR: No hdf5 files in current directory.")
            usage()
        elif len(hdf5_files) != 1:
            print("ERROR: Multiple hdf5 files in current directory.")
            os.system("ls -lt *.hdf5")
            print("Which one do you want to use?\n")
            sys.exit(-1)
        filename = hdf5_files[0]
    try:
        h5 = h5py.File(filename, mode)
    except IOError:
        print("Unknown file: %s" % filename)
        sys.exit(-1)

    try:
        if h5.attrs['MEMOSA_UQ'] != b'MEMOSA':
            print("File '%s' is not a PUQ file." % filename)
            sys.exit(-1)
    except:
        print("File '%s' is not a PUQ file." % filename)
        sys.exit(-1)

    if int(h5.attrs['version']) < 200:
        print("File '%s' is too old to be read with this version of PUQ.\nPlease try an older version." % filename)
        sys.exit(-1)

    return h5, filename


def load_internal(name):
    debug(name)

    try:
        name = name[0]
    except:
        name = ''

    h5, fname = open_hdf5_file(name)

    if 'private' in h5:
        val = h5['private/sweep'].value
    else:
        # backwards compatibility
        val = h5['input/sweep'].value

    if type(val) != str:
        val = val.decode('UTF-8')
    sw = unpickle(val)

    sw.fname = os.path.splitext(fname)[0]
    h5.close()

    sw.psweep._sweep = sw

    if hasattr(sw.psweep, 'reinit'):
        sw.psweep.reinit()
    return sw


def start(*args):
    usage = """Usage: puq start [-f file.hdf5] script.py [args].
    where 'script' is a PUQ control script and
    'args' are optional arguments passed to run() in the control script."""
    parser = OptionParser(usage)
    parser.add_option("-f", type='string',
        help="Output filename. '.hdf5' will be appended if necessary. Default is 'sweep_' followed by a timestamp.")
    (opt, ar) = parser.parse_args(args=list(args))

    if len(ar) == 0:
        parser.print_help()
        sys.exit(-1)

    scriptname = ar[0]

    vprint(2, "Start %s" % scriptname)
    module = os.path.splitext(os.path.split(scriptname)[1])[0]
    sys.path = [os.getcwd()] + sys.path

    try:
        _temp = __import__(module, globals(), locals(), [], 0)
    except ImportError:
        exception("Error importing '%s'" % scriptname)
        return

    sw = _temp.run(*ar[1:])

    if not scriptname.endswith(".py"):
        scriptname += ".py"
    sw.input_script = os.path.abspath(scriptname)

    res = sw.run(opt.f)
    if res:
        sw.analyze()
    return res


def status(*args):
    debug(args)
    if len(args) > 1:
        usage()

    sweep = load_internal(args)
    sweep.host.status()
    return True


def resume(*args):
    debug(args)
    if len(args) > 1:
        usage()

    sweep = load_internal(args)
    sweep.resume()
    return True


# post-process sweep
# sweep analyze id  [foo[.py]]
def analyze(*args):
    debug(args)
    usage = "Usage: puq analyze [options] [hdf5_filename].\nType 'puq analyze -h' for option descriptions."
    parser = OptionParser(usage)
    parser.add_option("-v", action="store_true", default=False, help="Verbose.")
    parser.add_option("--psamples", type='string',
                      help="Filename CSV table of parameter samples.")
    parser.add_option("-r", action="store_true", help="Re-analyze the data.")
    (opt, ar) = parser.parse_args(args=list(args))

    sweep = load_internal(ar)
    h5 = h5py.File(sweep.fname + '.hdf5')
    try:
        uqtype = h5.attrs['UQtype']
    except:
        if 'smolyak' in h5:
            uqtype = 'smolyak'
        elif 'lhs' in h5:
            uqtype = 'lhs'
        elif 'montecarlo' in h5:
            uqtype = 'montecarlo'
        else:
            uqtype = ''
        if uqtype:
            h5.attrs['UQtype'] = uqtype

    num_outputs = 0
    if not opt.r and uqtype and uqtype in h5:
        num_outputs = len(h5[uqtype])

    errors = 0
    if num_outputs == 0:
        if 'output/data' in h5:
            del h5['/output/data']
        errors = sweep.analyze(opt.v)

    if opt.psamples and 'psamples' in h5:
        # FIXME: delete pdfs too!
        # FIXME check that this works.  or do we need it?
        del h5['psamples']
        sd = get_psamples_from_csv(sweep, h5, opt.psamples)
        h5['psamples'] = get_psamples(sweep.psweep.params, psamples=sd)
    h5.close()

    puq.analyzer(sweep, errors)
    return True


def dump(*args):
    debug(args)
    h5, fname = open_hdf5_file(args)
    puq.dump(h5, fname)
    h5.close()
    return True


def plot(*args):
    debug(args)
    usage = "Usage: puq plot [options] hdf5_filename.\n\n\
Examples:\n\
plot                  Plots all output PDFs. This is the default.\n\
plot -k               Plots output PDFs using Gaussian Kernel Density.\n\
plot -l -k            Plots output PDFs using Gaussian KDE and linear interpolation.\n\
plot -v temp          If temp is an output variable, plots its PDF.\n\
plot -v 'v1,v2'       Same as before, except plot v1 and v2.\n\
plot -r               Plot response surface of output variables.\n\
plot -r -v 'v1,v2'    Plots response surface of output variables v1 and v2.\n\
plot -f fmt           Save plots. Valid values for 'fmt' are eps, pdf, png, ps, raw, \n\
                      rgba, svg, and svgz.\n\
plot --psamples f.csv Use parameter samples from csv file to build PDF.\n\
plot -h               Help with additional options.\
"
    parser = OptionParser(usage)
    parser.add_option("-r", action="store_true",
                      help="Response Surface Plot")
    parser.add_option("-v", help='Variable list. \
If multiple, put them in quotes and separate by spaces or commas.')
    parser.add_option("-f", type='string', default='i',
                      help="Format [pdf|ps|png|svg|i] [i]")
    parser.add_option("-l", action="store_true",
                      help="Plot output PDF using linear interpolation from a histogram. [False]")
    parser.add_option("-k", action="store_true",
                      help="Use Gaussian Kernel Density Estimator on output PDFs. [True]")
    parser.add_option("--nogrid", action="store_true",
                      help="Don't show grid")
    parser.add_option("--title", type="string",
                      help="Title. Default is the Test Program description.")
    parser.add_option("--xlabel", type="string",
                      help="Label for the X-axis. Overrides the default which depends on the plot type.")
    parser.add_option("--ylabel", type="string",
                      help="Label for the Y-axis. Overrides the default which depends on the plot type.")
    parser.add_option("--zlabel", type="string",
                      help="Label for the Z-axis. Overrides the default which depends on the plot type.")
    parser.add_option("--fontsize", type="int", help="Normal font size in points.")
    parser.add_option("--using", type='string',
                      help="Filename containing substitute parameter(s).")
    parser.add_option("--psamples", type='string',
                      help="Filename CSV table of parameter samples.")
    (opt, ar) = parser.parse_args(args=list(args))

    if opt.f == 'i':
        if sys.platform == 'darwin':
            matplotlib.use('macosx', warn=False)
        else:
            matplotlib.use('tkagg', warn=False)
    else:
        matplotlib.use('Agg', warn=False)
    import matplotlib.pyplot as plt

    sweep = load_internal(ar)
    h5, fname = open_hdf5_file(sweep.fname + '.hdf5', 'r+')
    params = []
    if opt.using:
        sys.path = [os.getcwd()] + sys.path
        module = os.path.splitext(os.path.split(opt.using)[1])[0]
        _temp = __import__(module, globals(), locals(), [], 0)
        for k, v in _temp.__dict__.iteritems():
            if isinstance(v, puq.Parameter):
                for i, p in enumerate(sweep.psweep.params):
                    if p.name == v.name:
                        params.append(v)

    puq.plot(sweep, h5, opt, params=params)
    if opt.f == 'i':
        try:
            plt.show()
        except KeyboardInterrupt:
            pass

    h5.close()
    return True


def extend(*args):
    debug(args)
    usage = "Usage: sweep extend [--num num] hdf5_filename."
    parser = OptionParser(usage)
    parser.add_option("--num", type='int', default=0)
    (opt, ar) = parser.parse_args(args=list(args))
    sweep = load_internal(ar)
    cname = sweep.psweep.__class__.__name__
    vprint(1, "Extending %s.hdf5 using %s" % (sweep.fname, cname))
    if cname == 'MonteCarlo':
        if opt.num <= 0:
            print("Monte Carlo extend requires a valid num argument.")
            print(usage)
            return
        sweep.psweep.extend(opt.num)
    else:
        sweep.psweep.extend()
    return sweep.run()


def strip(*args):
    debug(args)
    h5, fname = open_hdf5_file(args)
    h5.close()
    puq.util.strip(fname)
    return True


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = OptionParser(__USAGE__)
    parser.disable_interspersed_args()
    parser.add_option("-d", action="store_true", help="Debug")
    parser.add_option("-q", action="store_true", help="Quiet")
    parser.add_option("-v", action="store_true", help="Verbose")
    parser.add_option("-V", "--version", action="store_true", help="Version", dest="V")
    parser.add_option("-k", action="store_true", help="Keep Directories")
    (opt, args) = parser.parse_args(argv[1:])

    if opt.q:
        options['verbose'] -= 1

    if opt.v:
        options['verbose'] += 1

    if opt.k:
        options['keep'] = 1

    if opt.d:
        logging.getLogger().setLevel(logging.DEBUG)

    funcs = {
             "analyze": analyze,
             "start": start,
             "resume": resume,
             "status": status,
             "plot": plot,
             "extend": extend,
             "dump": dump,
             "strip": strip,
             "read": puq.read,
             "monitor": resume,
    }
    if opt.V:
        print(puq.__version__)
        return 0

    if len(args) == 0:
        usage()
    elif args[0] in funcs:
        res = funcs[args[0]](*args[1:])
        if res is True:
            return 0
        else:
            return -1
    else:
        print("ERROR: unknown command '%s'" % args[0])
        usage()
    return -1

if __name__ == '__main__':
    exit_status = main(sys.argv)
    sys.exit(exit_status)
