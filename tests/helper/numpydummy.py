# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2017 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import collections
import unittest

import sumpf
import _common as common

try:
    import numpy
except ImportError:
    pass


@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestNumpyDummy(unittest.TestCase):
    """
    A TestCase for the numpydummy functions.
    """
    def setUp(self):
        self.arrayvalues = [(1.0, -0.1),
                            ((1.0, -2.0, 3.0),
                             (0.1, -0.2, 0.3)),
                            (((1.0, -2.0, 3.0),
                              (4.0, -5.0, 6.0),
                              (7.0, -8.0, 9.0)),
                             ((0.1, -0.2, 0.3),
                              (0.4, -0.5, 0.6),
                              (0.7, -0.8, 0.9)))]
        self.complexvalues = (2.0, 1.4j, 2.3 + 4.7j, 6.3j + 1.2)

    def __Compare(self, result_numpy, result_numpydummy, a_index, b_index):
        if isinstance(result_numpy, collections.Iterable):
            if not isinstance(result_numpydummy, collections.Iterable):
                self.fail("The numpy result is iterable while the numpydummy result isn't. (" + str(a_index) + " " + str(b_index) + ")")
            elif len(result_numpy) != len(result_numpydummy):
                self.fail("The numpy result has a different length than the numpydummy result. (" + str(a_index) + " " + str(b_index) + ")")
            else:
                for i in range(len(result_numpy)):
                    self.__Compare(result_numpy[i], result_numpydummy[i], a_index, b_index)
        else:
            if isinstance(result_numpydummy, collections.Iterable):
                self.fail("The numpy result isn't iterable while the numpydummy result is. (" + str(a_index) + " " + str(b_index) + ")")
            elif abs(result_numpy - result_numpydummy) > 1e-12:
                self.fail(str(result_numpy) + " != " + str(result_numpydummy) + "    (" + str(a_index) + " " + str(b_index) + ")")

    # number types

    def test_complex_(self):
        c = sumpf.helper.numpydummy.complex_(self.arrayvalues)
        def recursion(a):
            if isinstance(a, collections.Iterable):
                return all(recursion(b) for b in a)
            else:
                return isinstance(a, complex)
        self.assertTrue(recursion(c))

    # array generators and related functions

    def test_zeros(self):
        self.assertEqual(sumpf.helper.numpydummy.zeros(shape=()), 0.0)
        for s in range(1, 5):
            shape = list(range(s))
            r1 = numpy.zeros(shape=shape, dtype=float)
            r2 = sumpf.helper.numpydummy.zeros(shape=shape, dtype=sumpf.helper.numpydummy.float32)
            r3 = sumpf.helper.numpydummy.zeros(shape=shape)
            self.__Compare(r1, r2, s, None)
            self.__Compare(r2, r3, s, None)

    def test_shape(self):
        self.__Compare(numpy.shape(self.arrayvalues[0][0]), sumpf.helper.numpydummy.shape(self.arrayvalues[0][0]), 0, 0)
        self.__Compare(numpy.shape([]), sumpf.helper.numpydummy.shape([]), 0, 0)
        for i, a in enumerate(self.arrayvalues):
            self.__Compare(numpy.shape(a), sumpf.helper.numpydummy.shape(a), i, i)

    # algebra functions

    def test_add(self):
        a = [(1, 2), (3, 4)]
        b = [(5, 6)]
        n = numpy.add(a, b)
        d = sumpf.helper.numpydummy.add(a, b)
        self.assertEqual(numpy.linalg.norm(numpy.subtract(n, d)), 0)
        for a in range(len(self.arrayvalues)):
            for b in range(len(self.arrayvalues)):
                r1 = numpy.add(self.arrayvalues[a][0], self.arrayvalues[b][1])
                r2 = sumpf.helper.numpydummy.add(self.arrayvalues[a][0], self.arrayvalues[b][1])
                self.__Compare(r1, r2, a, b)

    def test_subtract(self):
        a = [(1, 2), (3, 4)]
        b = [(5, 6)]
        n = numpy.subtract(a, b)
        d = sumpf.helper.numpydummy.subtract(a, b)
        self.assertEqual(numpy.linalg.norm(numpy.subtract(n, d)), 0)
        for a in range(len(self.arrayvalues)):
            for b in range(len(self.arrayvalues)):
                r1 = numpy.subtract(self.arrayvalues[a][0], self.arrayvalues[b][1])
                r2 = sumpf.helper.numpydummy.subtract(self.arrayvalues[a][0], self.arrayvalues[b][1])
                self.__Compare(r1, r2, a, b)

    def test_multiply(self):
        a = [(1, 2), (3, 4)]
        b = [(5, 6)]
        n = numpy.multiply(a, b)
        d = sumpf.helper.numpydummy.multiply(a, b)
        self.assertEqual(numpy.linalg.norm(numpy.subtract(n, d)), 0)
        for a in range(len(self.arrayvalues)):
            for b in range(len(self.arrayvalues)):
                r1 = numpy.multiply(self.arrayvalues[a][0], self.arrayvalues[b][1])
                r2 = sumpf.helper.numpydummy.multiply(self.arrayvalues[a][0], self.arrayvalues[b][1])
                self.__Compare(r1, r2, a, b)

    def test_divide(self):
        a = [(1, 2), (3, 4)]
        b = [(5, 6)]
        n = numpy.divide(a, b)
        d = sumpf.helper.numpydummy.divide(a, b)
        self.assertEqual(numpy.linalg.norm(numpy.subtract(n, d)), 0)
        for a in range(len(self.arrayvalues)):
            for b in range(len(self.arrayvalues)):
                r1 = numpy.divide(self.arrayvalues[a][0], self.arrayvalues[b][1])
                r2 = sumpf.helper.numpydummy.divide(self.arrayvalues[a][0], self.arrayvalues[b][1])
                self.__Compare(r1, r2, a, b)

    def test_true_divide(self):
        a = [(1, 2), (3, 4)]
        b = [(5, 6)]
        n = numpy.true_divide(a, b)
        d = sumpf.helper.numpydummy.true_divide(a, b)
        self.assertEqual(numpy.linalg.norm(numpy.subtract(n, d)), 0)
        for a in range(len(self.arrayvalues)):
            for b in range(len(self.arrayvalues)):
                r1 = numpy.true_divide(self.arrayvalues[a][0], self.arrayvalues[b][1])
                r2 = sumpf.helper.numpydummy.true_divide(self.arrayvalues[a][0], self.arrayvalues[b][1])
                self.__Compare(r1, r2, a, b)

    def test_mod(self):
        a = [(1, 2), (3, 4)]
        b = [(5, 6)]
        n = numpy.mod(a, b)
        d = sumpf.helper.numpydummy.mod(a, b)
        self.assertEqual(numpy.linalg.norm(numpy.subtract(n, d)), 0)
        for a in range(len(self.arrayvalues)):
            for b in range(len(self.arrayvalues)):
                r1 = numpy.mod(self.arrayvalues[a][0], self.arrayvalues[b][1])
                r2 = sumpf.helper.numpydummy.mod(self.arrayvalues[a][0], self.arrayvalues[b][1])
                self.__Compare(r1, r2, a, b)

    def test_power(self):
        a = [(1, 2), (3, 4)]
        b = [(5, 6)]
        n = numpy.power(a, b)
        d = sumpf.helper.numpydummy.power(a, b)
        self.assertEqual(numpy.linalg.norm(numpy.subtract(n, d)), 0)
        for a in range(len(self.arrayvalues)):
            for b in range(len(self.arrayvalues)):
                r1 = numpy.power(numpy.abs(self.arrayvalues[a][0]), self.arrayvalues[b][1])
                r2 = sumpf.helper.numpydummy.power(numpy.abs(self.arrayvalues[a][0]), self.arrayvalues[b][1])
                self.__Compare(r1, r2, a, b)

    # monadic computations

    def test_abs(self):
        for i in range(len(self.complexvalues)):
            r1 = numpy.abs(self.complexvalues[i])
            r2 = sumpf.helper.numpydummy.abs(self.complexvalues[i])
            self.__Compare(r1, r2, i, None)
        for a in range(len(self.arrayvalues)):
            r1 = numpy.abs(self.arrayvalues[a][0])
            r2 = sumpf.helper.numpydummy.abs(self.arrayvalues[a][0])
            self.__Compare(r1, r2, a, None)

    def test_angle(self):
        for i in range(len(self.complexvalues)):
            r1 = numpy.angle(self.complexvalues[i])
            r2 = sumpf.helper.numpydummy.angle(self.complexvalues[i])
            self.__Compare(r1, r2, i, None)
        for a in range(len(self.arrayvalues)):
            r1 = numpy.angle(self.arrayvalues[a][0])
            r2 = sumpf.helper.numpydummy.angle(self.arrayvalues[a][0])
            self.__Compare(r1, r2, a, None)

    def test_real(self):
        # does not test for scalar values, since numpy's behavior to return an array for scalar input is a bit unexpected and not modelled by numpydummy
        r1 = numpy.real(self.complexvalues)
        r2 = sumpf.helper.numpydummy.real(self.complexvalues)
        self.__Compare(r1, r2, -1, None)
        for a in range(len(self.arrayvalues)):
            r1 = numpy.real(self.arrayvalues[a])
            r2 = sumpf.helper.numpydummy.real(self.arrayvalues[a])
            self.__Compare(r1, r2, a, None)

    def test_imag(self):
        # does not test for scalar values, since numpy's behavior to return an array for scalar input is a bit unexpected and not modelled by numpydummy
        r1 = numpy.imag(self.complexvalues)
        r2 = sumpf.helper.numpydummy.imag(self.complexvalues)
        self.__Compare(r1, r2, -1, None)
        for a in range(len(self.arrayvalues)):
            r1 = numpy.imag(self.arrayvalues[a])
            r2 = sumpf.helper.numpydummy.imag(self.arrayvalues[a])
            self.__Compare(r1, r2, a, None)

    def test_conjugate(self):
        for i in range(len(self.complexvalues)):
            r1 = numpy.conjugate(self.complexvalues[i])
            r2 = sumpf.helper.numpydummy.conjugate(self.complexvalues[i])
            self.__Compare(r1, r2, i, None)
        for a in range(len(self.arrayvalues)):
            r1 = numpy.conjugate(self.arrayvalues[a][0])
            r2 = sumpf.helper.numpydummy.conjugate(self.arrayvalues[a][0])
            self.__Compare(r1, r2, a, None)

    def test_transpose(self):
        # only tests for one- and twodimensional arrays
        for a in range(0, 1):
            r1 = numpy.transpose(self.arrayvalues[a])
            r2 = sumpf.helper.numpydummy.transpose(self.arrayvalues[a])
            self.__Compare(r1, r2, a, None)

    # array functions with a scalar result

    def test_min(self):
        self.assertEqual(numpy.min(self.arrayvalues[0][0]), sumpf.helper.numpydummy.min(self.arrayvalues[0][0]))
        self.assertRaises(ValueError, sumpf.helper.numpydummy.min, [])
        for a in self.arrayvalues:
            self.assertEqual(numpy.min(a), sumpf.helper.numpydummy.min(a))

    def test_max(self):
        self.assertEqual(numpy.max(self.arrayvalues[0][0]), sumpf.helper.numpydummy.max(self.arrayvalues[0][0]))
        self.assertRaises(ValueError, sumpf.helper.numpydummy.max, [])
        for a in self.arrayvalues:
            self.assertEqual(numpy.max(a), sumpf.helper.numpydummy.max(a))

    def test_sum(self):
        self.__Compare(numpy.sum(self.arrayvalues[0][0]), sumpf.helper.numpydummy.sum(self.arrayvalues[0][0]), 0, 0)
        self.__Compare(numpy.sum([]), sumpf.helper.numpydummy.sum([]), 0, 0)
        for i, a in enumerate(self.arrayvalues):
            self.__Compare(numpy.sum(a), sumpf.helper.numpydummy.sum(a), i, i)

    def test_prod(self):
        self.__Compare(numpy.prod(self.arrayvalues[0][0]), sumpf.helper.numpydummy.prod(self.arrayvalues[0][0]), 0, 0)
        self.__Compare(numpy.prod([]), sumpf.helper.numpydummy.prod([]), 0, 0)
        for i, a in enumerate(self.arrayvalues):
            self.__Compare(numpy.prod(a), sumpf.helper.numpydummy.prod(a), i, i)

    def test_mean(self):
        values = (3.3, -4.7, -9.8, 15.3, 6.4)
        from_dummy = sumpf.helper.numpydummy.mean(values)
        from_numpy = numpy.mean(values)
        self.assertEqual(from_dummy, from_numpy)

    def test_var(self):
        values = (3.3, -4.7, -9.8, 15.3, 6.4)
        from_dummy = sumpf.helper.numpydummy.var(values)
        from_numpy = numpy.var(values)
        self.assertAlmostEqual(from_dummy, from_numpy)

# evaluation functions

    def test_equal(self):
        for a in self.arrayvalues:
            a2 = numpy.square(a)
            for b in self.arrayvalues:
                try:
                    e1 = numpy.equal(a, b)
                except ValueError:
                    break
                else:
                    e2 = sumpf.helper.numpydummy.equal(a, b)
                    self.assertTrue(numpy.equal(e1, e2).all())
                    n1 = numpy.equal(a2, b)
                    n2 = sumpf.helper.numpydummy.equal(a2, b)
                    self.assertTrue(numpy.equal(n1, n2).all())

    def test_nonzero(self):
        self.__Compare(numpy.nonzero(0.0), sumpf.helper.numpydummy.nonzero(0.0), 0, 0)
        self.__Compare(numpy.nonzero(self.arrayvalues[0][0]), sumpf.helper.numpydummy.nonzero(self.arrayvalues[0][0]), 0, 0)
        self.__Compare(numpy.nonzero([]), sumpf.helper.numpydummy.nonzero([]), 0, 0)
        for i, a in enumerate(self.arrayvalues):
            self.__Compare(numpy.nonzero(a), sumpf.helper.numpydummy.nonzero(a), i, i)
            b = numpy.multiply(a, (0.0, 2.4, 0.0)[0:numpy.shape(a)[-1]])
            self.__Compare(numpy.nonzero(b), sumpf.helper.numpydummy.nonzero(b), i, i)

