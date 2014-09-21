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

import sumpf
from ..spectrumgenerator import SpectrumGenerator
from .filters import Constant, Rectangle, \
                     ButterworthLowpass, ButterworthHighpass, BesselLowpass, \
                     BesselHighpass, ChebyshevLowpass, ChebyshevHighpass, \
                     Bandpass, Bandstop, LaguerreFunction, PinkSlope, RedSlope, \
                     Derivative, AWeighting, CWeighting, ConstantGroupDelay, \
                     FilterWithCoefficients
from .filterbase import Filter


class FilterGenerator(SpectrumGenerator):
	"""
	Instances of this class generate a Spectrum from a given filter function. This
	filter function will be sampled with the given frequency resolution and the
	number of samples, that are given as the length of the output Spectrum.
	The available filter classes are accessible as static attributes of this class.
	"""
	CONSTANT = Constant
	RECTANGLE = Rectangle
	BUTTERWORTH_LOWPASS = ButterworthLowpass
	BUTTERWORTH_HIGHPASS = ButterworthHighpass
	BESSEL_LOWPASS = BesselLowpass
	BESSEL_HIGHPASS = BesselHighpass
	CHEBYSHEV_LOWPASS = ChebyshevLowpass
	CHEBYSHEV_HIGHPASS = ChebyshevHighpass
	BANDPASS = Bandpass
	BANDSTOP = Bandstop
	LAGUERRE_FUNCTION = LaguerreFunction
	PINK_SLOPE = PinkSlope
	RED_SLOPE = RedSlope
	DERIVATIVE = Derivative
	A_WEIGHTING = AWeighting
	C_WEIGHTING = CWeighting
	CONSTANT_GROUP_DELAY = ConstantGroupDelay
	FILTER_WITH_COEFFICIENTS = FilterWithCoefficients

	def __init__(self, filterfunction=Constant(), resolution=None, length=None):
		"""
		@param filterfunction: the filter function that shall be sampled by this generator
		@param resolution: the resolution of the created spectrum in Hz
		@param length: the number of samples of the spectrum
		"""
		SpectrumGenerator.__init__(self, resolution=resolution, length=length)
		self.__filter = filterfunction

	@sumpf.Input(Filter, "GetSpectrum")
	def SetFilter(self, filterfunction):
		"""
		Sets the filter function that shall be sampled.
		@param filterfunction: the filter function that shall be sampled by this generator
		"""
		self.__filter = filterfunction

	def _GetSample(self, f):
		"""
		This method generates a sample at the frequency f and returns it.
		@param f: the frequency of the sample in Hz
		@retval : the value of the filter's transfer function at the given frequency
		"""
		return self.__filter.GetFactor(frequency=f, resolution=self._resolution, length=self._length)

	def _GetLabel(self):
		"""
		Returns the label for the generated channel.
		@retval : the string label
		"""
		return "Filter"

