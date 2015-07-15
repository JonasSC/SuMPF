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


class RectangleFilterGenerator(SpectrumGenerator):
    """
    Generates a Spectrum whose samples outside the given frequency band are zero
    and one inside the frequency band.
    It is also possible to invert the spectrum, so that the samples outside the
    frequency band are one and the inside samples are zero.
    """
    def __init__(self, start_frequency=20.0, stop_frequency=20000.0, invert=False, resolution=None, length=None):
        """
        @param start_frequency: the smallest frequency as a float in Hz that shall be inside the frequency band
        @param stop_frequency: the smallest frequency as a float in Hz that shall be outside above the frequency band
        @param invert: if False, the samples inside the frequency band are one, if False, the samples outside the frequency band are one.
        @param resolution: the resolution of the created spectrum in Hz
        @param length: the number of samples of the spectrum
        """
        SpectrumGenerator.__init__(self, resolution=resolution, length=length)
        self.__start_frequency = start_frequency
        self.__stop_frequency = stop_frequency
        self.__invert = invert

    @sumpf.Input(float, "GetSpectrum")
    def SetStartFrequency(self, frequency):
        """
        Sets the start frequency for the frequency band.
        @param frequency: the smallest frequency as a float in Hz that shall be inside the frequency band
        """
        self.__start_frequency = frequency

    @sumpf.Input(float, "GetSpectrum")
    def SetStopFrequency(self, frequency):
        """
        Sets the stop frequency for the frequency band.
        @param frequency: the smallest frequency as a float in Hz that shall be outside above the frequency band
        """
        self.__stop_frequency = frequency

    @sumpf.Input(bool, "GetSpectrum")
    def SetInvert(self, invert):
        """
        Specifies, if the filter function shall be inverted.
        If the inversion is set to False, all samples outside the frequency band
        are zero, while the samples inside the frequency band are one. If it is
        True, the samples outside the frequency band are one, while the inside
        samples are zero.
        @param invert: if False, the samples inside the frequency band are one, if False, the samples outside the frequency band are one.
        """
        self.__invert = invert

    def _GetSample(self, f):
        """
        Defines the value for each sample
        @param f: the frequency of the sample in Hz
        @retval : the value of the generator function at the given frequency
        """
        if self.__invert:
            if self.__start_frequency <= f and f < self.__stop_frequency:
                return 0.0
            else:
                return 1.0
        else:
            if self.__start_frequency <= f and f < self.__stop_frequency:
                return 1.0
            else:
                return 0.0

    def _GetLabel(self):
        """
        Defines the label.
        @retval : a string label
        """
        return "Rectangle"

