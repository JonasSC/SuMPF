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
from .signalgenerator import SignalGenerator


class WindowFunction(object):
	"""
	Abstract base class that can be used to define window functions which can
	be passed to a WindowGenerator.
	The instances must be call-able with the length of the window as a parameter.
	The call must return a tuple of samples with the given length. This tuple has
	to contain both the rising and the falling edge of the window.
	The samples must be between 0.0 and 1.0
	Only if the length is odd, the middle sample contains the 1.0.
	Like this the WindowFunction instances behave much like the window functions
	in numpy. With the one exception that the instances only take the length
	parameter. Additional parameters (e.g. beta for the kaiser window) can be
	stored in a constructor of a derived class.
	"""
	def __call__(self, length):
		"""
		Virtual base method that makes the instance call-able.
		@param length: the full length of the window (in samples) for both the rising and the falling edge
		@retval : a tuple of samples with the rising and the falling edge of the window
		"""
		raise NotImplementedError("This method should have been overridden in a derived class")



class WindowGenerator(SignalGenerator):
	"""
	A class whose instances generate Signals that fall or raise according to a
	given window function.
	The resulting Signal does not contain acoustic data. It is mainly used to be
	multiplied with a sound Signal, to fade in or out the sound Signal without creating
	much unwanted distortion.
	The maximum of the window function will always be 1.0. It can be changed by
	sending the resulting Signal through a sumpf.AmplifySignal module.
	The resulting Signal will have one channel.
	"""
	def __init__(self, interval=(0, 1), raising=False, function=None, samplingrate=None, length=None):
		"""
		@param interval: a tuple (a, b) of integers where a is the index of first sample of the window and b is the index of the first sample after the window
		@param raising: True if the window shall be raising, False otherwise
		@param function: a WindowFunction instance
		@param samplingrate: the sampling rate in Hz
		@param length: the number of samples of the signal
		"""
		SignalGenerator.__init__(self, samplingrate=samplingrate, length=length)
		self.__interval = interval
		self.__raising = raising
		if function is None:
			self.__function = WindowGenerator.Hanning()
		else:
			self.__function = function

	def _GetSamples(self):
		"""
		Generates the samples of the window and returns them as a tuple.
		@retval : a tuple of samples
		"""
		samples = []
		value = 1.0
		if self.__raising:
			value = 0.0
		for i in range(self.__interval[0]):
			samples.append(value)
		width = self.__interval[1] - self.__interval[0]
		window = self.__function(2 * width)
		if self.__raising:
			window = window[0:width]
		else:
			window = window[width:]
		for s in window:
			samples.append(s)
		value = 1.0 - value
		for i in range(self._length - self.__interval[1]):
			samples.append(value)
		return tuple(samples[0:self._length])

	def _GetLabel(self):
		"""
		Returns the label for the generated channel.
		@retval : the string label
		"""
		return "Window"

	@sumpf.Input(tuple, "GetSignal")
	def SetInterval(self, interval):
		"""
		An interval in which the samples of the output Signal shall be falling
		(or raising) according to the given window function. Outside this
		interval, all samples will be 0.0 or 1.0 respectively.
		@param interval: a tuple (a, b) of integers where a is the index of first sample of the window and b is the index of the first sample after the window
		"""
		if interval[0] <= interval[1]:
			self.__interval = interval
		else:
			self.__interval = (interval[1], interval[0])

	@sumpf.Input(bool, "GetSignal")
	def SetRaising(self, raising):
		"""
		Sets if the window is raising or falling.
		If the window is raising, the samples of the output Signal will start
		with 0.0. During the given interval the samples will be raising
		according to the shape of the given window function. After the interval
		the samples will be 1.0.
		If the window is not raising, the samples of the output Signal will
		start at 1.0, during the interval they will fall and after the interval
		all samples will be 0.0.
		@param raising: True if the window shall be raising, False otherwise
		"""
		self.__raising = raising

	@sumpf.Input(WindowFunction, "GetSignal")
	def SetFunction(self, function):
		"""
		Sets the function that defines the shape of the window.
		@param function: a WindowFunction instance
		"""
		self.__function = function

	class Bartlett(WindowFunction):
		"""
		Wrapper for the bartlett window function in numpy.
		"""
		def __call__(self, length):
			"""
			@param length: the full length of the window (in samples) for both the rising and the falling edge
			@retval : a tuple of samples with the rising and the falling edge of the window
			"""
			return numpy.bartlett(length)

	class Blackman(WindowFunction):
		"""
		Wrapper for the blackman window function in numpy.
		"""
		def __call__(self, length):
			"""
			@param length: the full length of the window (in samples) for both the rising and the falling edge
			@retval : a tuple of samples with the rising and the falling edge of the window
			"""
			return numpy.blackman(length)

	class Hamming(WindowFunction):
		"""
		Wrapper for the hamming window function in numpy.
		"""
		def __call__(self, length):
			"""
			@param length: the full length of the window (in samples) for both the rising and the falling edge
			@retval : a tuple of samples with the rising and the falling edge of the window
			"""
			return numpy.hamming(length)

	class Hanning(WindowFunction):
		"""
		Wrapper for the hanning window function in numpy.
		"""
		def __call__(self, length):
			"""
			@param length: the full length of the window (in samples) for both the rising and the falling edge
			@retval : a tuple of samples with the rising and the falling edge of the window
			"""
			return numpy.hanning(length)

	class Kaiser(WindowFunction):
		"""
		Wrapper for the kaiser window function in numpy.
		"""
		def __init__(self, beta):
			"""
			A constructor to store the beta parameter for the numpy kaiser function.

			The following table is copied from the numpy documentation:
			beta	Window shape
			0		Rectangular
			5		Similar to a Hamming
			6		Similar to a Hanning
			8.6		Similar to a Blackman

			@param beta: the beta parameter for the numpy.kaiser function
			"""
			self.__beta = beta
		def __call__(self, length):
			"""
			@param length: the full length of the window (in samples) for both the rising and the falling edge
			@retval : a tuple of samples with the rising and the falling edge of the window
			"""
			return numpy.kaiser(length, self.__beta)

