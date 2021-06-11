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

"""Contains classes for stationary wave signals."""

import math
import numpy
import sumpf._internal as sumpf_internal
from ._signal import Signal

__all__ = ("SineWave", "SquareWave")


class Wave(Signal):
    """A base class for wave signals."""

    def __init__(self, frequency, channels, sampling_rate, offset, labels):
        """
        :param frequency: the sine wave's frequency in Hz
        :param phase: a phase offset in radians (e.g. pass pi/2 for a cosine signal)
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the sine wave
        """
        Signal.__init__(self, channels=channels, sampling_rate=sampling_rate, offset=offset, labels=labels)
        self.__periods = self.duration() * frequency

    def periods(self):
        """Returns the number of periods of the wave, that are captured by this signal.

        :returns: a float
        """
        return self.__periods


class SineWave(Wave):
    """A class for a sinusoidal signal."""

    def __init__(self, frequency=1000.0, phase=0.0, sampling_rate=48000.0, length=2 ** 16):
        """
        :param frequency: the sine wave's frequency in Hz
        :param phase: a phase offset in radians (e.g. pass pi/2 for a cosine signal)
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the sine wave
        """
        channels = sumpf_internal.allocate_array(shape=(1, length), dtype=numpy.float64)
        duration = (length - 1) / sampling_rate
        omega_t_plus_phase = numpy.linspace(phase, 2.0 * math.pi * frequency * duration + phase, length)
        numpy.sin(omega_t_plus_phase, out=channels[0])
        Wave.__init__(self,
                      frequency=frequency,
                      channels=channels,
                      sampling_rate=sampling_rate,
                      offset=0,
                      labels=("Sine",))


class SquareWave(Wave):
    """A class for a square wave signal."""

    def __init__(self, frequency=1000.0, phase=0.0, sampling_rate=48000.0, length=2 ** 16):
        """
        :param frequency: the square wave's frequency in Hz
        :param phase: a phase offset in radians
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the sine wave
        """
        channels = sumpf_internal.allocate_array(shape=(1, length), dtype=numpy.float64)
        duration = (length - 1) / sampling_rate
        omega_t_plus_phase = numpy.linspace(phase, 2.0 * math.pi * frequency * duration + phase, length)
        numpy.sin(omega_t_plus_phase, out=channels[0])
        numpy.sign(channels, out=channels)
        Wave.__init__(self,
                      frequency=frequency,
                      channels=channels,
                      sampling_rate=sampling_rate,
                      offset=0,
                      labels=("Square wave",))
