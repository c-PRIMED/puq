from puq.smolyak_funcs import legendre_nd, jacobi_e2_nd, nelms, chaos_sequence, jacobi_e2_1d
from numpy import array, allclose

values = [(jacobi_e2_1d, (3, 1.5, 0), array([[1.0], [0.55555556], [0.38461538], [0.29411765]])),
          (jacobi_e2_1d, (1, 1, 0), array([[1.0], [0.5]])),
          (jacobi_e2_1d, (1, 0, 0), array([[1.0], [0.33333333]])),
          (jacobi_e2_1d, (2, 0, 0), array([[1.0], [0.33333333], [0.2]])),
          (jacobi_e2_1d, (3, 0, 0), array([[1.0], [0.33333333], [0.2], [0.14285714]])),
          (jacobi_e2_nd, (1, 2, 0, 0), array([[1.0], [0.33333333], [0.2]])),
          (jacobi_e2_nd, (2, 1, 0, 0), array([[1.0], [0.33333333], [0.33333333]])),
          (jacobi_e2_nd, (3, 2, 0, 0), array([[1.0], [0.33333333], [0.33333333], [0.33333333], [0.2], [0.11111111], [0.11111111], [0.2], [0.11111111], [0.2]])),
          (legendre_nd, (array([0, 0.70711]), 2, 2), array([1.0, 0.0, 0.70711, -0.5, 0.0, 0.25000683])),
          (chaos_sequence, (1, 1), array([[0], [1]])),
          (chaos_sequence, (2, 1), array([[0, 0], [1, 0], [0, 1]])),
          (chaos_sequence, (2, 2), array([[0, 0], [1, 0], [0, 1], [2, 0], [1, 1], [0, 2]])),
          (chaos_sequence, (3, 2), array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [2, 0, 0], [1, 1, 0], [1, 0, 1], [0, 2, 0], [0, 1, 1], [0, 0, 2]])),
          ]

# nosetests requires this simplistic approach to generate decent xml test names
def test_jacobi_e2_1d_0():
    func, args, expected = values[0]
    do_tst(func, args, expected)
def test_jacobi_e2_1d_1():
    func, args, expected = values[1]
    do_tst(func, args, expected)
def test_jacobi_e2_1d_2():
    func, args, expected = values[2]
    do_tst(func, args, expected)
def test_jacobi_e2_1d_3():
    func, args, expected = values[3]
    do_tst(func, args, expected)
def test_jacobi_e2_1d_4():
    func, args, expected = values[4]
    do_tst(func, args, expected)
def test_jacobi_e2_nd_0():
    func, args, expected = values[5]
    do_tst(func, args, expected)
def test_jacobi_e2_nd_1():
    func, args, expected = values[6]
    do_tst(func, args, expected)
def test_jacobi_e2_nd_2():
    func, args, expected = values[7]
    do_tst(func, args, expected)
def test_legendre_nd():
    func, args, expected = values[8]
    do_tst(func, args, expected)
def test_chaos_sequence_0():
    func, args, expected = values[9]
    do_tst(func, args, expected)
def test_chaos_sequence_1():
    func, args, expected = values[10]
    do_tst(func, args, expected)
def test_chaos_sequence_2():
    func, args, expected = values[11]
    do_tst(func, args, expected)
def test_chaos_sequence_3():
    func, args, expected = values[12]
    do_tst(func, args, expected)


def do_tst(f, args, res):
    tmp = f(*args)
    #print tmp
    assert allclose(tmp, res)

