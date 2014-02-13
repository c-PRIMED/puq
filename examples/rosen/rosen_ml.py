from puq import *

def run(lev=4):
    # Declare our parameters here. Both are uniform on [-2, 2]
    p1 = UniformParameter('x', 'x', min=-2, max=2)
    p2 = UniformParameter('y', 'y', min=-2, max=2)

    # Create a host
    host = InteractiveHost()

    # Declare a UQ method.
    uq = Smolyak([p1, p2], level=lev)

    prog = TestProgram(
      exe="octave -q --eval 'rosen($x, $y)'",
      # exe="matlab -nodisplay -r 'rosen($x, $y);quit()'",
      desc='Rosenbrock Function (octave)')

    return Sweep(uq, host, prog)
