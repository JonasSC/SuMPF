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

def binomial_coefficient(n, k):
	"""
	This function calculates the binomial coefficient of n over k. This is the
	number of choices to pick k items out of a set of n items.
	@param n, k: two integers
	@retval : the binomial coefficient as an integer
	"""
	if k < 0 or k > n:
		return 0
	if k > n - k:
		k = n - k
	if k == 0 or n <= 1:
		return 1
	result = 1.0
	m = n + 1.0
	for i in range(1, k + 1):
		result *= (m - i) / i
	return int(round(result))

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
		import warnings
		warnings.warn("\n\tThe sumpf.helper.differentiate function calculates the derivative by subtracting\n\tthe two neighboring samples of the sample of which the derivative shall be calculated.\n\tThis is a moving average of the derivative, which is basically a bandpass rather\n\tthan the expected highpass.")
		result = []
		result.append(float(sequence[1] - sequence[0]))
		for i in range(1, len(sequence) - 1):
			result.append((sequence[i + 1] - sequence[i - 1]) / 2.0)
		result.append(float(sequence[-1] - sequence[-2]))
		return result
#		result = []
#		def get_derivative(y0, y1, y2):
#			c = y1
#			a = (y0 + y2) / 2.0 - c
#			b = y2 - c - a
#			return b
#		result.append(get_derivative(sequence[0], sequence[0], sequence[1]))
#		for i in range(1, len(sequence) - 1):
#			result.append(get_derivative(sequence[i - 1], sequence[i], sequence[i + 1]))
#		result.append(get_derivative(sequence[-2], sequence[-1], sequence[-1]))
#		return result

