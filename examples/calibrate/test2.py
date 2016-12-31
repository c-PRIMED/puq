import puq
import numpy as np

def run():

    # experimental data for z=Normal(12,2)
    exp_x =np.array([5.04,  5.14,  4.78,  5.12,  5.11,  5.13,  4.97,  5.1 ,  5.53,  5.09])
    exp_y = np.array([3.33,  3.56,  2.94,  3.27,  3.54,  3.4 ,  3.52,  3.63,  3.45,  3.19])
    exp_data = np.array([-26.16, -18.39, -20.57, -45.24, -29.16, -22., -46.47,  -3.15, -10.48, -16.88])

    # measurement error
    sigma = 0.1

    # Create parameters. Pass experimental input data to
    # non-calibration parameters.
    x = puq.NormalParameter('x', 'x', mean=5, dev=0.2, caldata=exp_x)
    y = puq.NormalParameter('y', 'y', mean=3.4, dev=0.25, caldata=exp_y)
    z = puq.UniformParameter('z', 'z', min=5, max=20)

    # set up host, uq and prog normally
    host = puq.InteractiveHost()
    uq = puq.Smolyak([x,y,z], level=2)
    prog = puq.TestProgram('python model_1.py', desc='model_1 calibration')

    # pass experimental results to Sweep
    return puq.Sweep(uq, host, prog, caldata=exp_data, calerr=sigma)
