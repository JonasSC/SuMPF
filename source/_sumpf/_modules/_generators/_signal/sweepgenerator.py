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

import math
import sumpf
from .signalgenerator import SignalGenerator


class SweepFunction(object):
    """
    A base class, that defines the interface for different functions by which the
    instantaneous frequency of a sweep increases with time.
    """
    @staticmethod
    def precompute_values(f0, fT, T):
        """
        This static method is called before actually generating the sweep. It
        precomputes and returns values, that are independent of the sample, so
        that their use increases the computation speed of the individual samples.
        @param f0: the start frequency of the sweep in Hz as a float
        @param f0: the stop frequency of the sweep in Hz as a float
        @param T: the duration, that it takes the sweep to go from the start to the stop frequency, in seconds as a float
        @retval : a tuple of precomputed values
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    @staticmethod
    def compute_sample(t, *precomputed):
        """
        This static method is called to compute each individual sample.
        @param t: the time of the sample in seconds as a float
        @param *precomputed: the parameters, that have been precomputed by the precompute_values method
        @retval : the computed sample
        """
        raise NotImplementedError("This method should have been overridden in a derived class")



class LinearIncrease(SweepFunction):
    """
    This class defines a linear increase of the sweep's frequency over time.
    """
    @staticmethod
    def precompute_values(f0, fT, T):
        """
        This static method is called before actually generating the sweep. It
        precomputes and returns values, that are independent of the sample, so
        that their use increases the computation speed of the individual samples.
        @param f0: the start frequency of the sweep in Hz as a float
        @param f0: the stop frequency of the sweep in Hz as a float
        @param T: the duration, that it takes the sweep to go from the start to the stop frequency, in seconds as a float
        @retval : a tuple of precomputed values
        """
        k = (fT - f0) / T
        return (2.0 * math.pi * f0, 2.0 * math.pi * k / 2.0)

    @staticmethod
    def compute_sample(t, *precomputed):
        """
        This static method is called to compute each individual sample.
        @param t: the time of the sample in seconds as a float
        @param *precomputed: the parameters, that have been precomputed by the precompute_values method
        @retval : the computed sample
        """
        x = precomputed[0] * t + precomputed[1] * (t ** 2)
        return math.sin(x)



class ExponentialIncrease(SweepFunction):
    """
    This class defines an exponential increase of the sweep's frequency over time.
    """
    @staticmethod
    def precompute_values(f0, fT, T):
        """
        This static method is called before actually generating the sweep. It
        precomputes and returns values, that are independent of the sample, so
        that their use increases the computation speed of the individual samples.
        @param f0: the start frequency of the sweep in Hz as a float
        @param f0: the stop frequency of the sweep in Hz as a float
        @param T: the duration, that it takes the sweep to go from the start to the stop frequency, in seconds as a float
        @retval : a tuple of precomputed values
        """
        k = (fT / f0) ** (1.0 / T)
        l = math.log(k)
        f = 2.0 * math.pi * f0 / l
        return (k, f)

    @staticmethod
    def compute_sample(t, *precomputed):
        """
        This static method is called to compute each individual sample.
        @param t: the time of the sample in seconds as a float
        @param *precomputed: the parameters, that have been precomputed by the precompute_values method
        @retval : the computed sample
        """
        k, f = precomputed
        e = (k ** t) - 1.0
        return math.sin(f * e)



class SynchronizedExponentialIncrease(SweepFunction):
    """
    This class defines an exponential increase of the sweep's frequency over time.
    Additionally, the sweeps frequency increase rate is adjusted to "synchronize
    the phase" of the sweep.
    Synchronization means in this context, that a sweep, that is shifted by the
    time it takes to sweep from one frequency to an integer multiple of that frequency
    is identical to an unshifted sweep, whose start and stop frequencies are multiplied
    with the same integer factor. This implies, that the sweep (which starts with
    a zero sample) has zero samples at each point in time, when it reaches an integer
    multiple of the start frequency.
    This is being done by a rounding operation, that affects the stop frequency
    of the sweep. This means, that the stop frequency is neither guaranteed to
    be reached by the sweep, nor is it guaranteed to be the highest frequency,
    that is excited by the sweep.
    The synchronized sweep was proposed by Antonin Novak in his PHD thesis:
    http://ant-novak.com/publications.php
    """
    @staticmethod
    def precompute_values(f0, fT, T):
        """
        This static method is called before actually generating the sweep. It
        precomputes and returns values, that are independent of the sample, so
        that their use increases the computation speed of the individual samples.
        @param f0: the start frequency of the sweep in Hz as a float
        @param f0: the stop frequency of the sweep in Hz as a float
        @param T: the duration, that it takes the sweep to go from the start to the stop frequency, in seconds as a float
        @retval : a tuple of precomputed values
        """
        l = math.log((fT / f0) ** (1.0 / T))
        L = 1.0 / f0 * round(f0 / l)
        k = math.exp(1.0 / L)
        f = 2.0 * math.pi * f0 * L
        return (k, f)

    @staticmethod
    def compute_sample(t, *precomputed):
        """
        This static method is called to compute each individual sample.
        @param t: the time of the sample in seconds as a float
        @param *precomputed: the parameters, that have been precomputed by the precompute_values method
        @retval : the computed sample
        """
        k, f = precomputed
        e = (k ** t) - 1.0
        return math.sin(f * e)



class SweepGenerator(SignalGenerator):
    """
    A class whose instances generate a sine wave that sweeps its frequency from
    the start frequency to the stop frequency. Such a Signal is known as sweep
    or chirp.
    The amplitude of the sweep will always be one. It can be changed by
    sending the resulting Signal through a sumpf.Multiply module.
    The resulting Signal will have one channel.
    """

    LINEAR = LinearIncrease
    EXPONENTIAL = ExponentialIncrease
    SYNCHRONIZED = SynchronizedExponentialIncrease

    def __init__(self, start_frequency=20.0, stop_frequency=20000.0, function=EXPONENTIAL, interval=None, samplingrate=None, length=None):
        """
        @param start_frequency: the frequency at the beginning in Hz
        @param stop_frequency: the frequency at the end in Hz
        @param function: one of the flags for the SweepGenerators frequency increase functions (e.g. LINEAR or EXPONENTIAL)
        @param interval: None or a tuple (start, stop) that defines the interval of samples in which shall be swept through the frequencies. See SetInterval for details
        @param samplingrate: the sampling rate in Hz
        @param length: the number of samples of the signal
        """
        SignalGenerator.__init__(self, samplingrate=samplingrate, length=length)
        self.__start = float(start_frequency)
        self.__stop = float(stop_frequency)
        self.__function = function
        self.__interval = interval
        self.__precomputed = None
        self.__offset = 0.0

    def _GetSamples(self):
        """
        Generates the samples of the sweep and returns them as a tuple.
        @retval : a tuple of samples
        """
        self.__PrecomputeValues()
        return SignalGenerator._GetSamples(self)

    def _GetSample(self, t):
        """
        Calculates and returns the value of the sample at time t.
        @param t: the time from the beginning of the signal in seconds
        @retval : the value of the sweep function at the given time
        """
        return self.__function.compute_sample(t - self.__offset, *self.__precomputed)

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

    @sumpf.Input(SweepFunction, "GetSignal")
    def SetSweepFunction(self, function):
        """
        Sets the function that defines the raising of the instantaneous frequency
        of the sweep.
        @param function: a class of a frequency increase function such as SweepGenerator.LINEAR, SweepGenerator.EXPONENTIAL or SweepGenerator.SYNCHRONIZED
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

    def __PrecomputeValues(self):
        """
        Calculates the precomputable values for the sweep and stores them.
        This way these values do not need to be calculated for each sample
        individually.
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
        self.__precomputed = self.__function.precompute_values(f0, fT, T)

