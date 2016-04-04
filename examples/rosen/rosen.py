from puq import *


def run(level=2):

    # Declare our parameters here. Both are uniform on [-2, 2]
    p1 = UniformParameter('x', 'x', min=-2, max=2)
    p2 = UniformParameter('y', 'y', min=-2, max=2)

    # Create a host
    host = InteractiveHost()

    # Example pbshost
    # This says each process uses 1 cpu and there are 8 cpus in a node.
    # So 8 processes will run at once. the "pack=" parameter tells it to
    # repeat this 8 times in a PBS job, so up to 8x8=64 jobs will run
    # as a single PBS job. Be sure to set walltime accordingly.
    #
    #host = PBSHost(env='/scratch/prism/mmh/memosa/env-hansen.sh', cpus=1, cpus_per_node=8, walltime='2:00', pack=8)

    # Declare a UQ method.
    uq = Smolyak([p1, p2], level=level)

    # Our test program
    prog = TestProgram(exe='python rosen_prog.py --x=$x --y=$y',
      desc='Rosenbrock Function')

    return Sweep(uq, host, prog)
