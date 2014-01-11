from scipy import vectorize
from scipy.integrate import quad
import numpy as np

def rosen(x, y):
    return 100*(y-x**2)**2 + (1-x)**2
    
def irosen(i):
    return quad(rosen, -2, 2, args=(i))[0]

vrosen = vectorize(irosen)

print quad(vrosen, -2, 2)[0]/16
# OUT: 455.66666666666669

for i in np.logspace(1, 20, num=20, base=2):
    a = np.linspace(-2,2,i)
    print "%8d %s" % (i, np.sum(rosen(a,a))/len(a))

# do smolyak with 2 uniform [-2,2] parameters
# find the mean and std dev
