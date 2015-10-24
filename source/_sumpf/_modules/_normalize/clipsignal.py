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

import collections
import numpy
import sumpf


class ClipSignal(object):
    """
    Clips a Signal to given minimum and maximum values.
    """
    def __init__(self, signal=None, thresholds=(-1.0, 1.0)):
        """
        @param input: the Signal which shall be clipped
        @param thresholds: a tuple (min, max) with the thresholds for the clipping
        """
        if thresholds[1] < thresholds[0]:
            raise ValueError("The minimum threshold must be smaller than the maximum threshold")
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
        self.__thresholds = thresholds

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Generates the clipped Signal and returns it.
        @retval : the clipped Signal
        """
        return sumpf.Signal(channels=numpy.clip(self.__signal.GetChannels(), a_min=self.__thresholds[0], a_max=self.__thresholds[1]),
                            samplingrate=self.__signal.GetSamplingRate(),
                            labels=self.__signal.GetLabels())

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        """
        A method for setting the Signal which shall be clipped.
        @param signal: the Signal which shall be clipped
        """
        self.__signal = signal

    @sumpf.Input(collections.Iterable, "GetOutput")
    def SetThresholds(self, thresholds):
        """
        A method for specifying the minimum and maximum values to which the output
        Signal shall be clipped.
        @param thresholds: a tuple (min, max) with the thresholds for the clipping
        """
        if thresholds[1] < thresholds[0]:
            raise ValueError("The minimum threshold must be smaller than the maximum threshold")
        self.__thresholds = thresholds

