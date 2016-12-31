from __future__ import absolute_import, division, print_function
import puq.hdf
import os
import h5py
import numpy as np

dname = os.path.dirname(os.path.realpath(__file__))
fname = os.path.join(dname, 'test1.hdf5')
hf = h5py.File(fname)


def test1():
    names = puq.hdf.get_output_names(hf)
    assert names == ['energy', 'kinetic_energy'], 'hdf5_get_output_names'


def test2():
    a = puq.hdf.get_result(hf, 'energy')
    b = hf['/output/data/energy'].value
    assert np.all(a == b), 'hdf5_get_result'

    got_except = False
    try:
        print(puq.hdf.get_result(hf))
    except:
        got_except = True
    assert got_except, 'hdf5_get_result (no args)'


def test3():
    print(puq.hdf.get_param_names(hf))
    print(puq.hdf.data_description(hf, 'energy'))
    print(puq.hdf.param_description(hf, 'm'))
    assert puq.hdf.get_param_names(hf) == ['m', 'v'], 'get_param_names'
    assert puq.hdf.data_description(hf, 'energy') == 'A random energy equation.', 'data_description'
    assert puq.hdf.param_description(hf, 'm') == 'mass', 'param_description'


if __name__ == "__main__":
    test1()
    test2()
    test3()
