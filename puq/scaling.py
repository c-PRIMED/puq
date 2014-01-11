"""
CPU Scaling Sweeps
"""

# FIXME: broken

import numpy as np

class Scaling():
    def __init__(self, params):
        self.params = [params]
        self.results = []

    def get_args(self):
        for cpus in self.params[0].values:
            yield [(self.params[0].name, cpus)]

    def analyze(self, hf, outdesc):
        import matplotlib
        matplotlib.use('PDF')
        import matplotlib.pyplot as plt
        
        results = hf['run/time']
        plt.xlabel('Processors')
        plt.ylabel('Time')
        plt.title('Scalability')
        plt.plot(self.params[0].values, results)
        plt.savefig('scale.pdf')
        return results
