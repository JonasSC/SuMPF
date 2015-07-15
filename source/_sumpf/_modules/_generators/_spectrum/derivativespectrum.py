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
from .spectrumgenerator import SpectrumGenerator


class DerivativeSpectrumGenerator(SpectrumGenerator):
    """
    Objects of this class generate a spectrum with a magnitude, that raises
    proportionally to the frequency. This filter can be used to calculate the
    derivative of a signal in the frequency domain.
    """
    def _GetSample(self, f):
        """
        Defines the value for each sample
        @param f: the frequency of the sample in Hz
        @retval : the value of the generator function at the given frequency
        """
        return 2.0j * math.pi * f / (self._resolution * 2.0 * (self._length - 1))

    def _GetLabel(self):
        """
        Defines the label.
        @retval : a string label
        """
        return "Derivative"

