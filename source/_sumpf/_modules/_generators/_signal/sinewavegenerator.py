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
from .wavegenerator import WaveGenerator


class SineWaveGenerator(WaveGenerator):
    """
    A class whose instances generate a sine wave.
    The amplitude of the sine wave will always be 1.0. It can be changed by
    sending the resulting Signal through a sumpf.AmplifySignal module.
    The resulting Signal will have one channel.
    """
    def _GetSample(self, t):
        """
        Calculates and returns the value of the sample at time t.
        @param t: the time from the beginning of the signal in seconds
        @retval : the value of the sine function at the given time
        """
        return math.sin(2 * math.pi * self._frequency * t + self._phase)

    def _GetLabel(self):
        """
        Returns the label for the generated channel.
        @retval : the string label
        """
        return "Sine"

