import puq
import numpy as np


# Calibration example/test case
# Calibrate one parameter of a two parameter model

# QoI is 0.2.  There is a known variable with a
# measurement error of .05

def model(x, y):
    return y**2 + 17*x


# The actual values of our parameters
real_y = puq.NormalParameter('y', 'y', mean=5, dev=0.1)
real_x = 0.2

# take some samples, run them through the model
# and add some noise
num_samples = 50
y_data = real_y.pdf.random(num_samples)
y_err = np.ones(len(y_data)) * 0.1  # [0.1, 0.1, 0.1,...]
y_data_noisy = y_data + y_err * np.random.randn(len(y_data))  # simulated noise
y_caldata = np.column_stack((y_data_noisy, y_err))

z_data = model(real_x, y_data)
z_err = np.ones(len(z_data))
z_data_noisy = z_data + z_err * np.random.randn(len(z_data))  # simulated noise

# prior for x. Caltype is 'D' because x is not a stochastic.
x = puq.UniformParameter('x', 'x', min=0, max=10, caltype='D')

# PDF and data for y
y = puq.NormalParameter('y', 'y', mean=5, dev=0.1, caldata=y_caldata)

[calibrated_x, y], kpdf = puq.calibrate([x, y], z_data_noisy, z_err, model)

print(calibrated_x)
