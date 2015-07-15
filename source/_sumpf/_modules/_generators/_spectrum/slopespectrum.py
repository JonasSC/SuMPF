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


class SlopeSpectrumGenerator(SpectrumGenerator):
    """
    Objects of this class generate spectrums whose magnitude is falling with a
    given slope.
    The slope is defined by the function 1/(f**x), where f is the frequency and
    x is an exponent that can be chosen freely. It is also possible to define a
    start frequency, before which the magnitude is constantly one.
    The phase of the output spectrum is always zero.
    """
    def __init__(self, exponent=1.0, start_frequency=1.0, resolution=None, length=None):
        """
        @param exponent: a float exponent, that defines the slope with the function 1/(f**exponent)
        @param start_frequency: the frequency as a float in Hz, at which the slope shall start
        @param resolution: the resolution of the created spectrum in Hz
        @param length: the number of samples of the spectrum
        """
        SpectrumGenerator.__init__(self, resolution=resolution, length=length)
        self.__exponent = exponent
        self.__start_frequency = start_frequency

    @sumpf.Input(float, "GetSpectrum")
    def SetExponent(self, exponent):
        """
        Sets the exponent, that defines the slope with the function 1/(f**exponent).
        @param exponent: a float
        """
        self.__exponent = exponent

    @sumpf.Input(float, "GetSpectrum")
    def SetStartFrequency(self, frequency):
        """
        Sets the start frequency for the slope.
        @param start_frequency: the frequency as a float in Hz, at which the slope shall start
        """
        self.__start_frequency = frequency

    def _GetSample(self, f):
        """
        Defines the value for each sample
        @param f: the frequency of the sample in Hz
        @retval : the value of the generator function at the given frequency
        """
        if f <= self.__start_frequency:
            return 1.0
        elif self.__start_frequency == 0.0:
            return 1.0 / (f ** self.__exponent)
        else:
            return 1.0 / (f ** self.__exponent) / (1.0 / (self.__start_frequency ** self.__exponent))

    def _GetLabel(self):
        """
        Defines the label.
        @retval : a string label
        """
        return "Slope"

