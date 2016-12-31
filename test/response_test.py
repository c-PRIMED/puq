from __future__ import absolute_import, division, print_function
import numpy as np
from puq import *

def test_rf_simp_0():
    rf = ResponseFunc('0', vars=(('x',(-20,10)),('y',(-15,5)),('z',(20,22))))
    assert str(rf.simplify()) == '0'

def test_rf_simp_x():
    rf = ResponseFunc('x', vars=(('x',(-20,10)),('y',(-15,5)),('z',(20,22))))
    assert str(rf.simplify()) == 'x'

def test_rf_simp_2x():
    rf = ResponseFunc('2*x',vars=(('x',(-20,10)),('y',(-15,5)),('z',(20,22))))
    assert str(rf.simplify()) == '2*x'

def test_rf_simp_x2():
    rf = ResponseFunc('x*x', vars=(('x',(-20,10)),('y',(-15,5)),('z',(20,22))))
    assert str(rf.simplify()) == 'x**2'

def test_rf_simp_3():
    rf = ResponseFunc('x*x', vars=[('x',(-1,1))])
    assert str(rf.simplify()) == 'x**2'

def test_rf_simp_xy():
    rf = ResponseFunc('x+y', vars=[('x',(-1,1)), ('y', (-1000, 1000)) ])
    assert str(rf.simplify()) == 'y + x' or str(rf.simplify()) == 'x + y'
    assert str(rf.simplify(1e-2)) == 'y'

def test_rf_simp_xy0():
    rf = ResponseFunc('x+y',vars=[('x',(0,0)), ('y', (-1000, 1000)) ])
    s = str(rf.simplify())
    assert s == 'y' or s == '1.0*y'

def test_rf_simp_4():
    rf = ResponseFunc('1 + 2*x +y**2 + 7*x*z**2',vars=[('x',(-20,10)),('y',(-15,5)),('z',(20,22))])

    s = str(rf.simplify(1e-3))
    assert s == 'y**2 + 7*x*z**2' or s == '7*x*z**2 + y**2' or s == '7.0*x*z**2 + 1.0*y**2'

    s = str(rf.simplify(1e-4))
    assert s == '2*x + y**2 + 7*x*z**2' or s == '7*x*z**2 + 2*x + y**2' or s == '7.0*x*z**2 + 2.0*x + 1.0*y**2'

    s = str(rf.simplify())
    assert  s == '1 + 2*x + y**2 + 7*x*z**2' or s == '7*x*z**2 + 2*x + y**2 + 1' or s == '7.0*x*z**2 + 2.0*x + 1.0*y**2 + 1.0'

def test_rf_trunc():
    rf = ResponseFunc('1.00009 + 2*x +y**2 + 2/3*x*z**2',vars=[('x',(-20,10)),('y',(-15,5)),('z',(20,22))])
    s = str(rf.trunc(2))
    assert s == '0.67*x*z**2 + 2.0*x + 1.0*y**2 + 1.0' or s == '0.67*x*z**2 + 2.0*x + 1.0*y**2 + 1.0'
    s = str(rf.trunc(4))
    assert s == '0.6667*x*z**2 + 2.0*x + 1.0*y**2 + 1.0' or s == '0.6667*x*z**2 + 2.0*x + 1.0*y**2 + 1.0'
    s = str(rf.trunc(6))
    assert s == '0.666667*x*z**2 + 2.0*x + 1.0*y**2 + 1.00009' or s == '0.666667*x*z**2 + 2.0*x + 1.0*y**2 + 1.00009'
    s = str(rf.trunc(8))
    assert s == '0.66666667*x*z**2 + 2.0*x + 1.0*y**2 + 1.00009' or s == '0.66666663*x*z**2 + 2.0*x + 1.0*y**2 + 1.0000899'

def test_rf_simp_4_params():
    x = UniformParameter('x', 'first variable', min=-20, max=10)
    y = UniformParameter('y', 'second variable', min=-15, max=5)
    z = UniformParameter('z', 'third variable', min=20, max=22)

    rf = ResponseFunc('1 + 2*x +y**2 + 7*x*z**2', params=[x,y,z])
    pdf, samples = rf.pdf(return_samples=True)
    s = str(rf.simplify(1e-3))
    assert  s == 'y**2 + 7*x*z**2' or s == '7*x*z**2 + y**2' or s == '7.0*x*z**2 + 1.0*y**2'
    s = str(rf.simplify(1e-4))
    assert  s == '2*x + y**2 + 7*x*z**2' or s == '7*x*z**2 + 2*x + y**2' or s == '7.0*x*z**2 + 2.0*x + 1.0*y**2'
    s = str(rf.simplify())
    assert  s == '1 + 2*x + y**2 + 7*x*z**2' or s == '7*x*z**2 + 2*x + y**2 + 1' or s == '7.0*x*z**2 + 2.0*x + 1.0*y**2 + 1.0'


def test_rf_bad0():
    ok = False
    try:
        rf = ResponseFunc()
    except TypeError:
        ok = True
    except:
        assert False, 'Wrong Exception'
    if not ok:
        assert False, 'No Exception when one was expected'


def test_rf_bad1():
    ok = False
    try:
        rf = ResponseFunc('x')
    except ValueError:
        ok = True
    except:
        assert False, 'Wrong Exception'
    if not ok:
        assert False, 'No Exception when one was expected'

def test_rf_bad2():
    ok = False
    try:
        rf = ResponseFunc(vars=[('x', (0,2))])
    except TypeError:
        ok = True
    except:
        assert False, 'Wrong Exception'
    if not ok:
        assert False, 'No Exception when one was expected'

def test_sf_bad0():
    ok = False
    try:
        rf = SampledFunc()
    except ValueError:
        ok = True
    except:
        assert False, 'Wrong Exception'
    if not ok:
        assert False, 'No Exception when one was expected'


def test_sf_bad1():
    ok = False
    try:
        rf = SampledFunc([1,2,3])
    except ValueError:
        ok = True
    except:
        assert False, 'Wrong Exception'
    if not ok:
        assert False, 'No Exception when one was expected'

def test_sf_bad2():
    ok = False
    try:
        rf = SampledFunc(vars=[('x', (0,2))])
    except ValueError:
        ok = True
    except:
        assert False, 'Wrong Exception'
    if not ok:
        assert False, 'No Exception when one was expected'

def test_rf_eval0():
    rf = ResponseFunc('x*x+y', vars=(('x',(0,100)),('y',(0,100))))
    assert np.all(rf.eval(np.array([4]), np.array([5])) == [21.0])
    assert np.all(rf.eval(np.array([1,4,8]), np.array([2,5,9])) == [3.0, 21.0, 73.0])

def test_sf_eval0():
    pts = np.array([[0,0,1],[10,10,1],[100,100,1],[50,50,1],[100,50,1],[50,100,1],[50,0,1],[0,50,1]])
    sf = SampledFunc(pts[:,0], pts[:,1], pts[:,2], vars=(('x',(0,100)),('y',(0,100))))
    assert np.allclose(sf.eval(pts[:,0], pts[:,1]), pts[:,2].astype('float64'), rtol=1e-6)

def test_sf_eval1():
    x = np.array([0,0,5,5,5,10,10])
    y = np.array([0,10,0,5,10,0,10])
    z = np.array([0,0,5,10,5,10,10])
    sf = SampledFunc(x,y,z, vars=(('x',(0,100)),('y',(0,100))))
    assert np.allclose(sf.eval(np.array([5]), np.array([5])), [10.], rtol=1e-6)

    assert np.allclose(sf.eval(np.array([0,5,0]), np.array([0,0,10])), [0.,5,0.], atol=.01)
    assert np.allclose(sf.eval(np.array([3,3,3]), np.array([0,5,10])), [2.88,7.45,2.88], rtol=.1)
    assert np.allclose(sf.eval(np.array([7,7,7]), np.array([0,5,10])), [7.18,11.95,7.18], rtol=.1)
    # same again, using broadcasting
    assert np.allclose(sf.eval(np.array([0]), np.array([0,10])), [0., 0.], atol=.1)
    assert np.allclose(sf.eval(np.array([3]), np.array([0,5,10])), [2.88,7.45,2.88], rtol=.1)
    assert np.allclose(sf.eval(np.array([7]), np.array([0,5,10])), [7.18,11.95,7.18], rtol=.1)

def test_rf_pdf0():
    print("TEST_RF_PDF")
    x = UniformParameter('x', 'first variable', min=-20, max=10)
    y = UniformParameter('y', 'second variable', min=-15, max=5)
    z = UniformParameter('z', 'third variable', min=20, max=22)

    rf = ResponseFunc('1 + 2*x +y**2 + 7*x*z**2', params=[x,y,z])
    mean1 = rf.pdf().mean

    x = UniformParameter('x', 'first variable', min=0, max=10)
    mean2 = rf.pdf(params=[x]).mean

    rf = ResponseFunc('1 + 2*x +y**2 + 7*x*z**2', params=[x,y,z])
    mean3 = rf.pdf().mean

    assert not np.allclose(mean1, mean2, rtol=1e-2)
    assert np.allclose(mean3, mean2, rtol=1e-2)

def test_rf_pdf1():
    print("TEST_RF_PDF1")
    x = UniformParameter('x', 'first variable', min=-20, max=10)
    y = UniformParameter('y', 'second variable', min=-15, max=5)
    z = UniformParameter('z', 'third variable', min=20, max=22)

    rf = ResponseFunc('1 + 2*x +y**2 + 7*x*z**2', params=[x,y,z])
    mean1 = rf.pdf().mean

    x = UniformParameter('x', 'first variable', min=0, max=10)
    y = UniformParameter('y', 'second variable', min=-15, max=0)
    z = UniformParameter('z', 'third variable', min=20, max=21)

    mean2 = rf.pdf(params=[x,y,z]).mean

    rf = ResponseFunc('1 + 2*x +y**2 + 7*x*z**2', params=[x,y,z])
    mean3 = rf.pdf().mean

    assert not np.allclose(mean1, mean2, rtol=1e-2)
    assert np.allclose(mean3, mean2, rtol=1e-2)

def test_rf_pdf2():
    print("TEST_RF_PDF2")
    x = UniformParameter('x', 'first variable', min=-20, max=10)
    y = UniformParameter('y', 'second variable', min=-15, max=5)
    z = UniformParameter('z', 'third variable', min=20, max=22)

    rf = ResponseFunc('1 + 2*x +y**2 + 7*x*z**2', params=[x,y,z])
    mean1 = rf.pdf().mean

    ok = False
    x = UniformParameter('x', 'first variable', min=0, max=11)
    try:
        mean2 = rf.pdf(params=[x]).mean
    except ValueError:
        ok = True
    assert ok

    mean2 = rf.pdf(params=[x], force=True).mean

    rf = ResponseFunc('1 + 2*x +y**2 + 7*x*z**2', params=[x,y,z])
    mean3 = rf.pdf().mean

    assert not np.allclose(mean1, mean2, rtol=1e-2)
    assert np.allclose(mean3, mean2, rtol=1e-2)

# ========= REPEAT SOME TESTS WITH JSONPICKLE ===========

def test_rf_simp_0_P():
    rf = ResponseFunc('0', vars=(('x',(-20,10)),('y',(-15,5)),('z',(20,22))))
    rf = unpickle(pickle(rf))
    assert str(rf.simplify()) == '0'

def test_rf_simp_4_P():
    rf = ResponseFunc('1 + 2*x +y**2 + 7*x*z**2',vars=[('x',(np.int64(-20),10)),('y',(-15,5)),('z',(20,22))])
    rf = unpickle(pickle(rf))

    s = str(rf.simplify(1e-3))
    assert s == 'y**2 + 7*x*z**2' or s == '7*x*z**2 + y**2' or s == '7.0*x*z**2 + 1.0*y**2'

    s = str(rf.simplify(1e-4))
    assert s == '2*x + y**2 + 7*x*z**2' or s == '7*x*z**2 + 2*x + y**2' or s == '7.0*x*z**2 + 2.0*x + 1.0*y**2'

    s = str(rf.simplify())
    assert  s == '1 + 2*x + y**2 + 7*x*z**2' or s == '7*x*z**2 + 2*x + y**2 + 1' or s == '7.0*x*z**2 + 2.0*x + 1.0*y**2 + 1.0'

def test_rf_simp_4_params_P():
    x = UniformParameter('x', 'first variable', min=-20, max=10)
    y = UniformParameter('y', 'second variable', min=-15, max=5)
    z = UniformParameter('z', 'third variable', min=20, max=22)

    rf = ResponseFunc('1 + 2*x +y**2 + 7*x*z**2', params=[x,y,z])
    rf = unpickle(pickle(rf))

    s = str(rf.simplify(1e-3))
    assert  s == 'y**2 + 7*x*z**2' or s == '7*x*z**2 + y**2' or s == '7.0*x*z**2 + 1.0*y**2'
    s = str(rf.simplify(1e-4))
    assert  s == '2*x + y**2 + 7*x*z**2' or s == '7*x*z**2 + 2*x + y**2' or s == '7.0*x*z**2 + 2.0*x + 1.0*y**2'
    s = str(rf.simplify())
    assert  s == '1 + 2*x + y**2 + 7*x*z**2' or s == '7*x*z**2 + 2*x + y**2 + 1' or s == '7.0*x*z**2 + 2.0*x + 1.0*y**2 + 1.0'

def test_rf_eval0_P():
    rf = ResponseFunc('x*x+y', vars=(('x',(0,100)),('y',(0,100))))
    rf = unpickle(pickle(rf))
    assert np.all(rf.eval(np.array([4]), np.array([5])) == [21.0])
    assert np.all(rf.eval(np.array([1,4,8]), np.array([2,5,9])) == [3.0, 21.0, 73.0])

def test_sf_eval0_P():
    pts = np.array([[0,0,1],[10,10,1],[100,100,1],[50,50,1],[100,50,1],[50,100,1],[50,0,1],[0,50,1]])
    sf = SampledFunc(pts[:,0], pts[:,1], pts[:,2], vars=(('x',(0,100)),('y',(0,100))))
    sf = unpickle(pickle(sf))
    assert np.allclose(sf.eval(pts[:,0], pts[:,1]), pts[:,2].astype('float64'), rtol=1e-6)

def test_sf_eval1_P():
    x = np.array([0,0,5,5,5,10,10])
    y = np.array([0,10,0,5,10,0,10])
    z = np.array([0,0,5,10,5,10,10])
    sf = SampledFunc(x,y,z, vars=(('x',(0,100)),('y',(0,100))))
    sf = unpickle(pickle(sf))
    assert np.allclose(sf.eval(np.array([0]), np.array([0,10])), [0.,0.], atol=.01)
    assert np.allclose(sf.eval(np.array([3]), np.array([0,5,10])), [2.88,7.45,2.88], rtol=.1)
    assert np.allclose(sf.eval(np.array([7]), np.array([0,5,10])), [7.18,11.95,7.18], rtol=.1)

if __name__ == "__main__":
    test_sf_eval1()
    test_sf_eval1_P()