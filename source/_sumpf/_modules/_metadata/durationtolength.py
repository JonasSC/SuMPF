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


class DurationToLength(object):
	"""
	A module that converts a duration in seconds to a length in number of samples.
	This way the length of a Signal can be set in a more intuitive way. Furthermore
	the duration of a Signal can be decoupled from its sampling rate.
	"""
	def __init__(self, duration=None, samplingrate=None):
		"""
		Both parameters are optional. If they are not given, they are taken from
		the config.
		@param duration: a duration in seconds as a float
		@param samplingrate: the sampling rate for which the length shall be calculated
		"""
		if samplingrate is None:
			samplingrate = sumpf.config.get("default_samplingrate")
		self.__samplingrate = float(samplingrate)
		if duration is None:
			duration = sumpf.config.get("default_signal_length") / self.__samplingrate
		self.__duration = float(duration)

	@sumpf.Output(int)
	def GetLength(self):
		"""
		Returns the length of a Signal that has been calculated for the given
		duration and sampling rate.
		@retval : the length as an integer
		"""
		return int(round(self.__duration * self.__samplingrate))

	@sumpf.Input(float, "GetLength")
	def SetDuration(self, duration):
		"""
		Sets the duration from which the length shall be calculated.
		@param duration: the duration in seconds as a float
		"""
		self.__duration = duration

	@sumpf.Input(float, "GetLength")
	def SetSamplingRate(self, samplingrate):
		"""
		Sets the sampling rate for which the length shall be calculated.
		@param samplingrate: the sampling rate for which the length shall be calculated
		"""
		self.__samplingrate = samplingrate

