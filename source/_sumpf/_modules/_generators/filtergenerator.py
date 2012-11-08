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

import math
import sumpf
from .spectrumgenerator import SpectrumGenerator


class FilterGenerator(SpectrumGenerator):
	"""
	Instances of this class generate a spectrum for a specified filter.
	The filter are defined by a set of coefficients. This class also offers some
	common functions to generate these coefficients as static methods, like
	"Butterworth" or "Chebyshev".
	It is possible to give the coefficients of a lowpass filter and then generate
	a highpass from them. The Butterworth and Chebyshev functions return lowpass
	coefficients; if a highpass shall be created with them, the lowpass-to-highpass
	transformation has to be enabled.
	"""
	def __init__(self, frequency=1000.0, coefficients=[], transform=False, resolution=None, length=None):
		"""
		@param frequency: the cutoff- or resonant frequency of the filter in Hz
		@param coefficients: a list of tuples (a, b) where a and b are lists of coefficients (see SetCoefficients)
		@param transform: if True a lowpass-to-highpass-transformation will be done
		@param resolution: the resolution of the created spectrum in Hz
		@param length: the number of samples of the spectrum
		"""
		if length is None:
			length = sumpf.modules.ChannelDataProperties().GetSpectrumLength()
		if resolution is None:
			resolution = sumpf.modules.ChannelDataProperties().GetResolution()
		SpectrumGenerator.__init__(self, resolution, length)
		self.__frequency = float(frequency)
		self.__coefficients = coefficients
		self.__transform = transform

	def _GetSample(self, f):
		"""
		This method generates a sample at the frequency f and returns it.
		@param f: the frequency of the sample in Hz
		@retval : the value of the filter's transfer function at the given frequency
		"""
		s = 1.0j * f / self.__frequency
		sample = 1.0
		if self.__transform:
			if f == 0.0:
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

	def _GetLabel(self):
		"""
		Returns the label for the generated channel.
		@retval : the string label
		"""
		return "Filter"

	@sumpf.Input(list, "GetSpectrum")
	def SetCoefficients(self, coefficients):
		"""
		Sets the coefficients for the filter.
		The given coefficients shall be a list of tuples (a, b) where a is the
		list of coefficients for the numerator and b is the list of coefficients
		for the denominator.
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

		@param coefficients: a list of tuples (a, b) where a and b are lists of coefficients
		"""
		self.__coefficients = coefficients

	@sumpf.Input(float, "GetSpectrum")
	def SetFrequency(self, frequency):
		"""
		Sets the frequency for the filter.
		With low- and highpass filters this will be the cutoff frequency.
		With bandpass filters this will be the resonant frequency.
		@param frequency: the frequency in Hz as a float
		"""
		self.__frequency = float(frequency)

	@sumpf.Input(bool, "GetSpectrum")
	def SetLowpassToHighpassTransform(self, transform):
		"""
		Sets if a lowpass-to-highpass-transformation shall be done.
		@param transform: if True a lowpass-to-highpass-transformation will be done
		"""
		self.__transform = transform

	@staticmethod
	def Bandpass(q_factor=1.0):
		"""
		Static method that calculates and returns the coefficients for a
		normalized 2nd order Bandpass-filter.
		@param q_factor: the Q-factor of the resonance
		@retval : a list of tuples which are the coefficients for the filter
		"""
		Q = float(q_factor)
		a0 = 0.0
		a1 = 1.0 / Q
		b0 = 1.0
		b1 = a1
		b2 = 1.0
		return [([a0, a1], [b0, b1, b2])]

	@staticmethod
	def Butterworth(order=1):
		"""
		Static method that calculates and returns the coefficients for a
		normalized Butterworth-filter.
		@param order: the order of the filter as an integer
		@retval : a list of tuples which are the coefficients for the filter
		"""
		result = []
		n = float(order)
		if order % 2 == 0:
			for i in range(1, order // 2 + 1):
				b1 = 2.0 * math.cos((2 * i - 1) * math.pi / (2 * n))
				result.append(([1.0], [1.0, b1, 1.0]))
		else:
			result.append(([1.0], [1.0, 1.0]))
			for i in range(2, (order + 1) // 2 + 1):
				b1 = 2.0 * math.cos((i - 1) * math.pi / n)
				result.append(([1.0], [1.0, b1, 1.0]))
		return result

	@staticmethod
	def Chebyshev(order=1, ripple=3.0):
		"""
		Static method that calculates and returns the coefficients for a
		normalized Chebyshev-filter.
		@param order: the order of the filter as an integer
		@param ripple: the float value of the maximum ripple in dB
		@retval : a list of tuples which are the coefficients for the filter
		"""
		result = []
		n = float(order)
		g = math.asinh(1.0 / (math.sqrt((10.0 ** (ripple / 10.0)) - 1.0))) / n
		if order % 2 == 0:
			for i in range(1, order // 2 + 1):
				b2 = 1 / ((math.cosh(g) ** 2) - (math.cos((2 * i - 1) * math.pi / (2 * n)) ** 2))
				b1 = 2.0 * b2 * math.sinh(g) * math.cos((2 * i - 1) * math.pi / (2 * n))
				result.append(([1.0], [1.0, b1, b2]))
		else:
			b1 = 1.0 / math.sinh(g)
			result.append(([1.0], [1.0, b1]))
			for i in range(2, (order + 1) // 2 + 1):
				b2 = 1 / ((math.cosh(g) ** 2) - (math.cos((i - 1) * math.pi / n) ** 2))
				b1 = 2.0 * b2 * math.sinh(g) * math.cos((i - 1) * math.pi / n)
				result.append(([1.0], [1.0, b1, b2]))
		return result

