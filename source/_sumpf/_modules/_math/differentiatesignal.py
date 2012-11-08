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


class DifferentiateSignal(object):
	"""
	A module for calculating the derivative of a Signal.
	"""
	def __init__(self, signal=None):
		"""
		@param signal: the input Signal
		"""
		if signal is None:
			self.__signal = sumpf.Signal()
		else:
			self.__signal = signal

	@sumpf.Input(sumpf.Signal, "GetOutput")
	def SetInput(self, signal):
		"""
		Sets the input Signal.
		@param signal: the input Signal
		"""
		self.__signal = signal

	@sumpf.Output(sumpf.Signal)
	def GetOutput(self):
		"""
		Returns the output Signal, which is the derivative of the input Signal.
		@retval : a Signal which is the derivative of the input Signal
		"""
		result = []
		for c in self.__signal.GetChannels():
			diffs = sumpf.helper.differentiate(c)
			derivative = tuple(numpy.multiply(diffs, self.__signal.GetSamplingRate()))
			result.append(derivative)
		return sumpf.Signal(channels=result, samplingrate=self.__signal.GetSamplingRate(), labels=self.__signal.GetLabels())

