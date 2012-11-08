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

from .base import AverageBase

try:
	import numpy
except ImportError:
	# This is a dirty import that has to be made cleaner one day
	# Do not remove the comment line below, because it is needed by a unit test
	# sumpf.helper.numpydummy
	import _sumpf._helper.numpydummy as numpy



class SumAndDivide(AverageBase):
	"""
	A class that calculates the average through the simple algorithm of summing
	all values up and then dividing that sum through the number of values.
	To reduce the problem with limited float precision, the values are sorted
	before summing them up.
	Advantages of this method:
		- Adding a value is the relatively simple task of appending the value to
		the list. So the averaging process does not interfere with the data
		creation process.
		- Calculating the average has the relatively low complexity of O(n)
	Disadvantages:
		- Storing all the values uses a lot of space.
		- If the sum of the values gets large compared to the values, these
		values might become under represented because of the limited float
		precision.
		- Sorting does not necessarily help when averaging lists.
	"""
	def _GetAverage(self):
		"""
		Calculates the average and returns it.
		@retval : the average all added values
		"""
		self._values.sort()
		sum = self._values[0]
		for v in self._values[1:]:
			sum = numpy.add(sum, v)
		result = numpy.divide(sum, float(len(self._values)))
		return result

