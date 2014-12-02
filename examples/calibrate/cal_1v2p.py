import puq
import numpy as np


# Calibration example/test case
# QoI is 0.2.  There is a known variable with a
# measurement error of .05

def model(x, y):
    return y**2 + 17*x

# measurement error for exp_data
sigma = 0.1


real_y = puq.NormalParameter('y', 'y', mean=5, dev=0.1)
real_x = 0.2

num_samples = 25
y_data = real_y.pdf.random(num_samples)
x_data = np.ones(num_samples)*real_x
z_data = model(x_data, y_data)
z_data_noisy = z_data + sigma * np.random.randn(len(z_data))

# measurement error for y
y_err = .05

# prior for x. Caltype is 'D' because x is not a stochastic.
x = puq.UniformParameter('x', 'x', min=0, max=1, caltype='D')

# PDF and data for y
y = puq.NormalParameter('y', 'y', mean=5, dev=0.1, caldata=y_data)

calibrated_x, y = puq.calibrate([x, y], z_data_noisy, sigma, model)

print calibrated_x
