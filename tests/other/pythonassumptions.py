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


class TestPythonAssumptions(unittest.TestCase):
    """
    Tests if some assumptions, which are made about the interpretation by python,
    are true.
    """
    def test_equal(self):
        self.assertEqual([], [])
        self.assertEqual(list(), list())    # it is preferred to use [] in the source code
        self.assertEqual(list(), [])        # it is preferred to use [] in the source code
        self.assertEqual({}, {})
        self.assertEqual(dict(), dict())    # it is preferred to use {} in the source code
        self.assertEqual(dict(), {})        # it is preferred to use {} in the source code
        self.assertEqual((), ())
        self.assertEqual(tuple(), tuple())
        self.assertEqual(tuple(), ())
        self.assertEqual(0.0, 0.0 + 0.0j)

    def test_not_equal(self):
        self.assertNotEqual([], ())
        self.assertNotEqual([], set())
        self.assertNotEqual((), frozenset())

    def test_is(self):
        self.assertIs(None, None)

    def test_is_not(self):
        self.assertIsNot([], [])
        self.assertIsNot(list(), list())    # it is preferred to use [] in the source code
        self.assertIsNot(list(), [])        # it is preferred to use [] in the source code
        self.assertIsNot({}, {})
        self.assertIsNot(dict(), dict())    # it is preferred to use {} in the source code
        self.assertIsNot(dict(), {})        # it is preferred to use {} in the source code
#       self.assertIsNot((0.0,), (0.0,))    # this assumption is not true, when using PyPy

    def test_bool(self):
        self.assertFalse(None)

    def test_iterables(self):
        # concatenation
        self.assertEqual([1, 2] + [3], [1, 2, 3])
        self.assertEqual((1, 2) + (3,), (1, 2, 3))
        # tests if a list is copied, even when it is casted to a list again
        a = [6, 4, 2, 0, 3]
        b = list(a)
        b.reverse()
        self.assertEqual(a, [6, 4, 2, 0, 3])
        self.assertEqual(b, [3, 0, 2, 4, 6])
        a.sort()
        self.assertEqual(a, [0, 2, 3, 4, 6])
        self.assertEqual(b, [3, 0, 2, 4, 6])

