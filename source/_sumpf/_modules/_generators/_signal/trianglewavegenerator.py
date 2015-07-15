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

import math
import sumpf
from .wavegenerator import WaveGenerator


class TriangleWaveGenerator(WaveGenerator):
    """
    A class whose instances generate triangle waves.
    The triangle waves can be modified with the same parameters as a sine wave.
    These parameters are the frequency and the phase, where the phase can be
    given either in radian or in degrees.
    The zero crossings of the triangle wave are at the same places as with a sine
    wave with the same frequency and phase shift. For a raising-ratio of 0.5, this
    means that when T is the period length (1.0/frequency), t is the current time
    index and the phase is 0.0, then the triangle wave will be raising in the
    interval 0.0 <= t < 0.25*T, it will be falling for 0.25*T <= t < 0.75*T and
    then raising again. For t >= T this behavior is continued periodically.
    With the raising parameter, the fraction of the period length in which the
    wave is rising can be specified. This way, the steepness of the raising and
    the falling edge of the wave can be adjusted, for example to create a sawtooth
    wave.
    The amplitude of the triangle wave will always be 1.0. It can be changed by
    sending the resulting Signal through a AmplifySignal module.
    The resulting Signal will have one channel.
    """
    def __init__(self, raising=0.5, frequency=None, phase=0.0, samplingrate=None, length=None):
        """
        @param raising: the fraction of the period length in which the wave is rising. Set a float between 0.0 and 1.0, e.g. 0.5 for a symmetric triangle wave, 1.0 for a sawtooth wave and 0.0 for a backwards sawtooth wave
        @param phase: the phase of the sine wave in radian
        @param samplingrate: the sampling rate in Hz
        @param length: the number of samples of the signal
        """
        WaveGenerator.__init__(self, frequency=frequency, phase=phase, samplingrate=samplingrate, length=length)
        self.__raising = raising

    @sumpf.Input(float, "GetSignal")
    def SetRaising(self, raising):
        """
        Sets the fraction of the period length in which the wave is rising. Give
        a float between 0.0 and 1.0, e.g. 0.5 for a symmetric triangle wave, 1.0
        for a sawtooth wave (the wave raises for the whole period length and then
        falls abruptly) and 0.0 for a backwards sawtooth wave (the wave starts
        with 1.0 and then falls for the entire period length).
        The zero crossings of the triangle wave are at the same places as with a
        sine wave with the same frequency and phase shift, no matter at which
        value the raising-ratio is set.
        @param raising: a float between 0.0 and 1.0
        """
        if 0.0 <= raising <= 1.0:
            self.__raising = raising
        else:
            raise ValueError("The raising-ratio has to be between 0.0 and 1.0")

    def _GetSample(self, t):
        """
        Calculates and returns the value of the sample at time t.
        This is sample is is between 1.0 or -1.0.
        @param t: the time from the beginning of the signal in seconds
        @retval : the value of the square wave function at the given time
        """
        x = t * self._frequency + self._phase / (2.0 * math.pi) + 1.0 - self.__raising / 2.0    # the added values after the phase make the wave synchronous with a sine wave with the same frequency and phase
        r = x - int(x)
        if r < 1.0 - self.__raising:
            return 1.0 - 2.0 * r / (1.0 - self.__raising)
        else:
            return -1.0 + 2.0 * (r - 1.0 + self.__raising) / self.__raising

    def _GetLabel(self):
        """
        Returns the label for the generated channel.
        @retval : the string label
        """
        return "Triangle"

