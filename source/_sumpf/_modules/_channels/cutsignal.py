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


class CutSignal(object):
    """
    A module for cutting out a part of a Signal.
    The part, that is cut out of the Signal is defined by a SampleInterval, but
    it is possible to define the interval by passing a tuple, a float or an integer
    without creating a SampleInterval instance. See the SampleInterval's documentation
    for details about how to define intervals.
    """
    def __init__(self, signal=None, interval=(0, 1.0)):
        """
        @param signal: the input Signal from which the output Signal shall be cut out
        @param interval: the interval of samples, that shall become the output signal, as a SampleInterval, a sequence, an int or a float
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
        self.__interval = interval

    @sumpf.Input(sumpf.Signal, ("GetOutput", "GetOutputLength"))
    def SetSignal(self, signal):
        """
        Sets the input Signal from which the samples for the output Signal shall be taken.
        @param signal: the input Signal from which the output Signal shall be cut out
        """
        self.__signal = signal

    @sumpf.Input(sumpf.SampleInterval, ("GetOutput", "GetOutputLength"))
    def SetInterval(self, interval):
        """
        Sets the interval of samples, that shall become the output signal.
        The interval does not need to be a SampleInterval instance. A sequence
        or an integer or float number will be converted internally as documented
        in the SampleInterval's class.
        @param interval: a SampleInterval, a sequence, an int or a float
        """
        self.__interval = interval

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Calculates and returns the output Signal, which is cut out of the input Signal.
        @retval : the output Signal
        """
        start, stop = sumpf.SampleInterval.factory(self.__interval).GetIndices(len(self.__signal))
        return self.__signal[start:stop]

    @sumpf.Output(int)
    def GetOutputLength(self):
        """
        Returns the length that the output Signal will have.
        @retval : the length of the output Signal
        """
        start, stop = sumpf.SampleInterval.factory(self.__interval).GetIndices(len(self.__signal))
        start = max(0, start)
        stop = min(stop, len(self.__signal))
        return stop - start

