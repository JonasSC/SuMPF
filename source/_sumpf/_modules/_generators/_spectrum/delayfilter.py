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
from .spectrumgenerator import SpectrumGenerator


class DelayFilterGenerator(SpectrumGenerator):
    """
    Objects of this class generate a spectrum with a constant magnitude of one
    and with a constant, specifiable group delay.
    """
    def __init__(self, delay=0.0, resolution=None, length=None):
        """
        @param delay: the group delay as a float in seconds
        @param resolution: the resolution of the created spectrum in Hz
        @param length: the number of samples of the spectrum
        """
        SpectrumGenerator.__init__(self, resolution=resolution, length=length)
        self.__delay = delay

    @sumpf.Input(float, "GetSpectrum")
    def SetDelay(self, delay):
        """
        Sets the group delay of the filter.
        @param delay: the group delay as a float in seconds
        """
        self.__delay = delay

    def _GetSample(self, f):
        """
        Defines the value for each sample
        @param f: the frequency of the sample in Hz
        @retval : the value of the generator function at the given frequency
        """
        return math.e ** (-1.0j * self.__delay * 2.0 * math.pi * f)

    def _GetLabel(self):
        """
        Defines the label.
        @retval : a string label
        """
        return "Group Delay"

