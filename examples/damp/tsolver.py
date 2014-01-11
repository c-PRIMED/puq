#!/usr/bin/env python
"""
Example solver program. This can be run by itself or used
with the 'sweep' program.

Usage: tsolver.py [-v]
"""
import optparse, sys
import numpy as np

# for option parsing, add a method to check for required options
class OptionParser (optparse.OptionParser):
    def check_required (self, opt_list):
        for opt in opt_list:
            option = self.get_option(opt)
            # Assumes the option's 'default' is set to None!
            if getattr(self.values, option.dest) is None:
                self.error("%s option required but not supplied" % option)

usage = "usage: %prog --t t --freq f"
parser = OptionParser(usage)
parser.add_option("--t", type=float)
parser.add_option("--freq", type=float)
(options, args) = parser.parse_args()
parser.check_required(['--t', '--freq'])

#print "Solving for t=%f and freq=%f" % (options.t, options.freq)

# The rest of this would be where the normal solver code goes.
# But this test code just feeds back the precomputed results.
# This is useful for testing because a real run takes too long.

"""
The wrong results from matlab example
damp_results = np.array([
[1.00, 133862.0, 5.23],
[0.55, 133862.0, 8.82],
[1.45, 133862.0, 3.22],
[1.00, 113782.7, 4.74],
[1.00, 153941.3, 4.68],
[0.681802, 133862.0, 7.06],
[1.318198, 133862.0, 3.55],
[0.55, 113782.7, 9.74],
[1.45, 113782.7, 3.55],
[0.55, 153941.3, 8.12],
[1.45, 153941.3, 2.96],
[1.00, 119663.790809, 5.07],
[1.00, 148060.209191, 4.46]])
"""

damp_results = np.array([
[1.00, 133862.0, 4.74],
[0.55, 133862.0, 8.82],
[1.45, 133862.0, 3.22],
[1.00, 113782.7, 5.23],
[1.00, 153941.3, 4.68],
[0.681802, 133862.0, 7.06],
[1.318198, 133862.0, 3.55],
[0.55, 113782.7, 9.74],
[1.45, 113782.7, 3.55],
[0.55, 153941.3, 8.12],
[1.45, 153941.3, 2.96],
[1.00, 119663.790809, 5.07],
[1.00, 148060.209191, 4.46]])

#import time
#time.sleep(5)
from puqutil import dump_hdf5

for a,b,damp in damp_results:
    if np.allclose(a,options.t, atol=1e-3) and np.allclose(b, options.freq, atol=1e-3):
        dump_hdf5('damp', damp*1.0e-3, "Damping Coefficient")
        break

