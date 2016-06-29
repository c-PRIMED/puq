import puq
import numpy as np

def model(x, y, z):
    return x**2 + 0.75 * y**2 + 2*y + x*y - 7*z + 2

# experimental data for z=Normal(12,1)
exp_x = np.array([ 5.29,  4.96,  5.3 ,  5.18,  4.93,  5.11,  4.98,  4.81,  5.27,
        4.69,  5.06,  4.99,  4.87,  5.04,  5.15])
exp_y = np.array([ 3.51,  3.34,  3.45,  3.26,  3.45,  3.5 ,  3.37,  3.45,  3.42,
        3.4 ,  3.2 ,  3.24,  3.39,  3.35,  3.4 ])
exp_data = np.array([-18.28, -24.23, -24.5 , -24.13, -25.36, -17.2 , -16.5 , -24.87,
       -16.25, -26.51, -12.3 , -15.91, -27.96, -27.98, -34.41])

# measurement error for exp_data
sigma = 0.1

# Create parameters. Pass experimental input data to
# non-calibration parameters.
x = puq.NormalParameter('x', 'x', mean=5, dev=0.2, caldata=exp_x)
y = puq.NormalParameter('y', 'y', mean=3.4, dev=0.1, caldata=exp_y)
z = puq.UniformParameter('z', 'z', min=5, max=20, caltype='S')

[x, y, calibrated_z], kpdf = puq.calibrate([x, y, z], exp_data, sigma, model)

print "Calibrated z is", calibrated_z

