from puq import UniformParameter, Smolyak, TestProgram, Sweep, InteractiveHost

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

    The 'outfiles' option causes puq to save the listed files in the HDF5 file.
    It is not necessary for this example to run.
    """

    prog = TestProgram(desc='Quadratic using python file wrapper',
                       exe="../sim_file_wrap.py 1 2 3 $x",
                       newdir=True,
                       infiles=['input.txt'],
                       outfiles=['output.txt'])
    return Sweep(uq, host, prog)
