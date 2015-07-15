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

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy



class ChannelDataMean(object):
    """
    Abstract base class for calculating the mean value of each channel of a
    ChannelData instance.
    """
    def __init__(self, data):
        """
        @param data: the ChannelData instance for which the mean values shall be calculated
        """
        self.__data = data

    def _SetData(self, data):
        """
        Protected method to set the Data for which the mean values shall be calculated.
        @param data: the ChannelData instance for which the mean values shall be calculated
        """
        self.__data = data

    @sumpf.Output(tuple)
    def GetMean(self):
        """
        Calculates and returns a tuple of mean values. One value for each channel
        of the input data.
        @retval : a tuple of mean values
        """
        result = []
        for c in self.__data.GetChannels():
            result.append(numpy.mean(c))
        return tuple(result)



class SignalMean(ChannelDataMean):
    """
    Calculates the mean value for each channel of a Signal instance. The values
    are returned as a tuple of floats.
    """
    def __init__(self, signal=None):
        """
        @param signal: the Signal instance for which the mean values shall be calculated
        """
        if signal is None:
            signal = sumpf.Signal()
        ChannelDataMean.__init__(self, data=signal)

    @sumpf.Input(sumpf.Signal, "GetMean")
    def SetSignal(self, signal):
        """
        Sets the Signal for which the mean values shall be calculated.
        @param signal: the Signal instance for which the mean values shall be calculated
        """
        self._SetData(signal)



class SpectrumMean(ChannelDataMean):
    """
    Calculates the mean value for each channel of a Spectrum instance. The values
    are returned as a tuple of complex numbers.
    """
    def __init__(self, spectrum=None):
        """
        @param spectrum: the Spectrum instance for which the mean values shall be calculated
        """
        if spectrum is None:
            spectrum = sumpf.Spectrum()
        ChannelDataMean.__init__(self, data=spectrum)

    @sumpf.Input(sumpf.Spectrum, "GetMean")
    def SetSpectrum(self, spectrum):
        """
        Sets the Signal for which the mean values shall be calculated.
        @param spectrum: the Spectrum instance for which the mean values shall be calculated
        """
        self._SetData(spectrum)

