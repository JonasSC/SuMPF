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


class SpectrumAlgebra(object):
    """
    A base class for calculations with two Spectrum instances.
    """
    def __init__(self, spectrum1=None, spectrum2=None):
        """
        All parameters are optional.
        @param spectrum1: the first Spectrum-instance for the calculation
        @param spectrum2: the second Spectrum-instance for the calculation
        """
        if spectrum1 is None:
            self.__spectrum1 = sumpf.Spectrum()
        else:
            self.__spectrum1 = spectrum1
        if spectrum2 is None:
            self.__spectrum2 = sumpf.Spectrum()
        else:
            self.__spectrum2 = spectrum2

    @sumpf.Input(sumpf.Spectrum, "GetOutput")
    def SetInput1(self, spectrum):
        """
        Sets the first Spectrum for the calculation.
        @param spectrum: the first Spectrum-instance for the calculation
        """
        self.__spectrum1 = spectrum

    @sumpf.Input(sumpf.Spectrum, "GetOutput")
    def SetInput2(self, spectrum):
        """
        Sets the second Spectrum for the calculation.
        @param spectrum: the second Spectrum-instance for the calculation
        """
        self.__spectrum2 = spectrum

    @sumpf.Output(sumpf.Spectrum)
    def GetOutput(self):
        """
        Calculates and returns the Spectrum resulting from the calculation.
        Before the calculation, the input Spectrums are checked for compatibility.
        If the Spectrums are incompatible and both not empty, a ValueError is raised.
        If the Spectrums are incompatible and one Spectrum is empty, an empty
        Spectrum is returned.
        @retval : a Spectrum whose channels are the result of the calculation
        """
        spectrum1 = self.__spectrum1
        spectrum2 = self.__spectrum2
        if spectrum1.GetResolution() != spectrum2.GetResolution():
            if spectrum1.IsEmpty() or spectrum2.IsEmpty():
                return sumpf.Spectrum()
            else:
                raise ValueError("The Spectrums do not have the same resolution (Spectrum1: %f, Spectrum2: %f)" % (spectrum1.GetResolution(), spectrum2.GetResolution()))
        elif len(spectrum1.GetChannels()) != len(spectrum2.GetChannels()):
            if spectrum1.IsEmpty() or spectrum2.IsEmpty():
                return sumpf.Spectrum(resolution=spectrum1.GetResolution())
            else:
                raise ValueError("The Spectrums do not have the same number of channels (Spectrum1: %i, Spectrum2: %i)" % (len(spectrum1.GetChannels()), len(spectrum2.GetChannels())))
        elif len(spectrum1) != len(spectrum2):
            if spectrum1.IsEmpty() or spectrum2.IsEmpty():
                return sumpf.Spectrum(channels=((0.0, 0.0),) * len(spectrum1.GetChannels()), resolution=spectrum1.GetResolution())
            else:
                raise ValueError("The Spectrums do not have the same length (Spectrum1: %i, Spectrum2: %i)" % (len(spectrum1), len(spectrum2)))
        else:
            return self._Calculate(spectrum1, spectrum2)

    def _Calculate(self, spectrum1, spectrum2):
        """
        Abstract method that shall be overwritten with the actual calculation.
        @param spectrum1: the first Spectrum for the calculation
        @param spectrum2: the second Spectrum for the calculation
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

