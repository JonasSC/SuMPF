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
from .signalgenerator import SignalGenerator


class ConstantSignalGenerator(SignalGenerator):
    """
    Generates a Signal whose data is a sequence of constant samples with the given
    length and the given sampling rate.
    The resulting Signal will have one channel.
    """
    def __init__(self, value=1.0, samplingrate=None, length=None):
        """
        @param value: the constant value for the Signal's samples
        @param samplingrate: the sampling rate in Hz
        @param length: the number of samples of the signal
        """
        SignalGenerator.__init__(self, samplingrate=samplingrate, length=length)
        self.__value = value

    @sumpf.Input(float, "GetSignal")
    def SetValue(self, value):
        """
        Sets the value of the output Signal's samples.
        @param value: a float
        """
        self.__value = value

    def _GetSamples(self):
        """
        Generates the samples of a Signal which are all 0.0 and returns them as a tuple.
        @retval : a tuple of samples
        """
        return (self.__value,) * self._length

    def _GetLabel(self):
        """
        Returns the label for the output Signal's channel.
        @retval : a string label
        """
        return "Constant"

