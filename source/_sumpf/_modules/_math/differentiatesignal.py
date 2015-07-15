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
import sumpf

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy



class DifferentiateSignal(object):
    """
    A module for calculating the derivative of a Signal.
    As the derivative of a Signal can be calculated in different ways, the function
    that is used to calculate the derivative of each channel can be changed. The
    default function uses the simple algorithm of subtracting the previous sample
    from the current one.
    """
    def __init__(self, signal=None, function=sumpf.helper.differentiate):
        """
        @param signal: the input Signal
        @param function: the function that shall be used to calculate the derivative
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
        self.__function = function

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        """
        Sets the input Signal.
        @param signal: the input Signal
        """
        self.__signal = signal

    @sumpf.Input(collections.Callable, "GetOutput")
    def SetFunction(self, function):
        """
        Sets the function that shall be used to calculate the derivative.
        Since calculating the derivative of a sampled function is not trivial,
        there are different functions for this task in SuMPF:
         - helper.differentiate calculates the difference between the current sample and the previous one.
         - helper.differentiate_fft calculates the derivative in the frequency domain
         - helper.differentiate_spline uses a spline interpolation to calculate the derivative
        Please see these functions and their documentation to consider their advantages
        and drawbacks.
        The function that is passed to this method has to take the sequence, that
        shall be differentiated, as only argument. When using functions, which
        take more parameters (like the differentiate_spline function), use the
        lambda statement or functools.partial, to define all other arguments.
        @param function: the function that shall be used to calculate the derivative
        """
        self.__function = function

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Returns the output Signal, which is the derivative of the input Signal.
        @retval : a Signal which is the derivative of the input Signal
        """
        result = []
        for c in self.__signal.GetChannels():
            diffs = self.__function(c)
            derivative = tuple(numpy.multiply(diffs, self.__signal.GetSamplingRate()))
            result.append(derivative)
        return sumpf.Signal(channels=result, samplingrate=self.__signal.GetSamplingRate(), labels=self.__signal.GetLabels())

