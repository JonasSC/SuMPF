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

import math
import numpy
import sumpf

def get_hermite_polynomial(order, variance):
	if order == 0:
		return (1.0,)
	else:
		lower_order_polynomial = get_hermite_polynomial(order=order - 1, variance=variance)
		increased_order = (0.0,) + lower_order_polynomial
		derivative = []
		for o in range(len(lower_order_polynomial) - 1):
			d = lower_order_polynomial[o + 1] * (o + 1) * variance
			derivative.append(d)
		while len(derivative) < len(increased_order):
			derivative.append(0.0)
		return tuple(numpy.subtract(increased_order, derivative))

def calculate_hermite_power(index, order, excitation_powers, excitation_variance):
	polynomial = get_hermite_polynomial(order=order, variance=excitation_variance)
	result = sumpf.modules.ConstantSignalGenerator(value=polynomial[0], samplingrate=excitation_powers[0][0].GetSamplingRate(), length=len(excitation_powers[0][0])).GetSignal()
	for i in range(1, len(polynomial)):
		if polynomial[i] != 0.0:
			result = result + (excitation_powers[index][i - 1] * polynomial[i])
	return result

def calculate_combination(normalized_permutation, excitation_powers, excitation_variance):
	result = sumpf.modules.ConstantSignalGenerator(value=1.0, samplingrate=excitation_powers[0][0].GetSamplingRate(), length=len(excitation_powers[0][0])).GetSignal()
	for i in normalized_permutation:
		power = calculate_hermite_power(index=i,
		                                order=normalized_permutation[i],
		                                excitation_powers=excitation_powers,
		                                excitation_variance=excitation_variance)
		result = result * power
	return result

def calculate_weighting_coefficient(combination, resampled_response, nonlinear_order, normalized_permutation, excitation_variance):
	resampled_combination = sumpf.modules.ResampleSignal(signal=combination,
	                                                     samplingrate=2 * combination.GetSamplingRate(),
	                                                     algorithm=sumpf.modules.ResampleSignal.SPECTRUM).GetOutput()
	multiplied = resampled_combination * resampled_response
	mean = sumpf.modules.SignalMean(signal=multiplied).GetMean()[0]
	a = excitation_variance ** nonlinear_order
	b = 1.0
	for o in normalized_permutation.values():
		b *= math.factorial(o)
#	#####
#	squared = resampled_combination * resampled_combination
#	mean2 = sumpf.modules.SignalMean(signal=squared).GetMean()[0]
#	print "w", b, mean / (a * b), mean / (a * mean2), mean / mean2
#	return mean / mean2
	return mean / (a * b)

