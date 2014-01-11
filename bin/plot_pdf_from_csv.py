#!/usr/bin/env python
"""
%prog [-b] filename[.csv]
Options:
   -b   Number of BINS for the histogram.

Plots csv dumps of PDF data like that dumped by pdftool.
If filename_raw.csv exists it will also print a normalized histogram.
"""

import numpy as np
import sys

import matplotlib
if sys.platform == 'darwin':
    matplotlib.use('macosx')
else:
    matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

if __name__ == '__main__':
    import optparse
    parser = optparse.OptionParser(__doc__)
    parser.add_option("-b", type=int, default=0)
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_usage()
        sys.exit(0)

    filename = args[0]
    nbins = options.b

    if not filename.endswith('.csv'):
        filename += '.csv'
    extension = filename.split('.')[-1]
    raw_filename = ''.join(filename.split('.')[:-1]) + '_raw.' + extension
    
    f = open(filename, 'r').readlines()
    pdf = np.empty((len(f),2))
    for i, line in enumerate(f):
        pdf[i] = map(float,line.split(','))

    try:
        f = open(raw_filename, 'r').readlines()
        data = np.array(map(float,f))
    except:
        data = None


    if data != None:
        while nbins <=1:
            try:
                nbins = input('Number of bins: ')
                nbins = int(nbins)
            except KeyboardInterrupt:
                print
                break
            except:
                nbins=0
        if nbins >= 1:
            plt.hist(data, nbins, normed=1, facecolor='blue', alpha=0.3)

    plt.plot(pdf[:,0], pdf[:,1], 'red', linewidth=2)
    plt.show()
