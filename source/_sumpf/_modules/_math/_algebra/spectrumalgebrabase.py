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
from . import channeldataalgebra


class SpectrumAlgebra(channeldataalgebra.ChannelDataAlgebra):
	"""
	A base class for calculations with two Spectrum instances.
	"""
	def __init__(self, spectrum1=None, spectrum2=None):
		"""
		All parameters are optional.
		@param spectrum1: the first Spectrum-instance for the calculation
		@param spectrum2: the second Spectrum-instance for the calculation
		"""
		if spectrum1 is None:
			spectrum1 = sumpf.Spectrum()
		if spectrum2 is None:
			spectrum2 = sumpf.Spectrum()
		channeldataalgebra.ChannelDataAlgebra.__init__(self, spectrum1, spectrum2)

	@sumpf.Input(sumpf.Spectrum, "GetOutput")
	def SetInput1(self, spectrum):
		"""
		Sets the first Spectrum for the calculation.
		@param spectrum: the first Spectrum-instance for the calculation
		"""
		self._SetDataset1(spectrum)

	@sumpf.Input(sumpf.Spectrum, "GetOutput")
	def SetInput2(self, spectrum):
		"""
		Sets the second Spectrum for the calculation.
		@param spectrum: the second Spectrum-instance for the calculation
		"""
		self._SetDataset2(spectrum)

	@sumpf.Output(sumpf.Spectrum)
	def GetOutput(self):
		"""
		Calculates and returns the Spectrum resulting from the calculation.
		The resulting Spectrum will have as many channels as the input Spectrum
		with the least channels.
		@retval : a Spectrum whose channels are the result of the calculation
		"""
		resolution = self._GetDataset1().GetResolution()
		if self._GetDataset1().IsEmpty():
			resolution = self._GetDataset2().GetResolution()
		if not self._GetDataset1().IsEmpty() and not self._GetDataset2().IsEmpty():
			if self._GetDataset1().GetResolution() != self._GetDataset2().GetResolution():
				raise ValueError("The given spectrums have a different resolution")
			if len(self._GetDataset1()) != len(self._GetDataset2()):
				raise ValueError("The given spectrums have a different length")
		return sumpf.Spectrum(channels=self._GetChannels(), resolution=resolution, labels=self._GetLabels())

