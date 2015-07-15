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
import math
import sumpf
from .signalgenerator import SignalGenerator


class SweepGenerator(SignalGenerator):
    """
    A class whose instances generate a sine wave that sweeps its frequency from
    the start frequency to the stop frequency. Such a Signal is known as sweep
    or chirp.
    The amplitude of the sweep will always be one. It can be changed by
    sending the resulting Signal through a sumpf.AmplifySignal module.
    The resulting Signal will have one channel.
    """
    def __init__(self, start_frequency=20.0, stop_frequency=20000.0, function=None, interval=None, samplingrate=None, length=None):
        """
        @param start_frequency: the frequency at the beginning in Hz
        @param stop_frequency: the frequency at the end in Hz
        @param function: a function with the parameters (x, start, stop). See SweepGenerator.Exponential for details
        @param interval: None or a tuple (start, stop) that defines the interval of samples in which shall be swept through the frequencies. See SetInterval for details
        @param samplingrate: the sampling rate in Hz
        @param length: the number of samples of the signal
        """
        SignalGenerator.__init__(self, samplingrate=samplingrate, length=length)
        self.__start = float(start_frequency)
        self.__stop = float(stop_frequency)
        if function is None:
            self.__function = SweepGenerator.Exponential
        else:
            self.__function = function
        self.__interval = interval
        self.__increase_rate = None
        self.__offset = 0.0

    def _GetSamples(self):
        """
        Generates the samples of the Sweep and returns them as a tuple.
        @retval : a tuple of samples
        """
        self.__CalculateIncreaseRate()
        return SignalGenerator._GetSamples(self)

    def _GetSample(self, t):
        """
        Calculates and returns the value of the sample at time t.
        @param t: the time from the beginning of the signal in seconds
        @retval : the value of the sweep function at the given time
        """
        return self.__function(t - self.__offset, self.__start, self.__increase_rate)

    def _GetLabel(self):
        """
        Returns the label for the generated channel.
        @retval : the string label
        """
        return "Sweep"

    @sumpf.Input(float, "GetSignal")
    def SetStartFrequency(self, frequency):
        """
        Sets the frequency at the beginning of the sweep.
        @param frequency: a frequency in Hz
        """
        self.__start = float(frequency)

    @sumpf.Input(float, "GetSignal")
    def SetStopFrequency(self, frequency):
        """
        Sets the frequency at the beginning of the sweep.
        @param frequency: a frequency in Hz
        """
        self.__stop = float(frequency)

    @sumpf.Input(collections.Callable, "GetSignal")
    def SetSweepFunction(self, function):
        """
        Sets the function that defines the frequency raise (e.g. linear or exponential)
        @param function: a function with the parameters (x, start, stop). See SweepGenerator.Exponential for details
        """
        self.__function = function

    @sumpf.Input(tuple, "GetSignal")
    def SetInterval(self, interval):
        """
        Sets a time interval in which shall be swept through the frequencies.
        The interval shall be either None or a tuple of integers.
        If the interval is None, the sweep will start with the given start frequency
        at the first sample of the sweep and end with the given stop frequency
        at the last sample.
        If the interval is a tuple of sample numbers (a, b), the sweep will
        start with a low frequency at the first sample, reach the given start
        frequency at the a-th sample, go on to the given stop frequency at the
        b-th sample and then end with a high frequency at the last sample.
        This functionality is useful, when the sweep's beginning and end shall
        be faded in and out with a window function, because the time interval, in
        which the sweep sweeps though the interesting frequencies is known and
        before and after this interval, the signal can be faded in and out.
        If a or b are negative, the sample number will be counted from the end
        of the sweep.
        @param interval: None or a tuple of integers (a, b)
        """
        self.__interval = interval

    def __CalculateIncreaseRate(self):
        """
        Calculates the increase rate for the sweep and stores it.
        This way the increase rate does not need to be calculated for each
        sample individually.
        This method is called directly before the sweep is generated.
        """
        T = 0.0
        if self.__interval is None:
            T = float(self._length) / float(self._samplingrate)
            self.__offset = 0.0
        else:
            a = self.__interval[0]
            if a < 0:
                a = self._length + a
            b = self.__interval[1]
            if b < 0:
                b = self._length + b
            if a >= b:
                raise ValueError("The interval has to span at least one sample.")
            T = float(min(b, self._length) - max(a, 0)) / float(self._samplingrate)
            self.__offset = float(a) / float(self._samplingrate)
        f0 = self.__start
        fT = self.__stop
        k = 0.0
        if self.__function == SweepGenerator.Exponential:
            k = (fT / f0) ** (1.0 / T)
        elif self.__function == SweepGenerator.Linear:
            k = (fT - f0) / T
        self.__increase_rate = k

    @staticmethod
    def Exponential(t, f0, k):
        """
        The sweep function for an exponential increase of frequency.
        This function can be used with a SweepGenerator's SetSweepFunction-method.
        @param t: the time from the beginning of the signal in seconds
        @param f0: the start frequency in Hz
        @param k: the increase rate of the sweep
        """
        e = (k ** t) - 1
        l = math.log(k, math.e)
        x = 2.0 * math.pi * f0 * e / l
        return math.sin(x)

    @staticmethod
    def Linear(t, f0, k):
        """
        The sweep function for a linear increase of frequency.
        This function can be used with a SweepGenerator's SetSweepFunction-method.
        @param t: the time from the beginning of the signal in seconds
        @param f0: the start frequency in Hz
        @param k: the increase rate of the sweep
        """
        s = f0 + (t * k / 2.0)
        x = 2.0 * math.pi * t * s
        return math.sin(x)

