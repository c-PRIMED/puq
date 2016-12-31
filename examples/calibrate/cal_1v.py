import puq
import numpy as np
import pylab


def model(x):
    return (x-4)**3

# our real value of x
real_x = puq.NormalParameter('x', 'x', mean=5, dev=0.1)

# We take 25 samples of x
num_samples = 25
x_data = real_x.pdf.lhs(num_samples)
x_data.sort()  # sort for easier plotting

# compute z using our x samples
z_data = model(x_data)

# add some 'measurement' noise
sigma = 0.1
z_data_noisy = z_data + sigma * np.random.randn(len(z_data))

# prior for x. All we assume is x is between 2 and 25
# caltype is 'S' because we want to calibrate
# mean and deviation of x
x = puq.UniformParameter('x', 'x', min=2, max=25, caltype='S')

# do calibration
[calibrated], kpdf = puq.calibrate([x], z_data_noisy, sigma, model)
print(calibrated)

# plot actual and calibrated
real_x.pdf.plot(color='b')
calibrated.pdf.plot(color='r')
pylab.show()

