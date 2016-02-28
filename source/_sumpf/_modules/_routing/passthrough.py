# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2016 Jonas Schulte-Coerne
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


class PassThroughSignal(object):
    """
    A simple class, that just passes its input Signal to its output.
    This can be useful, if one Signal has to be distributed to multiple input
    connectors.
    """
    def __init__(self, signal=None):
        """
        @param signal: the input Signal instance
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal

    @sumpf.Output(sumpf.Signal, caching=False)
    def GetSignal(self):
        """
        Returns the given Signal.
        @retval : the given Signal
        """
        return self.__signal

    @sumpf.Input(sumpf.Signal, "GetSignal")
    def SetSignal(self, signal):
        """
        Sets the input Signal.
        @param signal: the input Signal instance
        """
        self.__signal = signal



class PassThroughSpectrum(object):
    """
    A simple class, that just passes its input Spectrum to its output.
    This can be useful, if one Spectrum has to be distributed to multiple input
    connectors.
    """
    def __init__(self, spectrum=None):
        """
        @param spectrum: the input Spectrum instance
        """
        if spectrum is None:
            self.__spectrum = sumpf.Spectrum()
        else:
            self.__spectrum = spectrum

    @sumpf.Output(sumpf.Spectrum, caching=False)
    def GetSpectrum(self):
        """
        Returns the given Spectrum.
        @retval : the given Spectrum
        """
        return self.__spectrum

    @sumpf.Input(sumpf.Spectrum, "GetSpectrum")
    def SetSpectrum(self, spectrum):
        """
        Sets the input Spectrum.
        @param signal: the input Spectrum instance
        """
        self.__spectrum = spectrum

