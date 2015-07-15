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
from .spectrumgenerator import SpectrumGenerator


class ConstantSpectrumGenerator(SpectrumGenerator):
    """
    Generates a Spectrum whose data is a sequence of constant samples with the
    given length and the given resolution.
    The resulting Spectrum will have one channel.
    """
    def __init__(self, value=1.0, resolution=None, length=None):
        """
        @param value: the constant float value of each sample
        @param resolution: the resolution of the created spectrum in Hz
        @param length: the number of samples of the spectrum
        """
        SpectrumGenerator.__init__(self, resolution=resolution, length=length)
        self.__value = value

    @sumpf.Input(float, "GetSpectrum")
    def SetValue(self, value):
        """
        Sets the constant value.
        @param value: the constant float value of each sample
        """
        self.__value = value

    def _GetSample(self, f):
        """
        Defines the value for each sample
        @param f: the frequency of the sample in Hz
        @retval : the value of the generator function at the given frequency
        """
        return self.__value

    def _GetLabel(self):
        """
        Defines the label.
        @retval : a string label
        """
        return "Constant"

