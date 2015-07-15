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
from .signalgenerator import SignalGenerator


class ImpulseGenerator(SignalGenerator):
    """
    A class whose instances generate an impulse or a sequence of impulses.
    It is possible to give a frequency, with which the impulses are repeated.
    A frequency of 0.0 will lead to only one impulse.
    The first impulse will always occur after the given initial delay, independent
    of the given frequency.
    If a frequency is given, the impulses will be repeated at a rate that is the
    integer number of samples, which is closest to that frequency. This way, the
    resulting frequency might not be exactly as specified, but the gaps between
    the impulses do all have the same length.
    The amplitude of the impulses will always be one. It can be changed by
    sending the resulting Signal through a sumpf.AmplifySignal module.
    The resulting Signal will have one channel.
    """
    def __init__(self, delay=0.0, frequency=0.0, samplingrate=None, length=None):
        """
        @param delay: The delay before the first impulse in seconds
        @param frequency: The frequency in which the impulses repeat; 0.0 means no repetition (see SetFrequency)
        @param samplingrate: The sampling rate in Hz
        @param length: The number of samples of the signal
        """
        SignalGenerator.__init__(self, samplingrate=samplingrate, length=length)
        self.__delay = float(delay)
        self.__frequency = float(frequency)

    def _GetSample(self, t):
        """
        Calculates and returns the value of the sample at time t.
        @param t: the time from the beginning of the signal in seconds
        @retval : the value of the impulse function at the given time
        """
        first_impulse_sample = int(round(self.__delay * self._samplingrate))
        if first_impulse_sample > self._length:
            raise ValueError("Initial delay is greater than signal length")
        current_sample = int(round(t * self._samplingrate))
        impulse_distance = self._length
        if self.__frequency > 0.0:
            impulse_distance = int(round(self._samplingrate / self.__frequency))
        if (current_sample - first_impulse_sample) % impulse_distance == 0:
            return 1.0
        else:
            return 0.0

    def _GetLabel(self):
        """
        Returns the label for the generated channel.
        @retval : the string label
        """
        if self.__frequency > 0.0:
            return "Impulse Sequence"
        else:
            return "Impulse"

    @sumpf.Input(float, "GetSignal")
    def SetDelay(self, delay):
        """
        @param delay: The delay before the first impulse in seconds
        """
        self.__delay = float(delay)

    @sumpf.Input(float, "GetSignal")
    def SetFrequency(self, frequency):
        """
        Sets the frequency by which the impulses shall repeat. If the frequency does not divide
        the sampling rate cleanly, the frequency is rounded. This way, the number of samples between
        the impulses is constant.
        @param frequency: The frequency in which the impulses repeat; 0.0 means no repetition
        """
        self.__frequency = float(frequency)

