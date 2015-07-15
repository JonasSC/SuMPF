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
from .signalgenerator import SignalGenerator


class WaveGenerator(SignalGenerator):
    """
    An abstract base class for modules that generate periodic Signals like Sine-
    or Square waves.
    This class takes care of the constructor and the setter methods to set the
    frequency and the phase offset of the output Signal.
    The derived classes have to implement the _GetSample method (or the
    _GetSamples method) and the _GetLabel method.
    """
    def __init__(self, frequency=None, phase=0.0, samplingrate=None, length=None):
        """
        @param frequency: The sine frequency in Hz
        @param phase: The phase of the sine wave in radian
        @param samplingrate: The sampling rate in Hz
        @param length: The number of samples of the signal
        """
        if frequency is None:
            frequency = sumpf.config.get("default_frequency")
        SignalGenerator.__init__(self, samplingrate=samplingrate, length=length)
        self._frequency = float(frequency)
        self._phase = float(phase)

    @sumpf.Input(float, "GetSignal")
    def SetFrequency(self, frequency):
        """
        Sets the frequency of the output Signal.
        @param frequency: The sine frequency in Hz
        """
        self._frequency = float(frequency)

    @sumpf.Input(float, "GetSignal")
    def SetPhase(self, phase):
        """
        Sets the phase of the output Signal.
        @param phase: The phase of the sine wave in radian
        """
        self._phase = float(phase)

    @sumpf.Input(float, "GetSignal")
    def SetPhaseInDegrees(self, degrees):
        """
        Convenience method that calculates the output Signal's phase from the given angle in degrees
        @param degrees: The phase of the sine wave in degrees
        """
        self._phase = 2.0 * math.pi * degrees / 360.0

