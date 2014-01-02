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

class Filter(object):
	"""
	An abstract base class for filter classes that generate a complex weighting
	factor for a given frequency.
	"""
	def GetFactor(self, frequency):
		"""
		This calculates the complex factor by which the frequency shall be scaled
		and phase shifted.
		@param frequency: the frequency for which the factor shall be calculated
		@retval : the value of the filter's transfer function at the given frequency
		"""
		raise NotImplementedError("This method should have been overridden in a derived class")



class FilterWithCoefficients(Filter):
	"""
	An abstract base class for filter classes that generate the complex weighting
	factor for a given frequency, from a set of laplace coefficients.
	The coefficients shall be a list of tuples (a, b) where a is the list of
	coefficients for the numerator and b is the list of coefficients for the
	denominator.
	As many filter polynomials give their coefficients in product form, this
	method takes a list of tuples. The polynomials created from these tuples
	will be multiplied.

	In pseudo Python and even more pseudo Mathematics:
	n := len(coefficients)
	G(s) := the transfer function of the complete filter
	wc := the cutoff frequency in radians (2*pi*self.__frequency)
	then is:
	G(s) = G0(s) * G1(s) * G2(s) * ... Gi(s) ... * Gn(s)
	with:
	a = coefficients[i][0]
	b = coefficients[i][1]
	Gi(s) = (a[0] + (s/wc)*a[1] + ((s/wc)**2)*a[2] + ...) / (b[0] + (s/wc)*b[1] + ((s/wc)**2)*b[2] + ...)
	or with lowpass-to-highpass-transformation:
	Gi(s) = (a[0] + (wc/s)*a[1] + ((wc/s)**2)*a[2] + ...) / (b[0] + (wc/s)*b[1] + ((wc/s)**2)*b[2] + ...)
	"""
	def __init__(self, frequency, coefficients, transform):
		"""
		@param frequency: the corner or resonant frequency of the filter
		@param coefficients: a list of tuples (a, b) where a and b are lists of coefficients
		@param transform: True, if a lowpass-to-highpass transformation shall be made. False otherwise
		"""
		self.__frequency = frequency
		self.__coefficients = coefficients
		self._transform = transform

	def GetFactor(self, frequency):
		"""
		This calculates the complex factor by which the frequency shall be scaled
		and phase shifted.
		@param frequency: the frequency for which the factor shall be calculated
		@retval : the value of the filter's transfer function at the given frequency
		"""
		s = 1.0j * frequency / self.__frequency
		sample = 1.0
		if self._transform:
			if frequency == 0.0:
				return 0.0
			else:
				s = 1.0 / s
		for c in self.__coefficients:
			numerator = 0.0
			for i in range(len(c[0])):
				numerator += c[0][i] * (s ** i)
			denominator = 0.0
			for i in range(len(c[1])):
				denominator += c[1][i] * (s ** i)
			sample *= numerator / denominator
		return sample



class FilterWithSlope(Filter):
	"""
	An abstract base class for filters that fall with a given slope (for example 1/f)
	For these filters, a start frequency can be specified. The factor for every
	frequency below the start frequency will be 1.0. Above the frequency, the
	filter factors will fall with the given slope.
	"""
	def __init__(self, start, alpha):
		"""
		@param start: the start frequency for the slope
		@param alpha: the exponent for the frequency in the formula for the calculation of the filter factor ( 1/(f**aplha) )
		"""
		self.__start = start
		self.__alpha = alpha

	def GetFactor(self, frequency):
		"""
		This calculates the complex factor by which the frequency shall be scaled
		and phase shifted.
		@param frequency: the frequency for which the factor shall be calculated
		@retval : the value of the filter's transfer function at the given frequency
		"""
		if frequency <= self.__start:
			return 1.0
		elif self.__start == 0.0:
			return 1.0 / (frequency ** self.__alpha)
		else:
			return 1.0 / (frequency ** self.__alpha) / (1.0 / (self.__start ** self.__alpha))



class Weighting(Filter):
	"""
	An abstract base class for weighting functions such as the A- or C-weighting.
	These functions will be normalized to have a magnitude of 1.0 at 1000Hz.
	"""
	def __init__(self):
		self.__factor = 1.0 / self._GetWeighting(frequency=1000.0)

	def GetFactor(self, frequency):
		"""
		This calculates the complex factor by which the frequency shall be scaled
		and phase shifted.
		@param frequency: the frequency for which the factor shall be calculated
		@retval : the value of the filter's transfer function at the given frequency
		"""
		return self.__factor * self._GetWeighting(frequency=frequency)

	def _GetWeighting(self, frequency):
		"""
		This calculates the complex factor by which the frequency shall be scaled
		and phase shifted. In contrast to GetFactor, the factors that are returned
		by this function, need not be normalized to be 1.0 at 1000Hz.
		@param frequency: the frequency for which the factor shall be calculated
		@retval : the value of the filter's transfer function at the given frequency
		"""
		raise NotImplementedError("This method should have been overridden in a derived class")

