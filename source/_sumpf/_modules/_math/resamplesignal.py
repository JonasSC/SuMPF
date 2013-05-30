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
import numpy
import scikits.samplerate


class ResampleSignal(object):
	"""
	A module for changing the sampling rate of a Signal.
	The sampling rate can be increased or decreased. It is not necessary that
	the output sampling rate is an integer fraction or multiple of the input
	sampling rate.
	"""
	def __init__(self, signal=None, samplingrate=None):
		"""
		All parameters are optional.
		@param signal: the input Signal that shall be resampled
		@param samplingrate: the desired sampling rate of the output Signal or None, to keep the sampling rate of the input Signal
		"""
		self.__signal = signal
		if signal is None:
			self.__signal = sumpf.Signal()
		self.__samplingrate = samplingrate

	@sumpf.Input(sumpf.Signal, "GetOutput")
	def SetInput(self, signal):
		"""
		Sets the input Signal that shall be resampled.
		@param signal: the input Signal that shall be resampled
		"""
		self.__signal = signal

	@sumpf.Input(float, "GetOutput")
	def SetSamplingRate(self, samplingrate):
		"""
		Sets the sampling rate of the output Signal.
		If the sampling rate is set to None, the input Signal will be passed
		to the output and no sampling rate conversion will be done.
		@param samplingrate: the desired sampling rate of the output Signal or None, to keep the sampling rate of the input Signal
		"""
		self.__samplingrate = samplingrate

	@sumpf.Output(sumpf.Signal)
	def GetOutput(self):
		"""
		Calculates the resampled output Signal and returns it.
		@retval : a Signal instance with the given sampling rate
		"""
		if self.__samplingrate is None:
			return self.__signal
		else:
			factor = self.__samplingrate / self.__signal.GetSamplingRate()
			channels = []
			for c in self.__signal.GetChannels():
				in_channel = numpy.array(c)
				out_channel = scikits.samplerate.resample(in_channel, factor, 'sinc_best')
				channels.append(tuple(out_channel))
			return sumpf.Signal(channels=tuple(channels), samplingrate=self.__samplingrate, labels=self.__signal.GetLabels())

