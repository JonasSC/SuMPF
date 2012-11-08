# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012 Jonas Schulte-Coerne
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


class TestDifferentiate(unittest.TestCase):
	"""
	A TestCase for the differentiating function.
	"""
	def test_differentiate(self):
		tests = []
		tests.append(([1.0, 1.0, 1.0], [0.0, 0.0, 0.0]))	# test constant input
		tests.append(([0.0, 1.0, 2.0], [1.0, 1.0, 1.0]))	# test constant raise
		tests.append(([1.4, 2.5, 3.6], [1.1, 1.1, 1.1]))	# test constant raise with offset
		tests.append(([5.0, 1.0, 5.0], [-4.0, 0.0, 4.0]))	# test symmetric V
		tests.append(([5.0, 1.0, 3.0], [-4.0, -1.0, 2.0]))	# test asymmetric V
		tests.append(([5, 1, 2], [-4.0, -1.5, 1.0]))		# test integer input
		tests.append(([], []))								# test empty input
		tests.append(([5.0], [0.0]))						# test input with length 1
		tests.append(([1.0, 3.0], [2.0, 2.0]))				# test input with length 2
		for test, result in tests:
			self.assertEqual(sumpf.helper.differentiate(test), result)

