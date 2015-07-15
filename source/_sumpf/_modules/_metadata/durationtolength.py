# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2015 Jonas Schulte-Coerne
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
    def __init__(self, duration=None, samplingrate=None, even_length=False):
        """
        All parameters are optional. If they are not given, they are taken from
        the config.
        @param duration: a duration in seconds as a float
        @param samplingrate: the sampling rate for which the length shall be calculated
        @param even_length: if True, the length is rounded to an even integer value, to avoid missing samples when a Signal is transformed to the frequency domain and back
        """
        if samplingrate is None:
            samplingrate = sumpf.config.get("default_samplingrate")
        self.__samplingrate = float(samplingrate)
        if duration is None:
            duration = sumpf.config.get("default_signal_length") / self.__samplingrate
        self.__duration = float(duration)
        self.__even_length = even_length

    @sumpf.Output(int)
    def GetLength(self):
        """
        Returns the length of a Signal that has been calculated for the given
        duration and sampling rate.
        @retval : the length as an integer
        """
        if self.__even_length:
            return 2 * int(round(0.5 * self.__duration * self.__samplingrate))
        else:
            return int(round(self.__duration * self.__samplingrate))

    @sumpf.Input(float, "GetLength")
    def SetDuration(self, duration):
        """
        Sets the duration from which the length shall be calculated.
        @param duration: the duration in seconds as a float
        """
        self.__duration = duration

    @sumpf.Input(bool, "GetLength")
    def SetEvenLength(self, even_length):
        """
        Specifies, if the length shall be rounded to an even integer.
        This is useful, when a Signal with the given length shall be transformed
        to the frequency domain. The fourier transformation expects the length of
        the Signal to be even. When transforming a Signal with an odd length, the
        last sample of the Signal will be dropped.
        @param even_length: if True, the length is rounded to an even integer value, if False, the length is rounded to the integer that gives the closest match to the given duration
        """
        self.__even_length = even_length

    @sumpf.Input(float, "GetLength")
    def SetSamplingRate(self, samplingrate):
        """matches
        Sets the sampling rate for which the length shall be calculated.
        @param samplingrate: the sampling rate for which the length shall be calculated
        """
        self.__samplingrate = samplingrate

