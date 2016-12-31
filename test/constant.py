import numpy as np
from puq import *

x = UniformParameter('x', 'first variable', min=0, max=10)
y = UniformParameter('y', 'second variable', min=-100, max=-50)
z = UniformParameter('z', 'third variable', min=20, max=22)

def test1():
    rf = ResponseFunc('0', params=[x])
    pdf = rf.pdf()
    assert pdf.dev == 0.0
    assert pdf.mean == 0.0
    assert pdf.range == (0.0, 0.0)
    assert np.all(pdf.lhs(10) == np.array([0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]))


def test2():
    rf = ResponseFunc('0', params=[x, y])
    pdf = rf.pdf()
    assert pdf.dev == 0.0
    assert pdf.mean == 0.0
    assert pdf.range == (0.0, 0.0)
    assert np.all(pdf.lhs(10) == np.array([0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]))


def test3():
    rf = ResponseFunc('42', params=[x])
    pdf = rf.pdf()
    assert pdf.dev == 0.0
    assert pdf.mean == 42.0
    assert pdf.range == (42.0, 42.0)
    assert np.all(pdf.lhs(10) == np.ones(10)*42.0)


def test4():
    # response function where one variable is constant
    rf = ResponseFunc('x', params=[x, y])
    assert rf.eval([1, 2, 3], [7, 8, 9]) == [1, 2, 3]
    pdf = rf.pdf()
    assert np.allclose(pdf.dev, 2.79346042119, rtol=1e-4)
    assert np.allclose(pdf.mean, 5.0)
    ok = np.array([0.64810732773017177, 1.6282691967777745, 2.5916374123046322, 3.5549824478537291, 4.5183274826179138, 5.4816725173820959, 6.4450175521462754, 7.4083625876953683, 8.3717308032222224, 9.351892672269825])
    assert np.allclose(sorted(pdf.ds(10)), ok, rtol=1e-3)


def test5():
    d = np.array([1.23456789, 1.23456789, 1.23456789, 1.23456789, 1.23456789])
    pdf = ExperimentalPDF(data=d, fit=True)
    assert pdf.dev == 0.0
    assert pdf.mean == 1.23456789
    assert pdf.range == (pdf.mean, pdf.mean)
    assert np.all(pdf.lhs(10) == np.ones(10)*pdf.mean)


def test6():
    # Constant PDF, not fit with LDE
    d = np.array([1.23456789, 1.23456789, 1.23456789, 1.23456789, 1.23456789])
    pdf = ExperimentalPDF(data=d, fit=False)
    assert pdf.dev == 0.0
    assert pdf.mean == 1.23456789
    assert pdf.range == (pdf.mean, pdf.mean)
    assert np.all(pdf.lhs(10) == np.ones(10)*pdf.mean)


def test7():
    # Almost constant PDF, fit with KDE
    d = np.array([1.23456789, 1.23456789, 1.23456789, 1.23456789, 1.23456789001])
    pdf = ExperimentalPDF(data=d, fit=True)
    assert np.allclose(pdf.dev, 0)
    assert np.allclose(pdf.mean, 1.23456789)
    assert np.allclose(pdf.range, (pdf.mean, pdf.mean))
    assert np.allclose(pdf.lhs(10), np.ones(10)*pdf.mean)


def test8():
    # Almost constant PDF, NOT fit with KDE
    d = np.array([1.23456789, 1.23456789, 1.23456789, 1.23456789, 1.23456789001])
    pdf = ExperimentalPDF(data=d, fit=False)
    assert np.allclose(pdf.dev, 0)
    assert np.allclose(pdf.mean, 1.23456789)
    assert np.allclose(pdf.range, (pdf.mean, pdf.mean))
    assert np.allclose(pdf.lhs(10), np.ones(10)*pdf.mean)


if __name__ == "__main__":
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test7()
    test8()
