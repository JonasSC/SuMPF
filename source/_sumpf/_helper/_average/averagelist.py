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

from .base import AverageBase

try:
	import numpy
except ImportError:
	# This is a dirty import that has to be made cleaner one day
	# Do not remove the comment line below, because it is needed by a unit test
	# sumpf.helper.numpydummy
	import _sumpf._helper.numpydummy as numpy



class AverageList(AverageBase):
	"""
	DO NOT USE THIS. It seems, that this algorithm is currently less precise
	than the SumAndDivide algorithm. Use that one instead.

	A class that calculates the average through a list in which the averages of
	the previously added values are stored.
	If the list is empty, a new value will simply be added to the list.
	If a new value shall be written to a cell that already contains a value, the
	average of these two values is calculated and written to the next cell,
	while the current cell is reset to None.
	The average is then calculated by summing up the products of each list value
	and the number of values of which the list value is the average. This sum
	is divided by the total number of values is the average.

	An Example:
	The list contains a value at its beginning and one in the second cell.
	When adding a new value, the average of the new value and the first value in
	the list is calculated. The first cell is reset to None. The average shall
	be written to the second cell which is neither None nor does it not exist,
	so the average of the second value and the average is calculated and stored
	in the third cell of the list (which is appended if it does not exist).

	Another Example just with code:
		avg = AverageList()     # list: []
		avg.Add(1)              # list: [1]
		avg.Add(2)              # list: [None, 1.5]
		avg.Add(3)              # list: [3, 1.5]
		avg.Add(4)              # list: [None, None, 2.5]
		avg.Add(5)              # list: [5, None, 2.5]

	Advantages of this method:
		- Since most sums are created by adding averaged values, the summands
		are likely to have similar values. This reduces the loss of precision
		which is created by adding very small floats and very large floats.
		- Instead of storing the added values, only some averages are stored, so
		The memory usage has only the complexity of O(log2(n)).
	Disadvantages:
		- Both adding a value and calculating the average are quite complicated
		compared to other averaging algorithms
		- the final calculation of the average does not seem to be optimal since
		there is still an addition of very different floats if there are many
		None cells in the list.
	"""
	def __init__(self, values=[]):
		"""
		All parameters are optional.
		@param values: a list of values of which the average shall be calculated.
		"""
		AverageBase.__init__(self, values=[])
		for v in values:
			self.Add(v)

	def Add(self, value):
		"""
		Method to add a value to the list of values which shall be averaged.
		The value can be either a scalar value or a list.
		@param value: the value that shall be added
		"""
		if len(self._values) == 0:
			self._values.append(value)
		else:
			for i in range(len(self._values)):
				if self._values[i] is None:
					self._values[i] = value
					break
				else:
					value = numpy.add(self._values[i], value)
					value = numpy.divide(value, 2.0)
					self._values[i] = None
					if len(self._values) == i + 1:
						self._values.append(value)

	def _GetAverage(self):
		"""
		Calculates the average and returns it.
		@retval : the average all added values
		"""
		number = 0
		value = 0.0
		# initialize value as a list of 0.0s if needed
		for v in self._values:
			if v is not None:
				if isinstance(v, float):
					break
				else:
					value = numpy.multiply(v, 0.0)
		# sum the values up
		for i in range(len(self._values)):
			if self._values[i] is not None:
				weighted = numpy.multiply((2 ** i), self._values[i])
				value = numpy.add(value, weighted)
				number += 2 ** i
		result = numpy.divide(value, float(number))
		return result

