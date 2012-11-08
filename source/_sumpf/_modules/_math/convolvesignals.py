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

import numpy
import sumpf


class ConvolveSignals(object):
	"""
	A module for the convolution of Signals.
	It's basically a wrapper for numpy.convolve.

	The input Signals must have the same sampling rate.
	If one Signal has more channels than the other, the surplus channels will be
	left out of the resulting Signal.
	"""

	FULL = "full"
	SAME = "same"
	VALID = "valid"

	def __init__(self, signal1=None, signal2=None, mode=None):
		"""
		@param signal1: the first Signal-instance for convolution
		@param signal2: the second Signal-instance for convolution
		@param mode: either None or one of the available convolution modes (See SetConvolutionMode for details)
		"""
		if signal1 is None:
			signal1 = sumpf.Signal()
		if signal2 is None:
			signal2 = sumpf.Signal()
		if mode is None:
			mode = ConvolveSignals.FULL
		self.__signal1 = signal1
		if signal2.IsEmpty():
			self.__signal2 = signal2
		else:
			self.SetInput2(signal2)
		self.SetConvolutionMode(mode)

	@sumpf.Input(sumpf.Signal, "GetOutput")
	def SetInput1(self, signal):
		"""
		Sets the first Signal for convolution.
		@param signal: the first Signal instance for convolution
		"""
		self.__signal1 = signal

	@sumpf.Input(sumpf.Signal, "GetOutput")
	def SetInput2(self, signal):
		"""
		Sets the second Signal for convolution.
		@param signal: the second Signal instance for convolution
		"""
		self.__signal2 = signal

	@sumpf.Input(type(FULL), "GetOutput")
	def SetConvolutionMode(self, mode):
		"""
		Sets the convolution mode.
		The mode can be one of the following:
		  - ConvolveSignals.FULL
		      for full length convolution. If M and N are the lengths of the
		      input signals, the output's length will be M+N-1.
		  - ConvolveSignals.SAME
		      for an output with the same length as the longer input.
		      (output_length=max(M,N))
		  - ConvolveSignals.VALID
		  for an output length of max(M,N)-min(M,N)+1
		See help(numpy.convolve) for more details.
		@param mode: one of the modes from the description
		"""
		if mode not in ["full", "same", "valid"]:
			raise ValueError("Unrecognized Mode: " + str(mode))
		self.__mode = mode

	@sumpf.Output(sumpf.Signal)
	def GetOutput(self):
		"""
		Calculates and returns the Signal resulting from the convolution.
		The resulting Signal will have as many channels as the input Signal with
		the least channels.
		@retval : a Signal whose channels are the result of the convolution
		"""
		if self.__signal1.GetSamplingRate() != self.__signal2.GetSamplingRate():
			raise ValueError("The given signals have a different sampling rate")
		else:
			maxc = min(len(self.__signal1.GetChannels()), len(self.__signal2.GetChannels()))
			channels = []
			labels = []
			for c in range(maxc):
				channel = tuple(numpy.convolve(self.__signal1.GetChannels()[c], self.__signal2.GetChannels()[c], mode=self.__mode))
				channels.append(channel)
				labels.append("Convolution " + str(c + 1))
			return sumpf.Signal(channels=channels, samplingrate=self.__signal1.GetSamplingRate(), labels=labels)

