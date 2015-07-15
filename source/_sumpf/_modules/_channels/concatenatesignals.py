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


class ConcatenateSignals(object):
    """
    A module for the concatenation of two Signals.
    To create the output Signal, the second input Signal will be appended to the
    first one.
    """
    def __init__(self, signal1=None, signal2=None):
        """
        All parameters are optional
        @param signal1: the first Signal-instance for the concatenation
        @param signal2: the second Signal-instance for the concatenation
        """
        if signal1 is None:
            self.__signal1 = sumpf.Signal()
        else:
            self.__signal1 = signal1
        if signal2 is None:
            self.__signal2 = sumpf.Signal()
        else:
            self.__signal2 = signal2

    @sumpf.Input(sumpf.Signal, ["GetOutput", "GetOutputLength"])
    def SetInput1(self, signal):
        """
        Sets the first Signal for concatenation.
        @param signal: the first Signal instance for concatenation
        """
        self.__signal1 = signal

    @sumpf.Input(sumpf.Signal, ["GetOutput", "GetOutputLength"])
    def SetInput2(self, signal):
        """
        Sets the second Signal for concatenation.
        @param signal: the second Signal instance for concatenation
        """
        self.__signal2 = signal

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Appends the second Signal to the first one and returns the concatenated Signal.
        @retval : a Signal whose channels are the result of the concatenation
        """
        if self.__signal1.IsEmpty():
            return self.__signal2
        elif self.__signal2.IsEmpty():
            return self.__signal1
        else:
            if self.__signal1.GetSamplingRate() != self.__signal2.GetSamplingRate():
                raise ValueError("The given signal has a different sampling rate than the second signal")
            if len(self.__signal1.GetChannels()) != len(self.__signal2.GetChannels()):
                raise ValueError("The given signal has a different channel count than the second signal")
            channels = []
            for c in self.__signal1.GetChannels():
                channels.append(list(c))
            labels = []
            for i in range(len(self.__signal2.GetChannels())):
                for s in self.__signal2.GetChannels()[i]:
                    channels[i].append(s)
                labels.append("Concatenation " + str(i + 1))
            return sumpf.Signal(channels=channels, samplingrate=self.__signal1.GetSamplingRate(), labels=labels)

    @sumpf.Output(int)
    def GetOutputLength(self):
        """
        Returns the length of the resulting output Signal.
        (This is the sum of the lengths of the input Signals.)
        @retval : the length of the output Signal as integer
        """
        if self.__signal1.IsEmpty():
            return len(self.__signal2)
        elif self.__signal2.IsEmpty():
            return len(self.__signal1)
        else:
            return len(self.__signal1) + len(self.__signal2)

