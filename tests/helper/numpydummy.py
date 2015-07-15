# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2015 Jonas Schulte-Coerne
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
        self.arrayvalues = []
        self.arrayvalues.append((1.0, -0.1))
        self.arrayvalues.append(((1.0, -2.0, 3.0),
                                 (0.1, -0.2, 0.3)))
        self.arrayvalues.append((
                                 ((1.0, -2.0, 3.0),
                                  (4.0, -5.0, 6.0),
                                  (7.0, -8.0, 9.0)),
                                 ((0.1, -0.2, 0.3),
                                  (0.4, -0.5, 0.6),
                                  (0.7, -0.8, 0.9)),
                               ))
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

    def test_add(self):
        for a in range(len(self.arrayvalues)):
            for b in range(len(self.arrayvalues)):
                r1 = numpy.add(self.arrayvalues[a][0], self.arrayvalues[b][1])
                r2 = sumpf.helper.numpydummy.add(self.arrayvalues[a][0], self.arrayvalues[b][1])
                self.__Compare(r1, r2, a, b)

    def test_subtract(self):
        for a in range(len(self.arrayvalues)):
            for b in range(len(self.arrayvalues)):
                r1 = numpy.subtract(self.arrayvalues[a][0], self.arrayvalues[b][1])
                r2 = sumpf.helper.numpydummy.subtract(self.arrayvalues[a][0], self.arrayvalues[b][1])
                self.__Compare(r1, r2, a, b)

    def test_multiply(self):
        for a in range(len(self.arrayvalues)):
            for b in range(len(self.arrayvalues)):
                r1 = numpy.multiply(self.arrayvalues[a][0], self.arrayvalues[b][1])
                r2 = sumpf.helper.numpydummy.multiply(self.arrayvalues[a][0], self.arrayvalues[b][1])
                self.__Compare(r1, r2, a, b)

    def test_divide(self):
        for a in range(len(self.arrayvalues)):
            for b in range(len(self.arrayvalues)):
                r1 = numpy.divide(self.arrayvalues[a][0], self.arrayvalues[b][1])
                r2 = sumpf.helper.numpydummy.divide(self.arrayvalues[a][0], self.arrayvalues[b][1])
                self.__Compare(r1, r2, a, b)

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

    def test_conjugate(self):
        for i in range(len(self.complexvalues)):
            r1 = numpy.conjugate(self.complexvalues[i])
            r2 = sumpf.helper.numpydummy.conjugate(self.complexvalues[i])
            self.__Compare(r1, r2, i, None)
        for a in range(len(self.arrayvalues)):
            r1 = numpy.conjugate(self.arrayvalues[a][0])
            r2 = sumpf.helper.numpydummy.conjugate(self.arrayvalues[a][0])
            self.__Compare(r1, r2, a, None)

    def test_zeros(self):
        self.assertEqual(sumpf.helper.numpydummy.zeros(shape=()), 0.0)
        for s in range(1, 5):
            shape = list(range(s))
            r1 = numpy.zeros(shape=shape, dtype=float)
            r2 = sumpf.helper.numpydummy.zeros(shape=shape, dtype=sumpf.helper.numpydummy.float32)
            r3 = sumpf.helper.numpydummy.zeros(shape=shape)
            self.__Compare(r1, r2, s, None)
            self.__Compare(r2, r3, s, None)

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

