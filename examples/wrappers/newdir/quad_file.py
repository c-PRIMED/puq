from puq import *

def run():
    p1 = UniformParameter('x', 'x', min=-5, max=5)
    host = InteractiveHost()
    uq = Smolyak([p1], level=2)

    """
    Call the wrapper with a=1, b=2, c=3
    Note the relative path to the wrapper which will be executed
    from a subdirectory (because of the newdir option)

    newdir option to TestProgram() causes each instance of the wrapper
    and simulation it wraps to execute in a separate subdirectory.
    This is required because the simulation and wrapper write files with
    the same name but containing different information on each run.
    """

    prog = TestProgram(desc='Quadratic using bash file wrapper',
                       exe="../sim_file_wrap.sh 1 2 3 $x",
                       newdir=True)
    return Sweep(uq, host, prog)
