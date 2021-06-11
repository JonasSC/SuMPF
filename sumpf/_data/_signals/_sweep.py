# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2021 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""Contains classes for exponential sweep signals."""

import collections
import math
import numpy
import sumpf._internal as sumpf_internal
from ._signal import Signal

try:
    import numexpr
except ImportError:
    numexpr = False

__all__ = ("LinearSweep", "InverseLinearSweep", "ExponentialSweep", "InverseExponentialSweep")

####################
# helper functions #
####################


def general_sweep_parameters(interval, sampling_rate, length):
    """A helper function that computes parameters, that are used by the sweep classes."""
    start, stop = sumpf_internal.index(interval, length)
    sweep_offset = start / sampling_rate
    sweep_length = stop - start
    sweep_duration = sweep_length / sampling_rate
    t = numpy.linspace(-sweep_offset, (length - 1) / sampling_rate - sweep_offset, length)  # the time values for the samples
    return start, stop, t, sweep_duration, sweep_offset


def linear_sweep_parameters(start_frequency, stop_frequency, interval, sampling_rate, length):
    """A helper function that computes parameters, that are used by both the
    LinearSweep and the InverseLinearSweep classes.
    """
    start, stop, t, sweep_duration, sweep_offset = general_sweep_parameters(interval, sampling_rate, length)
    k = (stop_frequency - start_frequency) / sweep_duration
    a = 2.0 * math.pi * start_frequency
    b = math.pi * k
    return start, stop, t, sweep_duration, sweep_offset, a, b, k


def exponential_sweep_parameters(start_frequency, stop_frequency, interval, sampling_rate, length):
    """A helper function that computes parameters, that are used by both the
    ExponentialSweep and the InverseExponentialSweep classes.
    """
    start, stop, t, sweep_duration, sweep_offset = general_sweep_parameters(interval, sampling_rate, length)
    frequency_ratio = stop_frequency / start_frequency
    l = sweep_duration / math.log(frequency_ratio)
    a = 2.0 * math.pi * start_frequency * l
    return start, stop, t, sweep_duration, sweep_offset, l, a


def apply_delay(channels, sampling_rate, delay, out):
    """A helper function, that applies a delay to signal channels by multiplying
    with ``exp(2j * pi * f * delay)`` in the frequency domain
    """
    if channels.size:
        spectrum = numpy.fft.rfft(channels)
        f = numpy.linspace(0.0, sampling_rate / 2.0, spectrum.shape[-1])
        spectrum *= numpy.exp(2j * math.pi * f * delay)
        signal = numpy.fft.irfft(spectrum, n=channels.shape[-1])
        out[:, 0:signal.shape[1]] = signal[:, 0:out.shape[1]]
    else:
        out[:] = channels[:]

################
# base classes #
################


class Sweep(Signal):
    """Base class for swept sine signals"""

    def __init__(self, channels, sampling_rate, offset, function):
        """
        :param channels: the channels array with the sweep's samples
        :param sampling_rate: the sampling rate of the sweep
        :param offset: an integer number of samples, by which the first sample of
                       the channel is delayed virtually. The offset can also be
                       negative, if the signal shall be non-causal.
        :param function: a function, that takes a point in time as a float in seconds
                         and computes the instantaneous frequency of the sweep
                         at that point in time.
        """
        a, b = (function(0.0), function(len(channels[0]) / sampling_rate))
        if a <= b:
            Signal.__init__(self,
                            channels=channels,
                            sampling_rate=sampling_rate,
                            offset=offset,
                            labels=("Sweep",))
            self.__minimum_frequency = a
            self.__maximum_frequency = b
        else:
            Signal.__init__(self,
                            channels=channels,
                            sampling_rate=sampling_rate,
                            offset=offset,
                            labels=("Inverse sweep",))
            self.__minimum_frequency = b
            self.__maximum_frequency = a
        self.__function = function

    def minimum_frequency(self):
        """Returns the lowest frequency, that is excited by the sweep. If an
        interval has been specified, this frequency might be lower than the start
        frequency.

        :returns: the frequency in Hz as a float
        """
        return self.__minimum_frequency

    def maximum_frequency(self):
        """Returns the highest frequency, that is excited by the sweep. If an
        interval has been specified, this frequency might be higher than the stop
        frequency. Beware of the sampling theorem!

        :returns: the frequency in Hz as a float
        """
        return self.__maximum_frequency

    def instantaneous_frequency(self, t):
        """Returns the instantaneous frequency of the sweep at time t.

        :param t: a point in time as a float or multiple points in time as an array
        :returns: a float frequency or an array of frequencies
        """
        if isinstance(t, collections.abc.Iterable):
            f = numpy.vectorize(self.__function)
            return f(t)
        else:
            return self.__function(t)


class BaseExponentialSweep(Sweep):
    """Base class for (inverse) exponential sweeps"""

    def __init__(self, channels, sampling_rate, offset, function, l):
        """
        :param channels: the channels array with the sweep's samples
        :param sampling_rate: the sampling rate of the sweep
        :param offset: an integer number of samples, by which the first sample of
                       the channel is delayed virtually. The offset can also be
                       negative, if the signal shall be non-causal.
        :param function: a function, that takes a point in time as a float in seconds
                         and computes the instantaneous frequency of the sweep
                         at that point in time.
        :param l: the sweep rate `sweep_duration / log(stop_frequency / start_frequency)`
        """
        Sweep.__init__(self, channels=channels, sampling_rate=sampling_rate, offset=offset, function=function)
        self.__l = l

    def harmonic_impulse_response(self, impulse_response, harmonic, length=None):
        """Cuts out the impulse response of the given harmonic from an impulse
        response of a system, that has been measured with this sweep.

        :param impulse_response: the :class:`~sumpf.Signal` instance with the
                                 complete impulse response of the system. The
                                 signal's offset shall point to the beginning
                                 of the linear impulse response.
        :param harmonic: the integer order of the harmonic, that shall be cut out.
                         ``1`` is the linear part, while the harmonics with an order
                         of ``2`` and higher come from nonlinearities in the system
        :param length: the integer length, that the harmonic impulse response
                       shall have. This will be achieved by cropping or zero
                       padding. If this is None, the length will be determined
                       automatically and it will vary for the different orders
                       of harmonics.
        """
        offset = impulse_response.offset()
        sampling_rate = impulse_response.sampling_rate()
        # cut out the harmonic impulse response from the signal
        if harmonic == 1:
            channels = impulse_response.channels()[:, -offset:]
            remaining_delay = None
        else:
            delay = math.log(harmonic) * self.__l
            shift = math.ceil(delay * sampling_rate)
            start = -int(shift) - offset
            remaining_delay = shift / sampling_rate - delay
            if harmonic == 2:
                stop = -offset
            else:
                stop = -int(math.floor(math.log(harmonic - 1) * self.__l * sampling_rate)) - offset
            if stop == 0 or (start < 0 and stop >= 0):  # pylint: disable=chained-comparison; can't see what's wrong with this
                stop = None
            channels = impulse_response.channels()[:, start:stop]
        # zero-pad or crop the impulse response, so it has the desired length
        if length is not None:
            channel_count, harmonic_length = channels.shape
            if harmonic_length < length:
                new_channels = sumpf_internal.allocate_array(shape=(channel_count, length))
                new_channels[:, 0:harmonic_length] = channels
                new_channels[:, harmonic_length:] = 0.0
                if remaining_delay is not None:
                    apply_delay(channels=new_channels,
                                sampling_rate=sampling_rate,
                                delay=remaining_delay,
                                out=new_channels)
                channels = new_channels
            elif harmonic_length > channel_count:
                if remaining_delay is not None:
                    new_channels = sumpf_internal.allocate_array(shape=(channel_count, length))
                    apply_delay(channels=channels,
                                sampling_rate=sampling_rate,
                                delay=remaining_delay,
                                out=new_channels)
                    channels = new_channels
                else:
                    channels = channels[:, 0:length]
        elif remaining_delay is not None:
            apply_delay(channels=channels,
                        sampling_rate=sampling_rate,
                        delay=remaining_delay,
                        out=channels)
        # return the impulse response of the harmonic
        h = sumpf_internal.counting_number(harmonic)
        return Signal(channels=channels,
                      sampling_rate=sampling_rate,
                      offset=0,
                      labels=[f"{l} ({h} harmonic)" for l in impulse_response.labels()])

################
# linear sweep #
################


class LinearSweep(Sweep):
    """A class for a swept sine signal whose frequency increases linearly with time"""

    def __init__(self, start_frequency=20.0, stop_frequency=20000.0, phase=0.0,
                 interval=(0, 1.0), sampling_rate=48000.0, length=2 ** 16):
        """
        :param start_frequency: the start frequency in Hz
        :param stop_frequency: the stop frequency in Hz
        :param phase: a phase offset in radians (e.g. pass pi/2 for a cosine sweep)
        :param interval: a tuple, list or array of two numbers, that specify the
                         indices of the samples, at which the start and the stop
                         frequencies shall be excited. The sweep will continue
                         outside this interval. This functionality is useful, if
                         the sweep shall be faded in or out and the range between
                         the start and the stop frequency shall not be affected
                         by the fading.
                         The indices can be specified as integer indices or as
                         floats between 0.0 and 1.0, which are mapped to 0 and
                         ``length``. Negative indices (also possible with floats)
                         are relative to the end of the signal.
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the sweep
        """
        # allocate shared memory for the channels
        channels = sumpf_internal.allocate_array(shape=(1, length), dtype=numpy.float64)
        # generate the sweep
        _, _, t, _, sweep_offset, a, b, k = linear_sweep_parameters(start_frequency=start_frequency,
                                                                    stop_frequency=stop_frequency,
                                                                    interval=interval,
                                                                    sampling_rate=sampling_rate,
                                                                    length=length)
        if length <= 8192 or not numexpr:   # for short sweeps NumExpr is slower than NumPy
            array = t * t
            array *= b
            array += a * t
            array += phase
            numpy.sin(array, out=channels[0, :])
        else:
            numexpr.evaluate(ex="sin(phase + a * t + b * (t**2))", out=channels[0, :], optimization="moderate")
        # store the values and parameters
        Sweep.__init__(self,
                       channels=channels,
                       sampling_rate=sampling_rate,
                       offset=0,
                       function=lambda tau: start_frequency + k * (tau - sweep_offset))


class InverseLinearSweep(Sweep):
    """Creates an inverse for a linear sweep.
    In the excited frequency range, the convolution of a sweep with its inverse
    results in a unit impulse.

    In order to be able to use the same parameters to generate a sweep and its
    inverse, the ``start_frequency`` and ``stop_frequency`` parameters are
    swapped for the inverse sweep. An inverse sweep actually excites the
    start frequency at the end.

    The offset of this sweep is chosen to work with a non-circular convolution
    (convolution modes ``FULL`` or ``SPECTRUM_PADDED``). When performing a circular
    convolution (convolution mode ``SPECTRUM``), the resulting impulse response
    will be fully non-causal. In this case, it is recommended to set either the
    inverse sweep's offset or the impulse response's offset to 0 by calling their
    :meth:`~sumpf.InverseLinearSweep.shift` method with parameter ``None``.
    """

    def __init__(self, start_frequency=20.0, stop_frequency=20000.0, phase=0.0,
                 interval=(0, 1.0), sampling_rate=48000.0, length=2 ** 16):
        """
        :param start_frequency: the start frequency in Hz
        :param stop_frequency: the stop frequency in Hz
        :param phase: a phase offset in radians (e.g. pass pi/2 for a cosine sweep)
        :param interval: a tuple, list or array of two numbers, that specify the
                         indices of the samples, at which the start and the stop
                         frequencies shall be excited. The sweep will continue
                         outside this interval. This functionality is useful, if
                         the sweep shall be faded in or out and the range between
                         the start and the stop frequency shall not be affected
                         by the fading.
                         The indices can be specified as integer indices or as
                         floats between 0.0 and 1.0, which are mapped to 0 and
                         ``length``. Negative indices (also possible with floats)
                         are relative to the end of the signal.
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the sweep
        """
        # allocate shared memory for the channels
        channels = sumpf_internal.allocate_array(shape=(1, length), dtype=numpy.float64)
        # generate the sweep
        start, stop, t, T, sweep_offset, a, b, k = linear_sweep_parameters(start_frequency=start_frequency,
                                                                           stop_frequency=stop_frequency,
                                                                           interval=interval,
                                                                           sampling_rate=sampling_rate,
                                                                           length=length)
        t *= -1.0
        t += T
        s = 2.0 / (stop - start)    # a scaling factor, so that the convolution of the sweep and the inverse sweep results in a unit impulse
        if length <= 8192 or not numexpr:   # for short sweeps NumExpr is slower than NumPy
            array = t * t
            array *= b
            array += a * t
            array += phase + 0.0
            numpy.sin(array, out=channels[0, :])
            channels *= s
        else:
            numexpr.evaluate(ex="s * sin(phase + a * t + b * (t**2))", out=channels[0, :], optimization="moderate")
        # store the values and parameters
        Sweep.__init__(self,
                       channels=channels,
                       sampling_rate=sampling_rate,
                       offset=-stop - start,
                       function=lambda tau: stop_frequency - k * (tau - sweep_offset))

######################
# exponential sweeps #
######################


class ExponentialSweep(BaseExponentialSweep):
    """A class for a swept sine signal whose frequency increases exponentially with time"""

    def __init__(self, start_frequency=20.0, stop_frequency=20000.0, phase=0.0,
                 interval=(0, 1.0), sampling_rate=48000.0, length=2 ** 16):
        """
        :param start_frequency: the start frequency in Hz
        :param stop_frequency: the stop frequency in Hz
        :param phase: a phase offset in radians (e.g. pass pi/2 for a cosine sweep)
        :param interval: a tuple, list or array of two numbers, that specify the
                         indices of the samples, at which the start and the stop
                         frequencies shall be excited. The sweep will continue
                         outside this interval. This functionality is useful, if
                         the sweep shall be faded in or out and the range between
                         the start and the stop frequency shall not be affected
                         by the fading.
                         The indices can be specified as integer indices or as
                         floats between 0.0 and 1.0, which are mapped to 0 and
                         ``length``. Negative indices (also possible with floats)
                         are relative to the end of the signal.
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the sweep
        """
        # allocate shared memory for the channels
        channels = sumpf_internal.allocate_array(shape=(1, length), dtype=numpy.float64)
        # generate the sweep
        _, _, t, _, sweep_offset, l, a = exponential_sweep_parameters(start_frequency,
                                                                      stop_frequency,
                                                                      interval,
                                                                      sampling_rate,
                                                                      length)
        if length <= 8192 or not numexpr:   # for short sweeps NumExpr is slower than NumPy
            array = t
            array /= l
            numpy.expm1(array, out=array)
            array *= a
            array += phase
            numpy.sin(array, out=channels[0, :])
        else:
            numexpr.evaluate(ex="sin(a * expm1(t / l) + phase)", out=channels[0, :], optimization="moderate")
        # store the values and parameters
        BaseExponentialSweep.__init__(self,
                                      channels=channels,
                                      sampling_rate=sampling_rate,
                                      offset=0,
                                      function=lambda tau: start_frequency * math.exp((tau - sweep_offset) / l),
                                      l=l)


class InverseExponentialSweep(BaseExponentialSweep):
    """Creates an inverse for an exponential sweep.
    In the excited frequency range, the convolution of a sweep with its inverse
    results in a unit impulse.

    In order to be able to use the same parameters to generate a sweep and its
    inverse, the ``start_frequency`` and ``stop_frequency`` parameters are
    swapped for the inverse sweep. An inverse sweep actually excites the
    start frequency at the end.

    The offset of this sweep is chosen to work with a non-circular convolution
    (convolution modes ``FULL`` or ``SPECTRUM_PADDED``). When performing a circular
    convolution (convolution mode ``SPECTRUM``), the resulting impulse response
    will be fully non-causal. In this case, it is recommended to set either the
    inverse sweep's offset or the impulse response's offset to 0 by calling their
    :meth:`~sumpf.InverseExponentialSweep.shift` method with parameter ``None``.
    """

    def __init__(self, start_frequency=20.0, stop_frequency=20000.0, phase=0.0,
                 interval=(0, 1.0), sampling_rate=48000.0, length=2 ** 16):
        """
        :param start_frequency: the start frequency in Hz (this is usually the
                                lowest frequency, that is excited at the end of
                                an inverse sweep, but at the beginning of a regular
                                sweep)
        :param start_frequency: the stop frequency in Hz (this is usually the
                                highest frequency, that is excited at the beginning
                                of an inverse sweep, but at the end of a regular
                                sweep)
        :param phase: a phase offset in radians (e.g. pass pi/2 for a inverse
                      cosine sweep)
        :param interval: a tuple, list or array of two numbers, that specify the
                         indices of the samples, at which the start and the stop
                         frequencies shall be excited. The sweep will continue
                         outside this interval. This functionality is useful, if
                         the sweep shall be faded in or out and the range between
                         the start and the stop frequency shall not be affected
                         by the fading.
                         The indices can be specified as integer indices or as
                         floats between 0.0 and 1.0, which are mapped to 0 and
                         ``length``. Negative indices (also possible with floats)
                         are relative to the end of the signal.
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the inverse sweep
        """
        # allocate shared memory for the channels
        channels = sumpf_internal.allocate_array(shape=(1, length), dtype=numpy.float64)
        # generate the sweep
        start, stop, t, T, sweep_offset, l, a = exponential_sweep_parameters(start_frequency,
                                                                             stop_frequency,
                                                                             interval,
                                                                             sampling_rate,
                                                                             length)
        s = 2.0 * start_frequency / l / (stop_frequency - start_frequency) / sampling_rate      # a scaling factor, so that the convolution of the sweep and the inverse sweep results in a unit impulse
        if length <= 8192 or not numexpr:   # for short sweeps NumExpr is slower than NumPy
            exponent = numpy.subtract(T, t, out=t)
            exponent /= l
            # compute the envelope
            envelope = numpy.exp(exponent)
            envelope *= s
            # compute the sweep
            sweep = numpy.expm1(exponent, out=exponent)
            sweep *= a
            sweep += phase
            numpy.sin(sweep, out=sweep)
            # combine the envelope and the sweep
            numpy.multiply(envelope, sweep, out=channels[0, :])
        else:
            envelope = "s * exp((T-t) / l)"
            sweep = "sin(a * expm1((T-t) / l) + phase)"
            numexpr.evaluate(ex=f"{envelope} * {sweep}", out=channels[0, :], optimization="moderate")
        # store the values and parameters
        BaseExponentialSweep.__init__(self,
                                      channels=channels,
                                      sampling_rate=sampling_rate,
                                      offset=-stop - start,
                                      function=lambda tau: stop_frequency * math.exp((-tau + sweep_offset) / l),
                                      l=l)
