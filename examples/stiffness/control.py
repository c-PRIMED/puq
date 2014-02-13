from puq import *

def run():
    # Young's Modulus in MPa
    E = UniformParameter('e', 'Youngs Modulus', min=180e3, max=220e3)

    # residual stress in Mpa. Actual is not Uniform, but this is OK
    # for a response surface.
    sigma = UniformParameter('sigma', 'Residual Stress', min=15, max=40)

    b = UniformParameter('b', 'Beam Width', min=.119, max=.121)

    # 400 um
    #L = UniformParameter('L', 'Beam Length', min = .390, max = .395)
    #h = Parameter('h', 'Beam Thickness', pdf=NetPDF('http://dash.prism.nanohub.org:8081/prism/default/get/gen/thickness/3'))

    # 500 um
    L = UniformParameter('L', 'Beam Length', min=.490, max=.495)
    h = Parameter('h', 'Beam Thickness', pdf=NetPDF('http://dash.prism.nanohub.org:8081/prism/default/get/gen/thickness/4'))

    # center
    #eta = 0

    # center of the edge
    # eta = b/2/L
    # 400 um
    # eta = .120 / 2.0 / .391 = .15345
    # 500 um
    #eta = .120 / 2.0 / .492 = .12195

    #xi = 0.5

    # set poisson's ratio to 0.3
    nu = 0.3

    # Create a host
    host = InteractiveHost()

    # Declare a UQ method.
    uq = Smolyak([E, sigma, L, b, h], level=1)

    # Our test program. Make sure %1 corresponds to the first parameter
    # in the list passed to Smolyak() above
    prog = TestProgram(desc='fixed beam stiffness',
        exe="octave -q --eval 'stiffness($e, 0.3, $sigma, $L, $b, $h, 0.5, 0)'")

    return Sweep(uq, host, prog)
