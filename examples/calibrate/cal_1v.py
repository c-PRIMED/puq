import puq
import numpy as np
import pylab


def model(x):
    return (x-4)**3

# measurement error for data
sigma = 0.1

real_x = puq.NormalParameter('x', 'x', mean=5, dev=0.1)

num_samples = 25
x_data = real_x.pdf.ds(num_samples)
x_data.sort()
z_data = model(x_data)
z_data_noisy = z_data + sigma * np.random.randn(len(z_data))
#nplot(x_data, .001, z_data, sigma)
real_x.pdf.plot(color='b')

# prior for x
x = puq.UniformParameter('x', 'x', min=1, max=10)

# do calibration
calibrated = puq.calibrate([x], z_data_noisy, sigma, model)
print calibrated[0]
calibrated[0].pdf.plot(color='r')
pylab.show()

