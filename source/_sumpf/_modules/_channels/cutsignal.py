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


class CutSignal(object):
    """
    A module for cutting out a part of a Signal.
    The interval to define which part of the input Signal shall be in the output
    Signal can be given in two ways:
        - the index of the first sample that shall be in the output Signal can
          be passed to the SetStart method, while the first sample that shall not
          be in the Signal can be passed to the SetStop method.
        - the start and stop indexes can be passed to the SetInterval method as
          a tuple.
    The stop index can also be the flag CutSignal.END, when the output Signal
    shall contain all samples until the end of the input Signal. Or the index
    can be negative. SetStop(-1) would select the samples until the last but one
    sample of the input Signal, SetStop(-2) would select the samples until the
    last but two and so on...
    """

    END = None  # select the samples until the end of the input Signal

    def __init__(self, signal=None, start=0, stop=None):
        """
        @param signal: the input Signal from which the output Signal shall be cut out
        @param start: the index of the first sample that shall be in the output Signal
        @param stop: the index of the first sample that shall not be in the output Signal (can also be negative or the flag CutSignal.END, see SetStop for details)
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
        self.__start = start
        self.__stop = stop

    @sumpf.Input(sumpf.Signal, ["GetOutput", "GetOutputLength"])
    def SetInput(self, signal):
        """
        Sets the input Signal from which the samples for the output Signal shall be taken.
        @param signal: the input Signal from which the output Signal shall be cut out
        """
        self.__signal = signal

    @sumpf.Input(int, ["GetOutput", "GetOutputLength"])
    def SetStart(self, start):
        """
        Sets the index of the sample from the input Signal that shall be the first
        sample of the output Signal.
        @param start: the index of the first sample that shall be in the output Signal
        """
        self.__start = start

    @sumpf.Input(int, ["GetOutput", "GetOutputLength"])
    def SetStop(self, stop):
        """
        Defines the end of the cut out Signal.
        This can be done in three ways:
            - a positive integer will define the index of the first sample that
              will not be in the output Signal.
            - a negative integer will calculate the index from the end of the
              input Signal. With "stop = -1" the output Signal will go to the last
              but one sample of the input Signal, with "stop = -2" it will go
              to the last but two sample and so on...
            - with the flag CutSignal.END the output Signal will span until the
              end of the input Signal.
        @param: a positive or a negative integer index (counted from the end of the input) or the flag CutSignal.END
        """
        self.__stop = stop

    @sumpf.Input(tuple, ["GetOutput", "GetOutputLength"])
    def SetInterval(self, interval):
        """
        A convenience method to set the start and stop indexes with a tuple.
        @param interval: a tuple (start, stop)
        """
        self.SetStart(interval[0])
        self.SetStop(interval[1])

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Calculates and returns the output Signal, which is cut out of the input
        Signal
        @retval : the output Signal
        """
        return self.__signal[self.__start:self.__stop]

    @sumpf.Output(int)
    def GetOutputLength(self):
        """
        Returns the length that the output Signal will have.
        @retval : the length of the output Signal
        """
        stop = self.__stop
        if stop == CutSignal.END:
            stop = len(self.__signal)
        elif stop < 0:
            stop = len(self.__signal) + self.__stop
        result = stop - self.__start
        if result < 2:
            return 0
        elif result > len(self.__signal):
            return len(self.__signal) - self.__start
        else:
            return result

