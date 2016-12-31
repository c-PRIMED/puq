from puq import *
import numpy as np

def model_0(x, y):
    return x*x + 0.75 * y*y + 2*y + x*y - 7

def run():

    # create some "experimental" data
    real_x = NormalPDF(5, .2)
    real_y = NormalPDF(3.4, .25)
    sigma = 0.5
    num_samples = 5
    x_data = np.linspace(*real_x.range, num=num_samples)
    y_data = real_y.random(num_samples)
    z_data = model_0(x_data, y_data)
    z_data_noisy = z_data + sigma * np.random.randn(len(z_data))

    # Create parameters. Pass experimental input data to
    # non-calibration parameters.
    x = NormalParameter('x', 'x', mean=5, dev=.2, caldata=x_data)
    y = UniformParameter('y', 'y', min=1, max=5)

    # set up host, uq and prog normally
    host = InteractiveHost()
    prog = TestProgram('python model_0.py', desc='model_0 calibration')
    uq = Smolyak([x, y], level=2)

    # pass experimental results to Sweep
    return Sweep(uq, host, prog, caldata=z_data_noisy, calerr=sigma)

