# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2018 Jonas Schulte-Coerne
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
import sumpf


class FindSignalValues(object):
    """
    A class for finding the first index at which a Signal fulfills a given condition.
    The condition is defined by a check function and a value, that are passed to
    objects of this class.
    If a later index shall be found, the search range can be limited to an interval
    of sample indices.
    Predefined functions for finding an exact value or for checking where the Signal
    exceeds or falls below a certain threshold are available as static methods of
    this class.
    """
    @staticmethod
    def EXACT(signal, values, interval):
        """
        Finds the first indices, where the Signal's channels have exactly the
        respective value.
        @param signal: a Signal instance
        @param values: a sequence of values, one for each channel of the Signal
        @param interval: a SampleInterval instance, that defines which part of the signal shall be processed by this function
        @retval : a tuple of integer indices. The index can be None, if the given value has not been found in a channel
        """
        start, stop = interval.GetIndices(len(signal))
        try:
            return tuple(c.index(v, start, stop) for c, v in zip(signal.GetChannels(), values))
        except ValueError:
            result = []
            for c, v in zip(signal.GetChannels(), values):
                if v in c[start:stop]:
                    index = c.index(v, start, stop)
                    if start <= index < stop:
                        result.append(index)
                    else:
                        result.append(None)
                else:
                    result.append(None)
            return tuple(result)

    @staticmethod
    def ABOVE_THRESHOLD(signal, values, interval):
        """
        Finds the first indices, where a Signal's channels exceed the respective value.
        @param signal: a Signal instance
        @param values: a sequence of values, one for each channel of the Signal
        @param interval: a SampleInterval instance, that defines which part of the signal shall be processed by this function
        @retval : a tuple of integer indices. The index can be None, if the given threshold has not been exceeded by a channel
        """
        start, stop = interval.GetIndices(len(signal))
        result = []
        for c, v in zip(signal.GetChannels(), values):
            found = False
            for i, s in enumerate(c[start:stop]):
                if s > v:
                    result.append(start + i)
                    found = True
                    break
            if not found:
                result.append(None)
        return tuple(result)

    @staticmethod
    def BELOW_THRESHOLD(signal, values, interval):
        """
        Finds the first indices, where a Signal's channels fall below the respective value.
        @param signal: a Signal instance
        @param values: a sequence of values, one for each channel of the Signal
        @param interval: a SampleInterval instance, that defines which part of the signal shall be processed by this function
        @retval : a tuple of integer indices. The index can be None, if a channel has not gone below the given threshold
        """
        start, stop = interval.GetIndices(len(signal))
        result = []
        for c, v in zip(signal.GetChannels(), values):
            found = False
            for i, s in enumerate(c[start:stop]):
                if s < v:
                    result.append(start + i)
                    found = True
                    break
            if not found:
                result.append(None)
        return tuple(result)

    def __init__(self, signal=None, check=None, values=0.0, interval=(0, 1.0)):
        """
        @param signal: the Signal instance in which shall be searched for the fulfillment of the condition
        @param check: the function, that checks the condition and returns a tuple of indices
        @param values: a sequence of values, one for each channel of the Signal. The values are parameters for the condition function
        @param interval: a SampleInterval instance, that defines which part of the signal shall be processed
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
        if check is None:
            self.__check = FindSignalValues.EXACT
        else:
            self.__check = check
        self.__values = values
        self.__interval = interval

    @sumpf.Output(tuple)
    def GetSampleIndices(self):
        """
        Applies the condition function to the given Signal and returns a tuple of
        the first sample indices for each channel, where condition is fulfilled.
        If the condition is not fulfilled by any sample in the channel, the respective
        value in the tuple will be None.
        @retval : a tuple of either integer indices or None
        """
        if isinstance(self.__values, collections.Iterable):
            values = self.__values
        else:
            values = (self.__values,) * len(self.__signal.GetChannels())
        return self.__check(signal=self.__signal,
                            values=values,
                            interval=sumpf.SampleInterval.factory(self.__interval))

    @sumpf.Input(sumpf.Signal, "GetSampleIndices")
    def SetSignal(self, signal):
        """
        Sets the Signal in which shall be searched, where it fulfills the condition.
        @param signal: a Signal instance
        """
        self.__signal = signal

    @sumpf.Input(collections.Callable, "GetSampleIndices")
    def SetCheck(self, check):
        """
        Sets the condition function, that computes the first indices, where that
        condition is fulfilled.
        This class provides three predefined condition functions: EXACT, ABOVE_THRESHOLD
        and BELOW_THRESHOLD. It is also possible to pass custom functions, if they
        provide the following interface:
         - Parameter 0 (signal): a Signal instance, that shall be checked for the
                                 fulfillment of the condition
         - Parameter 1 (values): a sequence of parameter values, one for each
                                 channel of the Signal.
         - Parameter 2 (interval): a SampleInterval instance, that defines which
                                   part of the signal shall be processed by this
                                   function.
         - Return Value: a tuple of integer indices, one for each channel. The
                         index can be None, if the condition is never fulfilled
                         by a channel within the given interval.
        @param check: the function, that checks the condition and returns a tuple of indices
        """
        self.__check = check

    @sumpf.Input((collections.Iterable, float, int), "GetSampleIndices")
    def SetValues(self, values):
        """
        Specifies a set of values, that are passed as parameters to the condition
        function. These parameters can for example be an exact value to look for
        or a threshold.
        The values can be passed as a scalar value, which is then used for each
        channel of the input Signal or as a sequence, so that the condition function
        is parametrized for each channel individually.
        @param values: a sequence of values or a scalar value
        """
        self.__values = values

    @sumpf.Input(sumpf.SampleInterval, "GetSampleIndices")
    def SetInterval(self, interval):
        """
        Sets an interval of sample indices, within which the condition function
        shall be applied. This is usefull for finding other occurences than the
        first, where the condition is fulfilled.
        If a channel fulfills the condition, but only at samples, which are outside
        the given interval, the resulting index will be None.
        The interval does not need to be a SampleInterval instance. A sequence
        or an integer or float number will be converted internally as documented
        in the SampleInterval's class.
        @param interval: a SampleInterval, a sequence, an int or a float
        """
        self.__interval = interval

