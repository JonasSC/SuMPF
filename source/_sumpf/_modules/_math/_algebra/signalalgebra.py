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
from . import signalalgebrabase


class AddSignals(signalalgebrabase.SignalAlgebra):
    """
    A module for adding two Signals.
    The input Signals must have the same length, sampling rate and channel count.
    If one Signal is empty and the other is not, the result will be an empty Signal

    The two input Signals will be added channel per channel and sample per sample:
        signal1 = sumpf.Signal(channels = ((1, 2), (3, 4)))
        signal2 = sumpf.Signal(channels = ((5, 6), (7, 8)))
        signal1 + signal2 == sumpf.Signal(channels=((1+5, 2+6), (3+7, 4+8)))
    """
    def _Calculate(self, signal1, signal2):
        """
        Does the actual calculation.
        @param signal1: the first Signal for the calculation
        @param signal2: the second Signal for the calculation
        """
        return signal1 + signal2



class SubtractSignals(signalalgebrabase.SignalAlgebra):
    """
    A module for subtracting two Signals.
    The second Signal will be subtracted from the first one.
    The input Signals must have the same length, sampling rate and channel count.

    The two input Signals will be subtracted channel per channel and sample per sample:
        signal1 = sumpf.Signal(channels = ((1, 2), (3, 4)))
        signal2 = sumpf.Signal(channels = ((5, 6), (7, 8)))
        signal1 - signal2 == sumpf.Signal(channels=((1-5, 2-6), (3-7, 4-8)))
    """
    def _Calculate(self, signal1, signal2):
        """
        Does the actual calculation.
        @param signal1: the first Signal for the calculation
        @param signal2: the second Signal for the calculation
        """
        return signal1 - signal2



class MultiplySignals(signalalgebrabase.SignalAlgebra):
    """
    A module for multiplying two Signals.
    The input Signals must have the same length, sampling rate and channel count.

    The two input Signals will be multiplied channel per channel and sample per sample:
        signal1 = sumpf.Signal(channels = ((1, 2), (3, 4)))
        signal2 = sumpf.Signal(channels = ((5, 6), (7, 8)))
        signal1 * signal2 == sumpf.Signal(channels=((1*5, 2*6), (3*7, 4*8)))
    """
    def _Calculate(self, signal1, signal2):
        """
        Does the actual calculation.
        @param signal1: the first Signal for the calculation
        @param signal2: the second Signal for the calculation
        """
        return signal1 * signal2




class DivideSignals(signalalgebrabase.SignalAlgebra):
    """
    A module for dividing two Signals.
    The first Signal will be divided by the second one.
    The input Signals must have the same length, sampling rate and channel count.
    If both Signals are empty, an empty Signal is returned instead of raising an
    error.

    The two input Signals will be divided channel per channel and sample per sample:
        signal1 = sumpf.Signal(channels = ((1, 2), (3, 4)))
        signal2 = sumpf.Signal(channels = ((5, 6), (7, 8)))
        signal1 / signal2 == sumpf.Signal(channels=((1/5, 2/6), (3/7, 4/8)))
    """
    def _Calculate(self, signal1, signal2):
        """
        Does the actual calculation.
        @param signal1: the first Signal for the calculation
        @param signal2: the second Signal for the calculation
        """
        if signal1.IsEmpty() and signal2.IsEmpty():
            return sumpf.Signal(channels=((0.0, 0.0),) * len(signal1.GetChannels()), samplingrate=signal1.GetSamplingRate())
        else:
            return signal1 / signal2



class CompareSignals(signalalgebrabase.SignalAlgebra):
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
    def _Calculate(self, signal1, signal2):
        """
        Does the actual calculation.
        @param signal1: the first Signal for the calculation
        @param signal2: the second Signal for the calculation
        """
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

