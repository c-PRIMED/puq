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
        'format' : 'i',
        },
    'pdf':
        {
        'numpart': 100,
        'range': 0.9999,
        'srange': 0.998,
        },
    }

import sys
if sys.platform == 'darwin':
    options['plot']['iformat'] = 'macosx'
else:
    options['plot']['iformat'] = 'tkagg'
