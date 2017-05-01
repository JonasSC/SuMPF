# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2017 Jonas Schulte-Coerne
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


class RepeatSignal(object):
    """
    A class for repeating a Signal.
    If the repetitions are zero, an empty Signal with the same number of channels,
    samplingrate and labels as the input signal is returned by the GetOutput method.
    If the repetitions are negative, the GetOutput method raises a ValueError.
    """
    def __init__(self, signal=None, repetitions=1):
        """
        @param signal: the Signal, that shall be repeated
        @param repetitions: the integer number of repetitions
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
        self.__repetitions = repetitions

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Creates and returns the repeated Signal.
        @retval : a Signal instance
        """
        if self.__repetitions < 0:
            raise ValueError("Negative number of repetitions")
        elif self.__repetitions == 0:
            return sumpf.Signal(channels=((0.0, 0.0),) * len(self.__signal.GetChannels()),
                                samplingrate=self.__signal.GetSamplingRate(),
                                labels=self.__signal.GetLabels())
        else:
            channels = [c * self.__repetitions for c in self.__signal.GetChannels()]
            return sumpf.Signal(channels=channels, samplingrate=self.__signal.GetSamplingRate(), labels=self.__signal.GetLabels())

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetSignal(self, signal):
        """
        Sets the Signal, that shall be repeated.
        @param signal: a Signal instance
        """
        self.__signal = signal

    @sumpf.Input(int, "GetOutput")
    def SetRepetitions(self, repetitions):
        """
        Sets the number of repetitions. Zero is allowed, negative numbers are not.
        @param repetitions: the integer number of repetitions
        """
        self.__repetitions = repetitions

