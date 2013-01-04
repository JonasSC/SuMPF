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
import sumpf


class TestAverage(unittest.TestCase):
	"""
	A TestCase for the averaging classes.
	"""
	def test_basics(self):
		"""
		Tests the basic stuff for all averaging classes.
		"""
		for i in type(sumpf.helper.average.factory()).__mro__[-2].__subclasses__():	# iterate over all subclasses of the average base class
			avg = i()
			avg.Add([1.0, 2.0, 3.0])
			avg.Add([3.0, 2.0, 1.0])
			self.assertEqual(avg.GetAverage(), [2.0, 2.0, 2.0])	# averaging lists and adding values with the Add method should have worked
			avg = i(values=[13, 10])
			avg.Add(13)
			avg.Add(2.0)
			self.assertEqual(avg.GetAverage(), 9.5)				# averaging over scalars (even integers) and adding values with the constructor should have worked

	def test_factory(self):
		"""
		Tests the factory method.
		"""
		avg = sumpf.helper.average.factory()
		avg.Add([1, 2, 3])
		avg.Add([3, 2, 1])
		self.assertEqual(avg.GetAverage(), [2.0, 2.0, 2.0])	# averaging lists and adding values with the Add method should have worked
		avg = sumpf.helper.average.factory(values=[1.5, 1])
		self.assertEqual(avg.GetAverage(), 1.25)			# averaging over scalars (even integers) and adding values with the constructor should have worked

#	def test_precision(self):
#		"""
#		Tests if the AverageList algorithm is more precise than the SumAndDivide
#		algorithm.
#		"""
#		count = 15
#		base = numpy.float128(0.01)
#		average = (1 - base ** count) / ((1 - base) * count)
#		values = []
#		for i in range(count):
#			values.append(float(base ** i))
#		avg1 = sumpf.helper.average.SumAndDivide(values=values)
#		avg2 = sumpf.helper.average.AverageList(values=values)
#		e1 = abs(avg1.GetAverage() - average)
#		e2 = abs(avg2.GetAverage() - average)
#		self.assertNotEqual(e1, e2)
#		self.assertGreater(e1, e2)

