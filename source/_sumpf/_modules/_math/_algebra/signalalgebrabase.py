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

import sumpf
from . import channeldataalgebra


class SignalAlgebra(channeldataalgebra.ChannelDataAlgebra):
	"""
	A base class for calculations with two Signal instances.
	"""
	def __init__(self, signal1=None, signal2=None):
		"""
		All parameters are optional
		@param signal1: the first Signal-instance for the calculation
		@param signal2: the second Signal-instance for the calculation
		"""
		if signal1 is None:
			signal1 = sumpf.Signal()
		if signal2 is None:
			signal2 = sumpf.Signal()
		channeldataalgebra.ChannelDataAlgebra.__init__(self, signal1, signal2)

	@sumpf.Input(sumpf.Signal, "GetOutput")
	def SetInput1(self, signal):
		"""
		Sets the first Signal for the calculation.
		@param signal: the first Signal-instance for the calculation
		"""
		self._SetDataset1(signal)

	@sumpf.Input(sumpf.Signal, "GetOutput")
	def SetInput2(self, signal):
		"""
		Sets the second Signal for the calculation.
		@param signal: the second Signal-instance for the calculation
		"""
		self._SetDataset2(signal)

	@sumpf.Output(sumpf.Signal)
	def GetOutput(self):
		"""
		Calculates and returns the Signal resulting from the calculation.
		The resulting Signal will have as many channels as the input Signal with
		the least channels.
		@retval : a Signal whose channels are the result of the calculation
		"""
		samplingrate = self._GetDataset1().GetSamplingRate()
		if self._GetDataset1().IsEmpty():
			samplingrate = self._GetDataset2().GetSamplingRate()
		if not self._GetDataset1().IsEmpty() and not self._GetDataset2().IsEmpty():
			if self._GetDataset1().GetSamplingRate() != self._GetDataset2().GetSamplingRate():
				raise ValueError("The given signals have a different sampling rate")
			if len(self._GetDataset1()) != len(self._GetDataset2()):
				raise ValueError("The given signals have a different length")
		return sumpf.Signal(channels=self._GetChannels(), samplingrate=samplingrate, labels=self._GetLabels())

