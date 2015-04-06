"""
Options database for the UQ framework.

This is a global database of parameters that control internal details
of operations like plotting.
"""

options = {
    'verbose': 1,
    'keep': 0,
    'plot':
        {
            'format': 'i',
        },
    'pdf':
        {
            # number of sample points in PDF
            'numpart': 100,

            # range to use for building response
            'range': 0.999,

            # range to use for printing
            'srange': 0.995,
        },
    }

import sys
if sys.platform == 'darwin':
    options['plot']['iformat'] = 'macosx'
else:
    options['plot']['iformat'] = 'tkagg'
