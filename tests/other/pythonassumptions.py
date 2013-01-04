# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2013 Jonas Schulte-Coerne
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
		self.assertEqual(list(), list())	# it is preferred to use [] in the source code
		self.assertEqual(list(), [])		# it is preferred to use [] in the source code
		self.assertEqual({}, {})
		self.assertEqual(dict(), dict())	# it is preferred to use {} in the source code
		self.assertEqual(dict(), {})		# it is preferred to use {} in the source code
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
		self.assertIsNot(list(), list())	# it is preferred to use [] in the source code
		self.assertIsNot(list(), [])		# it is preferred to use [] in the source code
		self.assertIsNot({}, {})
		self.assertIsNot(dict(), dict())	# it is preferred to use {} in the source code
		self.assertIsNot(dict(), {})		# it is preferred to use {} in the source code
		self.assertIsNot((0.0,), (0.0,))

	def test_bool(self):
		self.assertFalse(None)

