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

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy



class NormalizeSpectrumToFrequency(object):
    """
    Normalizes the channels of a Spectrum instance so that its magnitude at a
    given frequency is 1.0.
    The value of the input Spectrum at the given frequency will be calculated by
    linearly interpolating the Spectrum's magnitude.
    If the magnitude for the given frequency is 0.0, the channel will not be
    normalized to avoid divisions by zero.

    Note that this works differently compared to the NormalizeSignal module. A
    normalized Spectrum which is then inversely fourier transformed does not
    necessarily result in a normalized Signal.
    """
    def __init__(self, input=None, frequency=1000.0):
        """
        All parameters are optional
        @param input: the Spectrum which shall be normalized
        @param frequency: the frequency at which the magnitude shall be 1.0
        """
        self.__spectrum = input
        self.__frequency = float(frequency)

    @sumpf.Output(sumpf.Spectrum)
    def GetOutput(self):
        """
        Generates the normalized Spectrum and returns it.
        @retval : the normalized Spectrum
        """
        spectrum = None
        if self.__spectrum is None:
            spectrum = sumpf.Spectrum()
        else:
            index = self.__frequency / self.__spectrum.GetResolution()
            lower_index = int(math.floor(index))
            channels = []
            for i in range(len(self.__spectrum.GetChannels())):
                lower, upper = self.__spectrum.GetMagnitude()[i][lower_index:lower_index + 2]
                quotient = lower * (1.0 - index + lower_index) + upper * (index - lower_index)
                if quotient == 0.0:
                    channels.append(self.__spectrum.GetChannels()[i])
                else:
                    channels.append(tuple(numpy.divide(self.__spectrum.GetChannels()[i], quotient)))
            spectrum = sumpf.Spectrum(channels=tuple(channels), resolution=self.__spectrum.GetResolution(), labels=self.__spectrum.GetLabels())
        return spectrum

    @sumpf.Input(sumpf.Spectrum, "GetOutput")
    def SetInput(self, spectrum):
        """
        Method for setting the Spectrum which shall be normalized.
        @param spectrum: the Spectrum which shall be normalized
        """
        self.__spectrum = spectrum

    @sumpf.Input(float, "GetOutput")
    def SetFrequency(self, frequency):
        """
        Sets the frequency at which the magnitude of the Spectrum shall be
        normalized to 1.0.
        @param frequency: the frequency as a float value
        """
        self.__frequency = float(frequency)

