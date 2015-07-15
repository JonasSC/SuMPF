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

import math
import sumpf


class LogarithmSignal(object):
    """
    Calculates the logarithm of a Signal.
    This will be done by calculating the logarithm of each sample.
    """
    def __init__(self, signal=None, base=10.0):
        """
        @param signal: the input Signal
        @param base: the float which shall be the base for the logarithm
        """
        if signal is None:
            self.__signal = sumpf.Signal(channels=((1.0, 1.0),))
        else:
            self.__signal = signal
        self.__base = base

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        """
        Sets the input Signal.
        @param signal: the input Signal
        """
        self.__signal = signal

    @sumpf.Input(float, "GetOutput")
    def SetBase(self, base):
        """
        Sets the base for the logarithm.
        @param base: the float which shall be the base for the logarithm
        """
        self.__base = base

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Returns the output Signal, which is the sample wise logarithm of the input
        Signal.
        @retval : the logarithm Signal
        """
        result = []
        for c in self.__signal.GetChannels():
            channel = []
            for s in c:
                channel.append(math.log(s, self.__base))
            result.append(tuple(channel))
        return sumpf.Signal(channels=result, samplingrate=self.__signal.GetSamplingRate(), labels=self.__signal.GetLabels())

