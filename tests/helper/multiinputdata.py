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

import unittest
import sumpf


class TestMultiInputData(unittest.TestCase):
    """
    A TestCase for the MultiInputData class.
    """
    def test_function(self):
        # initialization
        mid = sumpf.helper.MultiInputData()
        self.assertEqual(mid.GetData(), [])
        # adding
        id1 = mid.Add(1)
        self.assertEqual(mid.GetData(), [1])
        id2 = mid.Add(2)
        id3 = mid.Add(3)
        self.assertEqual(mid.GetData(), [1, 2, 3])
        self.assertNotEqual(id1, id2)
        self.assertNotEqual(id1, id3)
        self.assertNotEqual(id2, id3)
        # replacing
        mid.Replace(id2, 4)
        self.assertEqual(mid.GetData(), [1, 4, 3])
        # removing
        mid.Remove(id1)
        self.assertEqual(mid.GetData(), [4, 3])
        mid.Remove(id3)
        self.assertEqual(mid.GetData(), [4])
        # adding again
        id5 = mid.Add(5)
        id6 = mid.Add(6)
        self.assertEqual(mid.GetData(), [4, 5, 6])
        self.assertNotEqual(id2, id5)
        self.assertNotEqual(id2, id6)
        self.assertNotEqual(id5, id6)
        # clearing
        mid.Clear()
        self.assertEqual(mid.GetData(), [])

