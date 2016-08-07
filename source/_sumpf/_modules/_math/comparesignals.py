# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2016 Jonas Schulte-Coerne
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


class CompareSignals(object):
    """
    A comparator for two Signals.
    This works a bit like an open loop operational amplifier with the first Signal
    being connected to the +input and the second Signal to the -input. If the
    first input Signal is greater than the second Signal, the respective sample
    of the output Signal will be 1.0. If it is smaller, the sample will be -1.0.
    And wherever both input Signals have an equal value, the output will be 0.0.

    The input Signals must have the same length, sampling rate and channel count.

    The two input Signals will be compared channel per channel and sample per sample:
        signal1 = sumpf.Signal(channels = ((0, 2), (3, 4)))
        signal2 = sumpf.Signal(channels = ((1, 2), (2, 5)))
        compare(signal1, signal2) == sumpf.Signal(channels=((-1, 0), (1, -1)))
    """
    def __init__(self, signal1=None, signal2=None):
        """
        All parameters are optional
        @param signal1: the first Signal-instance for the comparison
        @param signal2: the second Signal-instance for the comparison
        """
        if signal1 is None:
            self.__signal1 = sumpf.Signal()
        else:
            self.__signal1 = signal1
        if signal2 is None:
            self.__signal2 = sumpf.Signal()
        else:
            self.__signal2 = signal2

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput1(self, signal):
        """
        Sets the first Signal for the comparison.
        @param signal: the first Signal-instance for the comparison
        """
        self.__signal1 = signal

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput2(self, signal):
        """
        Sets the second Signal for the comparison.
        @param signal: the second Signal-instance for the comparison
        """
        self.__signal2 = signal

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Calculates and returns the Signal resulting from the comparison.
        Before the calculation, the input Signals are checked for compatibility.
        If the Signals are incompatible and both not empty, a ValueError is raised.
        If the Signals are incompatible and one Signal is empty, an empty Signal
        is returned.
        @retval : a Signal whose channels are the result of the calculation
        """
        signal1 = self.__signal1
        signal2 = self.__signal2
        # checks
        if signal1.GetSamplingRate() != signal2.GetSamplingRate():
            raise ValueError("The Signals do not have the same sampling rate (Signal1: %f, Signal2: %f)" % (signal1.GetSamplingRate(), signal2.GetSamplingRate()))
        elif len(signal1.GetChannels()) != len(signal2.GetChannels()):
            raise ValueError("The Signals do not have the same number of channels (Signal1: %i, Signal2: %i)" % (len(signal1.GetChannels()), len(signal2.GetChannels())))
        elif len(signal1) != len(signal2):
            raise ValueError("The Signals do not have the same length (Signal1: %i, Signal2: %i)" % (len(signal1), len(signal2)))
        else:
        # the actual comparison
            signal1_channels = signal1.GetChannels()
            signal2_channels = signal2.GetChannels()
            result_channels = []
            result_labels = []
            for i in range(len(signal1_channels)):
                channel = []
                for j in range(len(signal1_channels[i])):
                    if signal1_channels[i][j] < signal2_channels[i][j]:
                        channel.append(-1.0)
                    elif signal1_channels[i][j] == signal2_channels[i][j]:
                        channel.append(0.0)
                    else:
                        channel.append(1.0)
                result_channels.append(tuple(channel))
                result_labels.append("Comparison %i" % (i + 1))
            return sumpf.Signal(channels=tuple(result_channels), samplingrate=signal1.GetSamplingRate(), labels=tuple(result_labels))

