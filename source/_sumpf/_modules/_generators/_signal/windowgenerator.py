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

import collections
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
    A class whose instances generate Signals that fall and/or raise according to
    a given window function.
    The resulting Signal does not contain acoustic data. It is mainly used to be
    multiplied with a sound Signal, to fade in or out the sound Signal without creating
    much unwanted distortion.
    The maximum of the window function will always be 1.0. It can be changed by
    sending the resulting Signal through a sumpf.Multiply module.
    The resulting Signal will have one channel.
    """
    def __init__(self, raise_interval=None, fall_interval=None, function=None, samplingrate=None, length=None):
        """
        @param raise_interval: None, a tuple of two integers or a float between -1.0 and 1.0, see the SetRaiseInterval method for details
        @param fall_interval: None, a tuple of two integers or a float between -1.0 and 1.0, see the SetFallInterval method for details
        @param function: a WindowFunction instance
        @param samplingrate: the sampling rate in Hz
        @param length: the number of samples of the signal
        """
        SignalGenerator.__init__(self, samplingrate=samplingrate, length=length)
        self.__raise_interval = raise_interval
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
        # check for the intervals being floats
        if self.__raise_interval is None or isinstance(self.__raise_interval, collections.Iterable):
            raise_interval = self.__raise_interval
        elif isinstance(self.__raise_interval, float):
            if self.__raise_interval >= 0.0:
                raise_interval = (0, int(round((self._length * self.__raise_interval))))
            else:
                raise_interval = (int(round((self._length * self.__raise_interval))), None)
        if self.__fall_interval is None or isinstance(self.__fall_interval, collections.Iterable):
            fall_interval = self.__fall_interval
        elif isinstance(self.__fall_interval, float):
            if self.__fall_interval >= 0.0:
                fall_interval = (0, int(round((self._length * self.__fall_interval))))
            else:
                fall_interval = (int(round((self._length * self.__fall_interval))), self._length)
        # create the samples
        result = None
        if raise_interval is not None:
            ra = raise_interval[0]
            if ra < 0:
                ra = self._length + ra
            rb = raise_interval[1]
            if rb is None:
                rb = self._length
            elif rb < 0:
                rb = self._length + rb
            if ra >= rb:
                raise ValueError("The raise interval has to span at least one sample.")
            width = rb - ra
            window = self.__function(2 * width)[0:width]
            samples = []
            for _ in range(ra):
                samples.append(0.0)
            for s in window:
                samples.append(s)
            for _ in range(self._length - rb):
                samples.append(1.0)
            result = samples[0:self._length]
        else:
            result = [1.0] * self._length
        if fall_interval is not None:
            fa = fall_interval[0]
            if fa < 0:
                fa = self._length + fa
            fb = fall_interval[1]
            if fb is None:
                fb = self._length
            elif fb < 0:
                fb = self._length + fb
            if fa >= fb:
                raise ValueError("The fall interval has to span at least one sample.")
            width = fb - fa
            window = self.__function(2 * width)[width:]
            samples = []
            for _ in range(fa):
                samples.append(1.0)
            for s in window:
                samples.append(s)
            for _ in range(self._length - fb):
                samples.append(0.0)
            if raise_interval is None:
                result = numpy.multiply(result, samples[0:self._length])
            elif fb < ra:
                result = numpy.add(result, samples[0:self._length])
            else:
                result = numpy.multiply(result, samples[0:self._length])
        return tuple(result)

    def _GetLabel(self):
        """
        Returns the label for the generated channel.
        @retval : the string label
        """
        return "Window"

    @sumpf.Input((tuple, float), "GetSignal")
    def SetRaiseInterval(self, interval):
        """
        An interval in which the samples of the output Signal shall be raising
        from 0.0 to 1.0 according to the given window function.
        There are three allowed data types to specify the interval:
         - None disables the fade in. All samples will be 1.0 from the start on.
         - A tuple of integers specifies the sample index, with which the fade in
           starts, and the index of the first sample after the fade in.
           With negative values, the indices will be calculated from the end of
           the output Signal. If the second index is None, the fade in will extend
           to the end of the output signal. (similar to slicing of lists)
         - A float value determines the fraction of the output Signal, that shall
           be affected by the fade in. Positive values place the fade in at the
           beginning of the signal, Negative values place it at the end.
        If the raise interval is located before the fall interval, or if the
        intervals overlap, the Signals for the raising and the falling edge are
        multiplied, which makes the output Signal have its minimums at the beginning
        and at the end. If the raise interval is located after the fall interval,
        the two Signals are added, which makes the output Signal have its maximums
        at the beginning and at the end.
        @param interval: None, a tuple of two integers or a float between -1.0 and 1.0
        """
        self.__raise_interval = interval

    @sumpf.Input((tuple, float), "GetSignal")
    def SetFallInterval(self, interval):
        """
        An interval in which the samples of the output Signal shall be falling
        from 1.0 to 0.0 according to the given window function.
        There are three allowed data types to specify the interval:
         - None disables the fade out. All samples will be 1.0 until the end.
         - A tuple of integers specifies the sample index, with which the fade
           out starts, and the index of the first sample after the fade out.
           With negative values, the indices will be calculated from the end of
           the output Signal. If the second index is None, the fade out will extend
           to the end of the output signal. (similar to slicing of lists)
         - A float value determines the fraction of the output Signal, that shall
           be affected by the fade out. Positive values place the fade out at the
           beginning of the signal, Negative values place it at the end.
        If the raise interval is located before the fall interval, or if the
        intervals overlap, the Signals for the raising and the falling edge are
        multiplied, which makes the output Signal have its minimums at the beginning
        and at the end. If the raise interval is located after the fall interval,
        the two Signals are added, which makes the output Signal have its maximums
        at the beginning and at the end.
        @param interval: None, a tuple of two integers or a float between -1.0 and 1.0
        """
        self.__fall_interval = interval

    @sumpf.Input(WindowFunction, "GetSignal")
    def SetFunction(self, function):
        """
        Sets the function that defines the shape of the window.
        @param function: a WindowFunction instance
        """
        self.__function = function

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

