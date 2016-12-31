from puq import *
import numpy as np

def model_1(x, y, z):
    return x*x + 0.75 * y*y + 2*y + x*y - 7*z + 2

def run():

    # create some "experimental" data
    real_x = NormalPDF(5, .2)
    real_y = NormalPDF(3.4, .25)
    real_z = NormalPDF(12, .2)
    sigma = 0.1
    num_samples = 100
    x_data = real_x.random(num_samples)
    y_data = real_y.random(num_samples)
    z_data = real_z.random(num_samples)
    f_data = model_1(x_data, y_data, z_data)
    f_data_noisy = f_data + sigma * np.random.randn(len(f_data))

    # Create parameters. Pass experimental input data to
    # non-calibration parameters.
    x = NormalParameter('x', 'x', mean=5, dev=.2, caldata=x_data)
    y = UniformParameter('y', 'y', min=1, max=5)
    z = NormalParameter('z', 'z', mean=5, dev=.2, caldata=z_data)

    # set up host, uq and prog normally
    host = InteractiveHost()
    uq = Smolyak([x,y,z], level=2)
    prog = TestProgram('python model_1.py', desc='model_1 calibration')

    # pass experimental results to Sweep
    return Sweep(uq, host, prog, caldata=f_data_noisy, calerr=sigma)

