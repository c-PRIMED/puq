#!/usr/bin/env python
"""
Example of using a UQ method with a sweep.

Usage: test1.py
"""
from puq import *

"""
You can do mpi like this
host = InteractiveHost(cpus=6)
prog = TestProgram('zeta', desc='zeta function',
                       exe="mpirun -np 6 ./zeta -n %1")

What about PBS?
PBSHost(cpus = 8,...
prog = TestProgram('zeta', desc='zeta function',
                       exe="mpirun -np 8 ./zeta -n %1")
"""

def run():
    x = Parameter('x', 'X', mean=5, dev=1)
    host = InteractiveHost(cpus=2, cpus_per_node=2)
    #host = PBSHost(env='/scratch/prism/memosa/env.sh', cpus=8, cpus_per_node=8, walltime='2:00')

    uq = Smolyak([x], 3)
    prog = TestProgram('zeta', desc='zeta function',
                       exe="mpirun -np 2 ./zeta -n %1")
    return Sweep(uq, host, prog)
