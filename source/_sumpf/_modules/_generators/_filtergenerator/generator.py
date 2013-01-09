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

import sumpf
from ..spectrumgenerator import SpectrumGenerator
from .filters import ButterworthLowpass, ButterworthHighpass, ChebyshevLowpass, \
                     ChebyshevHighpass, Bandpass, Bandstop, PinkSlope, RedSlope, \
                     AWeighting, CWeighting
from .filterbase import Filter


class FilterGenerator(SpectrumGenerator):
	"""
	Instances of this class generate a Spectrum from a set of given filters.
	The available filter classes are accessible as static attributes of this class.
	The spectrum can be defined by adding instances of these classes with the
	Add-, Remove- and ReplaceFilter methods.
	"""
	BUTTERWORTH_LOWPASS = ButterworthLowpass
	BUTTERWORTH_HIGHPASS = ButterworthHighpass
	CHEBYSHEV_LOWPASS = ChebyshevLowpass
	CHEBYSHEV_HIGHPASS = ChebyshevHighpass
	BANDPASS = Bandpass
	BANDSTOP = Bandstop
	PINK_SLOPE = PinkSlope
	RED_SLOPE = RedSlope
	A_WEIGHTING = AWeighting
	C_WEIGHTING = CWeighting

	def __init__(self, resolution=None, length=None):
		"""
		@param resolution: the resolution of the created spectrum in Hz
		@param length: the number of samples of the spectrum
		"""
		SpectrumGenerator.__init__(self, resolution, length)
		self.__filters = sumpf.helper.MultiInputData()

	@sumpf.MultiInput(data_type=Filter, remove_method="RemoveFilter", observers="GetSpectrum", replace_method="ReplaceFilter")
	def AddFilter(self, filter):
		"""
		Adds a filter instance to the generator.
		@param filter: the filter instance that shall be added
		@retval : the id under which the filter instance is stored
		"""
		return self.__filters.Add(filter)

	def RemoveFilter(self, filter_id):
		"""
		Removes the filter instance that is stored under the given id from the generator.
		@param filter_id: the id of the filter that shall be removed
		"""
		self.__filters.Remove(filter_id)

	def ReplaceFilter(self, filter_id, filter):
		"""
		Replaces the filter instance that is stored under the given id from the
		generator with a new filter instance.
		@param filter_id: the id of the filter that shall be replaced
		@param filter: the new filter instance that shall be stored under the given id
		"""
		self.__filters.Replace(filter_id, filter)

	def _GetSample(self, f):
		"""
		This method generates a sample at the frequency f and returns it.
		@param f: the frequency of the sample in Hz
		@retval : the value of the filter's transfer function at the given frequency
		"""
		sample = 1.0
		for factor in self.__filters.GetData():
			sample *= factor.GetFactor(f)
		return sample

	def _GetLabel(self):
		"""
		Returns the label for the generated channel.
		@retval : the string label
		"""
		return "Filter"

