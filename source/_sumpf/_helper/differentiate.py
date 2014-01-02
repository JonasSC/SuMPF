# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2014 Jonas Schulte-Coerne
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

def differentiate(sequence):
	"""
	This function takes a sequence of numbers and calculates the derivative of it.
	The length of the result is the same as the length of the input.
	The result might have to be scaled by the gap between the sequence's samples.
	@param sequence: a list of numbers
	@retval : the derivative of the given list as a list of floats
	"""
	if len(sequence) == 0:
		return []
	elif len(sequence) == 1:
		return [0.0]
	else:
		result = []
		result.append(float(sequence[1] - sequence[0]))
		for i in range(1, len(sequence) - 1):
			result.append((sequence[i + 1] - sequence[i - 1]) / 2.0)
		result.append(float(sequence[-1] - sequence[-2]))
		return result

