from puq.meshgridn import meshgridn
import numpy as np


def test_meshgrid_example():
    # official example for meshgrid() from numpy docs
    X, Y = meshgridn([1, 2, 3], [4, 5, 6, 7])
    assert (X == np.array([[1, 2, 3],
                           [1, 2, 3],
                           [1, 2, 3],
                           [1, 2, 3]])).all()

    assert (Y == np.array([[4, 4, 4],
                           [5, 5, 5],
                           [6, 6, 6],
                           [7, 7, 7]])).all()


def test_meshgrid_empty():
    X = meshgridn([])
    assert len(X) == 1
    assert len(X[0]) == 0


def test_meshgrid_1d():
    X = meshgridn([1, 2])
    assert len(X) == 1
    assert (X == np.array([1, 2])).all()


def test_meshgrid_4d():
    xx = meshgridn([1, 2], [3, 4], [5, 6], [7, 8])
    assert len(xx) == 4
    assert (np.vstack(map(np.ndarray.flatten, xx)).T ==
            np.array([[1, 3, 5, 7],
                      [2, 3, 5, 7],
                      [1, 4, 5, 7],
                      [2, 4, 5, 7],
                      [1, 3, 6, 7],
                      [2, 3, 6, 7],
                      [1, 4, 6, 7],
                      [2, 4, 6, 7],
                      [1, 3, 5, 8],
                      [2, 3, 5, 8],
                      [1, 4, 5, 8],
                      [2, 4, 5, 8],
                      [1, 3, 6, 8],
                      [2, 3, 6, 8],
                      [1, 4, 6, 8],
                      [2, 4, 6, 8]])).all()
