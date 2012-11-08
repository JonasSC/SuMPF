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

try:
	import numpy
except ImportError:
	import sumpf
	numpy = sumpf.helper.numpydummy



class Add:
	"""
	Abstract base class that can be used in conjunction with ChannelDataAlgebra.
	"""
	def _Calculate(self, a, b):
		return tuple(numpy.add(a, b))

	def _GetLabel(self):
		return "Sum"



class Subtract:
	"""
	Abstract base class that can be used in conjunction with ChannelDataAlgebra.
	"""
	def _Calculate(self, a, b):
		return tuple(numpy.subtract(a, b))

	def _GetLabel(self):
		return "Difference"



class Multiply:
	"""
	Abstract base class that can be used in conjunction with ChannelDataAlgebra.
	"""
	def _Calculate(self, a, b):
		return tuple(numpy.multiply(a, b))

	def _GetLabel(self):
		return "Product"



class Divide:
	"""
	Abstract base class that can be used in conjunction with ChannelDataAlgebra.
	"""
	def _Calculate(self, a, b):
		if min(b) == 0.0 == max(b):
			if min(a) == 0.0 == max(a):
				return (1.0,) * len(a)
			else:
				raise ZeroDivisionError("A non zero data set may not be divided by a zero data set")
		return tuple(numpy.divide(a, b))

	def _GetLabel(self):
		return "Quotient"

