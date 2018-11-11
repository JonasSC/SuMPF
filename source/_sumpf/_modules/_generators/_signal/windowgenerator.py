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

import numpy
import sumpf
from .signalgenerator import SignalGenerator


class WindowFunction(object):
    """
    Abstract base class that can be used to define window functions which can
    be passed to a WindowGenerator.
    The instances must be call-able with the length of the window as a parameter.
    The call must return a tuple of samples with the given length. This tuple has
    to contain both the rising and the falling edge of the window.
    The samples must be between 0.0 and 1.0
    Only if the length is odd, the middle sample contains the 1.0.
    Like this the WindowFunction instances behave much like the window functions
    in numpy. With the one exception that the instances only take the length
    parameter. Additional parameters (e.g. beta for the kaiser window) can be
    stored in a constructor of a derived class.
    """
    def __call__(self, length):
        """
        Virtual base method that makes the instance callable.
        @param length: the full length of the window (in samples) for both the rising and the falling edge
        @retval : a tuple of samples with the rising and the falling edge of the window
        """
        raise NotImplementedError("This method should have been overridden in a derived class")



class WindowGenerator(SignalGenerator):
    """
    A class whose instances generate Signals that fall and/or rise according to
    a given window function.
    The resulting Signal does not contain acoustic data. It is mainly used to be
    multiplied with a sound Signal, to fade in or out the sound Signal without
    creating much unwanted distortion.
    The maximum of the window function will always be 1.0. It can be changed by
    sending the resulting Signal through a sumpf.Multiply module.
    The resulting Signal will have one channel.
    """
    def __init__(self, rise_interval=(0, 0), fall_interval=(1.0, 1.0), function=None, samplingrate=None, length=None):
        """
        @param rise_interval: a SampleInterval, a sequence, an int or a float, see the SetRiseInterval method for details
        @param fall_interval: a SampleInterval, a sequence, an int or a float, see the SetFallInterval method for details
        @param function: a WindowFunction instance
        @param samplingrate: the sampling rate in Hz
        @param length: the number of samples of the signal
        """
        SignalGenerator.__init__(self, samplingrate=samplingrate, length=length)
        self.__rise_interval = rise_interval
        self.__fall_interval = fall_interval
        if function is None:
            self.__function = WindowGenerator.VonHann()
        else:
            self.__function = function

    def _GetSamples(self):
        """
        Generates the samples of the window and returns them as a tuple.
        @retval : a tuple of samples
        """
        ra, rb = sumpf.SampleInterval.factory(self.__rise_interval).GetIndices(self._length)
        rise_function = self.__GetRiseFunction(ra, rb)
        fa, fb = sumpf.SampleInterval.factory(self.__fall_interval).GetIndices(self._length)
        fall_function = self.__GetFallFunction(fa, fb)
        if fb <= ra: # first fall, then rise, intervals don't really overlap
            result = numpy.add(fall_function, rise_function)
        else:
            result = numpy.multiply(rise_function, fall_function)
        return tuple(result)

    def _GetLabel(self):
        """
        Returns the label for the generated channel.
        @retval : the string label
        """
        return "Window"

    @sumpf.Input(sumpf.SampleInterval, "GetSignal")
    def SetRiseInterval(self, interval):
        """
        An interval in which the samples of the output Signal shall be raising
        from 0.0 to 1.0 according to the given window function.
        If the rise interval is located before the fall interval, or if the
        intervals overlap, the Signals for the raising and the falling edge are
        multiplied, which makes the output Signal have its minimums at the beginning
        and at the end. If the rise interval is located after the fall interval,
        the two Signals are added, which makes the output Signal have its maximums
        at the beginning and at the end.
        The interval does not need to be a SampleInterval instance. A sequence
        or an integer or float number will be converted internally as documented
        in the SampleInterval's class.
        @param interval: a SampleInterval, a sequence, an int or a float
        """
        self.__rise_interval = interval

    @sumpf.Input(sumpf.SampleInterval, "GetSignal")
    def SetFallInterval(self, interval):
        """
        An interval in which the samples of the output Signal shall be falling
        from 1.0 to 0.0 according to the given window function.
        If the rise interval is located before the fall interval, or if the
        intervals overlap, the Signals for the raising and the falling edge are
        multiplied, which makes the output Signal have its minimums at the beginning
        and at the end. If the rise interval is located after the fall interval,
        the two Signals are added, which makes the output Signal have its maximums
        at the beginning and at the end.
        The interval does not need to be a SampleInterval instance. A sequence
        or an integer or float number will be converted internally as documented
        in the SampleInterval's class.
        @param interval: a SampleInterval, a sequence, an int or a float
        """
        self.__fall_interval = interval

    @sumpf.Input(WindowFunction, "GetSignal")
    def SetFunction(self, function):
        """
        Sets the function that defines the shape of the window.
        @param function: a WindowFunction instance
        """
        self.__function = function

    def __GetRiseFunction(self, start, stop):
        """
        Creates a sequence with the rising edge.
        """
        function = numpy.empty(self._length)
        if 0 <= start < self._length or 0 < stop < self._length:
            width = stop - start
            window = self.__function(2 * width)[0:width]
            function[max(start, 0):min(stop, self._length)] = window[max(0, -start):min(width, width + self._length - stop)]
        if start > 0:
            function[0:min(start, self._length)] = numpy.zeros(min(start, self._length))
        if stop < self._length:
            function[max(stop, 0):] = numpy.ones(min(self._length - stop, self._length))
        return function

    def __GetFallFunction(self, start, stop):
        """
        Creates a sequence with the falling edge.
        """
        function = numpy.empty(self._length)
        if 0 <= start < self._length or 0 < stop < self._length:
            width = stop - start
            window = self.__function(2 * width)[width:]
            function[max(start, 0):min(stop, self._length)] = window[max(0, -start):min(width, width + self._length - stop)]
        if start > 0:
            function[0:min(start, self._length)] = numpy.ones(min(start, self._length))
        if stop < self._length:
            function[max(stop, 0):] = numpy.zeros(min(self._length - stop, self._length))
        return function

    class Bartlett(WindowFunction):
        """
        Wrapper for the bartlett window function in numpy.
        """
        def __call__(self, length):
            """
            @param length: the full length of the window (in samples) for both the rising and the falling edge
            @retval : a tuple of samples with the rising and the falling edge of the window
            """
            return numpy.bartlett(length)

    class Blackman(WindowFunction):
        """
        Wrapper for the blackman window function in numpy.
        """
        def __call__(self, length):
            """
            @param length: the full length of the window (in samples) for both the rising and the falling edge
            @retval : a tuple of samples with the rising and the falling edge of the window
            """
            return numpy.blackman(length)

    class Hamming(WindowFunction):
        """
        Wrapper for the hamming window function in numpy.
        """
        def __call__(self, length):
            """
            @param length: the full length of the window (in samples) for both the rising and the falling edge
            @retval : a tuple of samples with the rising and the falling edge of the window
            """
            return numpy.hamming(length)

    class Kaiser(WindowFunction):
        """
        Wrapper for the kaiser window function in numpy.
        """
        def __init__(self, beta):
            """
            A constructor to store the beta parameter for the numpy kaiser function.

            The following table is copied from the numpy documentation:
            beta    Window shape
            0       Rectangular
            5       Similar to a Hamming
            6       Similar to a Hanning
            8.6     Similar to a Blackman

            @param beta: the beta parameter for the numpy.kaiser function
            """
            self.__beta = beta
        def __call__(self, length):
            """
            @param length: the full length of the window (in samples) for both the rising and the falling edge
            @retval : a tuple of samples with the rising and the falling edge of the window
            """
            return numpy.kaiser(length, self.__beta)

    class Rectangle(WindowFunction):
        """
        a window function class for creating a rectangle window
        """
        def __call__(self, length):
            """
            @param length: the full length of the window (in samples) for both the rising and the falling edge
            @retval : a tuple of samples with the rising and the falling edge of the window
            """
            return numpy.ones(length)

    class VonHann(WindowFunction):
        """
        Wrapper for the hanning window function in numpy.
        """
        def __call__(self, length):
            """
            @param length: the full length of the window (in samples) for both the rising and the falling edge
            @retval : a tuple of samples with the rising and the falling edge of the window
            """
            return numpy.hanning(length)

