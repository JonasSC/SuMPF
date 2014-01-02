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

import math
from .filterbase import Filter, FilterWithCoefficients, FilterWithSlope, Weighting


class ButterworthLowpass(FilterWithCoefficients):
	"""
	Filter class for a Butterworth lowpass.
	"""
	def __init__(self, frequency=1000.0, order=1):
		"""
		@param frequency: the corner frequency of the filter
		@param order: the order of the filter as an integer
		"""
		coefficients = []
		n = float(order)
		if order % 2 == 0:
			for i in range(1, order // 2 + 1):
				b1 = 2.0 * math.cos((2 * i - 1) * math.pi / (2 * n))
				coefficients.append(([1.0], [1.0, b1, 1.0]))
		else:
			coefficients.append(([1.0], [1.0, 1.0]))
			for i in range(2, (order + 1) // 2 + 1):
				b1 = 2.0 * math.cos((i - 1) * math.pi / n)
				coefficients.append(([1.0], [1.0, b1, 1.0]))
		FilterWithCoefficients.__init__(self, frequency=frequency, coefficients=coefficients, transform=False)



class ButterworthHighpass(ButterworthLowpass):
	"""
	Filter class for a Butterworth highpass.
	"""
	def __init__(self, frequency=1000.0, order=1):
		"""
		@param frequency: the corner frequency of the filter
		@param order: the order of the filter as an integer
		"""
		ButterworthLowpass.__init__(self, frequency=frequency, order=order)
		self._transform = True



class BesselLowpass(FilterWithCoefficients):
	"""
	Filter class for a Bessel lowpass.
	"""
	def __init__(self, frequency=1000.0, order=1):
		"""
		@param frequency: the corner frequency of the filter
		@param order: the order of the filter as an integer
		"""
		coefficients = []
		for k in range(order + 1):
			numerator = math.factorial(2.0 * order - k)
			denominator = (2.0 ** (order - k)) * math.factorial(k) * math.factorial(order - k)
			coefficients.append(numerator / denominator)
		FilterWithCoefficients.__init__(self, frequency=frequency, coefficients=[[[coefficients[0]], coefficients]], transform=False)



class BesselHighpass(BesselLowpass):
	"""
	Filter class for a Bessel highpass.
	"""
	def __init__(self, frequency=1000.0, order=1):
		"""
		@param frequency: the corner frequency of the filter
		@param order: the order of the filter as an integer
		"""
		BesselLowpass.__init__(self, frequency=frequency, order=order)
		self._transform = True



class ChebyshevLowpass(FilterWithCoefficients):
	"""
	Filter class for a Chebyshev lowpass.
	"""
	def __init__(self, frequency=1000.0, order=1, ripple=3.0):
		"""
		@param frequency: the corner frequency of the filter
		@param order: the order of the filter as an integer
		@param ripple: the float value of the maximum ripple in dB
		"""
		coefficients = []
		n = float(order)
		g = math.asinh(1.0 / (math.sqrt((10.0 ** (ripple / 10.0)) - 1.0))) / n
		if order % 2 == 0:
			for i in range(1, order // 2 + 1):
				b2 = 1 / ((math.cosh(g) ** 2) - (math.cos((2 * i - 1) * math.pi / (2 * n)) ** 2))
				b1 = 2.0 * b2 * math.sinh(g) * math.cos((2 * i - 1) * math.pi / (2 * n))
				coefficients.append(([1.0], [1.0, b1, b2]))
		else:
			b1 = 1.0 / math.sinh(g)
			coefficients.append(([1.0], [1.0, b1]))
			for i in range(2, (order + 1) // 2 + 1):
				b2 = 1 / ((math.cosh(g) ** 2) - (math.cos((i - 1) * math.pi / n) ** 2))
				b1 = 2.0 * b2 * math.sinh(g) * math.cos((i - 1) * math.pi / n)
				coefficients.append(([1.0], [1.0, b1, b2]))
		FilterWithCoefficients.__init__(self, frequency=frequency, coefficients=coefficients, transform=False)



class ChebyshevHighpass(ChebyshevLowpass):
	"""
	Filter class for a Chebyshev highpass.
	"""
	def __init__(self, frequency=1000.0, order=1, ripple=3.0):
		"""
		@param frequency: the corner frequency of the filter
		@param order: the order of the filter as an integer
		@param ripple: the float value of the maximum ripple in dB
		"""
		ChebyshevLowpass.__init__(self, frequency=frequency, order=order, ripple=ripple)
		self._transform = True



class Bandpass(FilterWithCoefficients):
	"""
	A filter class for a second order band pass that is normalized to have a
	gain of 1.0 at the resonant frequency.
	"""
	def __init__(self, frequency=1000.0, q_factor=1.0):
		"""
		@param frequency: the resonant frequency of the filter
		@param q_factor: the Q-factor of the resonance
		"""
		a0 = 0.0
		a1 = 1.0 / float(q_factor)
		b0 = 1.0
		b1 = a1
		b2 = 1.0
		FilterWithCoefficients.__init__(self, frequency=frequency, coefficients=[([a0, a1], [b0, b1, b2])], transform=False)



class Bandstop(FilterWithCoefficients):
	"""
	A filter class for a second order band stop or notch filter.
	"""
	def __init__(self, frequency=1000.0, q_factor=1.0):
		"""
		@param frequency: the resonant frequency of the filter
		@param q_factor: the Q-factor of the resonance
		"""
		a0 = 1.0
		a1 = 0.0
		a2 = 1.0
		b0 = 1.0
		b1 = 1.0 / q_factor
		b2 = 1.0
		FilterWithCoefficients.__init__(self, frequency=frequency, coefficients=[([a0, a1, a2], [b0, b1, b2])], transform=False)



class PinkSlope(FilterWithSlope):
	"""
	Filter class for a filter whose magnitude falls proportional to 1/f.
	A start frequency can be specified for this filter. The factor for every
	frequency below the start frequency will be 1.0. Above the frequency, the
	filter factors will fall 1/f.
	"""
	def __init__(self, start=0.0):
		"""
		@param start: the start frequency for the slope
		"""
		FilterWithSlope.__init__(self, start=start, alpha=1.0)



class RedSlope(FilterWithSlope):
	"""
	Filter class for a filter whose magnitude falls proportional to 1/f.
	A start frequency can be specified for this filter. The factor for every
	frequency below the start frequency will be 1.0. Above the frequency, the
	filter factors will fall 1/f.
	"""
	def __init__(self, start=0.0):
		"""
		@param start: the start frequency for the slope
		"""
		FilterWithSlope.__init__(self, start=start, alpha=2.0)



class AWeighting(Weighting):
	"""
	Filter class for an A-weighting filter.
	"""
	def _GetWeighting(self, frequency):
		"""
		This calculates the complex factor by which the frequency shall be scaled
		and phase shifted. In contrast to GetFactor, the factors that are returned
		by this function, need not be normalized to be 1.0 at 1000Hz.
		@param frequency: the frequency for which the factor shall be calculated
		@retval : the value of the filter's transfer function at the given frequency
		"""
		s = 2.0j * math.pi * frequency
		omega1 = -20.6 * 2.0 * math.pi
		omega2 = -107.7 * 2.0 * math.pi
		omega3 = -737.9 * 2.0 * math.pi
		omega4 = -12200.0 * 2.0 * math.pi
		pole1 = (s - omega1) ** 2
		pole2 = s - omega2
		pole3 = s - omega3
		pole4 = (s - omega4) ** 2
		return s ** 4 / (pole1 * pole2 * pole3 * pole4)



class CWeighting(Weighting):
	"""
	Filter class for a C-weighting filter.
	"""
	def _GetWeighting(self, frequency):
		"""
		This calculates the complex factor by which the frequency shall be scaled
		and phase shifted. In contrast to GetFactor, the factors that are returned
		by this function, need not be normalized to be 1.0 at 1000Hz.
		@param frequency: the frequency for which the factor shall be calculated
		@retval : the value of the filter's transfer function at the given frequency
		"""
		s = 2.0j * math.pi * frequency
		omega1 = -20.6 * 2.0 * math.pi
		omega2 = -12200 * 2.0 * math.pi
		pole1 = (s - omega1) ** 2
		pole2 = (s - omega2) ** 2
		return s ** 2 / (pole1 * pole2)



class ConstantGroupDelay(Filter):
	"""
	Filter class for a filter that adds a given group delay without affecting
	the magnitude of the Spectrum.
	"""
	def __init__(self, delay=0.0):
		"""
		@param delay: the group delay in seconds
		"""
		self.__delay = delay

	def GetFactor(self, frequency):
		"""
		This calculates the complex factor by which the frequency shall be scaled
		and phase shifted.
		@param frequency: the frequency for which the factor shall be calculated
		@retval : the value of the filter's transfer function at the given frequency
		"""
		return math.e ** (-1.0j * self.__delay * 2.0 * math.pi * frequency)

