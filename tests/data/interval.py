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

import unittest
import sumpf


class TestSampleInterval(unittest.TestCase):
    def test_integer(self):
        """
        test creating an interval from integers.
        """
        # single values
        i = sumpf.SampleInterval(30)
        self.assertEqual(self.__get_values(i, 100), [(0, 30), False, False])
        self.assertEqual(self.__get_values(i, 500), [(0, 30), False, False])
        i = sumpf.SampleInterval(-20)
        self.assertEqual(self.__get_values(i, 100), [(80, 100), False, False])
        self.assertEqual(self.__get_values(i, 500), [(480, 500), False, False])
        i = sumpf.SampleInterval(0)
        self.assertEqual(self.__get_values(i, 100), [(0, 0), False, False])
        self.assertEqual(self.__get_values(i, 500), [(0, 0), False, False])
        i = sumpf.SampleInterval(100)
        self.assertEqual(self.__get_values(i, 100), [(0, 100), False, False])
        self.assertEqual(self.__get_values(i, 500), [(0, 100), False, False])
        # intervals
        i = sumpf.SampleInterval(30, 50)
        self.assertEqual(self.__get_values(i, 100), [(30, 50), False, False])
        self.assertEqual(self.__get_values(i, 500), [(30, 50), False, False])
        i = sumpf.SampleInterval(-70, -40)
        self.assertEqual(self.__get_values(i, 100), [(30, 60), False, False])
        self.assertEqual(self.__get_values(i, 500), [(430, 460), False, False])
        i = sumpf.SampleInterval(0, 100)
        self.assertEqual(self.__get_values(i, 100), [(0, 100), False, False])
        self.assertEqual(self.__get_values(i, 500), [(0, 100), False, False])
        # values, that exceed the limits
        i = sumpf.SampleInterval(110)
        self.assertEqual(self.__get_values(i, 100), [(0, 110), True, False])
        i = sumpf.SampleInterval(-110)
        self.assertEqual(self.__get_values(i, 100), [(-10, 100), True, False])
        i = sumpf.SampleInterval(-20, 110)
        self.assertEqual(self.__get_values(i, 100), [(80, 110), True, False])
        i = sumpf.SampleInterval(-110, 20)
        self.assertEqual(self.__get_values(i, 100), [(-10, 20), True, False])
        # values, that make the start index smaller than the stop index
        i = sumpf.SampleInterval(50, 30)
        self.assertEqual(self.__get_values(i, 100), [(50, 30), False, True])
        i = sumpf.SampleInterval(-10, 10)
        self.assertEqual(self.__get_values(i, 100), [(90, 10), False, True])
        i = sumpf.SampleInterval(10, -110)
        self.assertEqual(self.__get_values(i, 100), [(10, -10), True, True])

    def test_integer_iterable(self):
        """
        test creating an interval from lists or tuples of integers.
        """
        # intervals
        i = sumpf.SampleInterval((30, 50))
        self.assertEqual(self.__get_values(i, 100), [(30, 50), False, False])
        self.assertEqual(self.__get_values(i, 500), [(30, 50), False, False])
        i = sumpf.SampleInterval([-70, -40])
        self.assertEqual(self.__get_values(i, 100), [(30, 60), False, False])
        self.assertEqual(self.__get_values(i, 500), [(430, 460), False, False])
        i = sumpf.SampleInterval((0, 100))
        self.assertEqual(self.__get_values(i, 100), [(0, 100), False, False])
        self.assertEqual(self.__get_values(i, 500), [(0, 100), False, False])
        # values, that exceed the limits
        i = sumpf.SampleInterval((-20, 110))
        self.assertEqual(self.__get_values(i, 100), [(80, 110), True, False])
        i = sumpf.SampleInterval([-110, 20])
        self.assertEqual(self.__get_values(i, 100), [(-10, 20), True, False])
        # values, that make the start index smaller than the stop index
        i = sumpf.SampleInterval((50, 30))
        self.assertEqual(self.__get_values(i, 100), [(50, 30), False, True])
        i = sumpf.SampleInterval([-10, 10])
        self.assertEqual(self.__get_values(i, 100), [(90, 10), False, True])
        i = sumpf.SampleInterval((10, -110))
        self.assertEqual(self.__get_values(i, 100), [(10, -10), True, True])

    def test_float(self):
        """
        test creating an interval from floats.
        """
        # single values
        i = sumpf.SampleInterval(0.3)
        self.assertEqual(self.__get_values(i, 100), [(0, 30), False, False])
        self.assertEqual(self.__get_values(i, 500), [(0, 150), False, False])
        i = sumpf.SampleInterval(-0.2)
        self.assertEqual(self.__get_values(i, 100), [(80, 100), False, False])
        self.assertEqual(self.__get_values(i, 500), [(400, 500), False, False])
        i = sumpf.SampleInterval(0.0)
        self.assertEqual(self.__get_values(i, 100), [(0, 0), False, False])
        self.assertEqual(self.__get_values(i, 500), [(0, 0), False, False])
        i = sumpf.SampleInterval(1.0)
        self.assertEqual(self.__get_values(i, 100), [(0, 100), False, False])
        self.assertEqual(self.__get_values(i, 500), [(0, 500), False, False])
        # intervals
        i = sumpf.SampleInterval(0.3, 0.5)
        self.assertEqual(self.__get_values(i, 100), [(30, 50), False, False])
        self.assertEqual(self.__get_values(i, 500), [(150, 250), False, False])
        i = sumpf.SampleInterval(-0.7, -0.4)
        self.assertEqual(self.__get_values(i, 100), [(30, 60), False, False])
        self.assertEqual(self.__get_values(i, 500), [(150, 300), False, False])
        i = sumpf.SampleInterval(0.0, 1.0)
        self.assertEqual(self.__get_values(i, 100), [(0, 100), False, False])
        self.assertEqual(self.__get_values(i, 500), [(0, 500), False, False])
        # values, that exceed the limits
        i = sumpf.SampleInterval(1.1)
        self.assertEqual(self.__get_values(i, 100), [(0, 110), True, False])
        i = sumpf.SampleInterval(-1.1)
        self.assertEqual(self.__get_values(i, 100), [(-10, 100), True, False])
        i = sumpf.SampleInterval(-0.2, 1.1)
        self.assertEqual(self.__get_values(i, 100), [(80, 110), True, False])
        i = sumpf.SampleInterval(-1.1, 0.2)
        self.assertEqual(self.__get_values(i, 100), [(-10, 20), True, False])
        # values, that make the start index smaller than the stop index
        i = sumpf.SampleInterval(0.5, 0.3)
        self.assertEqual(self.__get_values(i, 100), [(50, 30), False, True])
        i = sumpf.SampleInterval(-0.1, 0.1)
        self.assertEqual(self.__get_values(i, 100), [(90, 10), False, True])
        i = sumpf.SampleInterval(0.1, -1.1)
        self.assertEqual(self.__get_values(i, 100), [(10, -10), True, True])

    def test_float_iterable(self):
        """
        test creating an interval from lists or tuples of floats.
        """
        # intervals
        i = sumpf.SampleInterval((0.0, 0.5))
        self.assertEqual(self.__get_values(i, 100), [(0, 50), False, False])
        self.assertEqual(self.__get_values(i, 500), [(0, 250), False, False])
        i = sumpf.SampleInterval([-0.7, -0.4])
        self.assertEqual(self.__get_values(i, 100), [(30, 60), False, False])
        self.assertEqual(self.__get_values(i, 500), [(150, 300), False, False])
        i = sumpf.SampleInterval((0.0, 1.0))
        self.assertEqual(self.__get_values(i, 100), [(0, 100), False, False])
        self.assertEqual(self.__get_values(i, 500), [(0, 500), False, False])
        # values, that exceed the limits
        i = sumpf.SampleInterval((-0.2, 1.1))
        self.assertEqual(self.__get_values(i, 100), [(80, 110), True, False])
        i = sumpf.SampleInterval([-1.1, 0.2])
        self.assertEqual(self.__get_values(i, 100), [(-10, 20), True, False])
        # values, that make the start index smaller than the stop index
        i = sumpf.SampleInterval((0.5, 0.3))
        self.assertEqual(self.__get_values(i, 100), [(50, 30), False, True])
        i = sumpf.SampleInterval([-0.1, 0.1])
        self.assertEqual(self.__get_values(i, 100), [(90, 10), False, True])
        i = sumpf.SampleInterval((0.1, -1.1))
        self.assertEqual(self.__get_values(i, 100), [(10, -10), True, True])

    def test_factory(self):
        """
        test the static "factory" method.
        """
        for d in ((0.3,), (-40,), ((0.9, 100),), (-3, 1.0)):
            i1 = sumpf.SampleInterval.factory(*d)
            i2 = sumpf.SampleInterval(*d)
            i3 = sumpf.SampleInterval.factory(i2)
            self.assertEqual(i1, i2)
            self.assertIs(i2, i3)

    def test_equality(self):
        """
        test the overload of the __eq__ and __ne__ methods.
        """
        # not equal
        self.assertNotEqual(sumpf.SampleInterval(100), sumpf.SampleInterval(1.0))
        # equal integers
        self.assertEqual(sumpf.SampleInterval(12, 25), sumpf.SampleInterval(12, 25))
        self.assertEqual(sumpf.SampleInterval((12, -25)), sumpf.SampleInterval(12, -25))
        self.assertEqual(sumpf.SampleInterval(25), sumpf.SampleInterval(0, 25))
        self.assertEqual(sumpf.SampleInterval(-25), sumpf.SampleInterval(-25, 1.0))
        # equal floats
        self.assertEqual(sumpf.SampleInterval(0.12, 0.25), sumpf.SampleInterval(0.12, 0.25))
        self.assertEqual(sumpf.SampleInterval((0.12, -0.25)), sumpf.SampleInterval(0.12, -0.25))
        self.assertEqual(sumpf.SampleInterval(0.25), sumpf.SampleInterval(0.0, 0.25))
        self.assertEqual(sumpf.SampleInterval(-0.25), sumpf.SampleInterval(-0.25, 1.0))
        # negative floats converted
        self.assertEqual(sumpf.SampleInterval(-0.12, -0.25), sumpf.SampleInterval(0.88, 0.75))
        self.assertEqual(sumpf.SampleInterval((-0.12, -0.25)), sumpf.SampleInterval(0.88, 0.75))
        self.assertEqual(sumpf.SampleInterval(-0.25), sumpf.SampleInterval(0.75, 1.0))

    def test_slicing(self):
        """
        test if slicing an iterable with an interval works as expected
        """
        a = tuple(range(10))
        i = sumpf.SampleInterval(2, 6)
        self.assertEqual(a[i.GetSlice(10)], tuple(range(2, 6)))
        i = sumpf.SampleInterval(0.2, -0.4)
        self.assertEqual(a[i.GetSlice(10)], tuple(range(2, 6)))

    def __get_values(self, interval, length):
        """
        Returns all parameters of the interval as a list
        """
        return [interval.GetIndices(length),
                interval.IsExcessive(length),
                interval.IsReversed(length)]

