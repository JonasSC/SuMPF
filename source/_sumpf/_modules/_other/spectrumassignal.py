# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2018 Jonas Schulte-Coerne
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


class SpectrumAsSignal(object):
    """
    Copies a Spectrum's channels to a Signal, so that processing steps for Signals
    such as cutting can be applied to the spectrum.
    """
    # flags for the data that shall be copied from the Spectrum
    MAGNITUDE = 0
    PHASE = 1
    CONTINUOUS_PHASE = 2
    GROUP_DELAY = 3
    REAL = 4
    IMAGINARY = 5

    def __init__(self, spectrum=None, data_set=MAGNITUDE):
        """
        @param spectrum: the Spectrum, that shall be converted
        @param data_set: a flag, which data from the complex valued Spectrum shall be copied to the real valued Signal
        """
        if spectrum is None:
            self.__spectrum = sumpf.Spectrum()
        else:
            self.__spectrum = spectrum
        self.__data_set = data_set

    @sumpf.Output(sumpf.Signal)
    def GetSignal(self):
        """
        Returns the generated Signal.
        The Signal's sampling rate is the inverted resolution of the input Spectrum.
        @retval : a Signal instance
        """
        if self.__data_set == SpectrumAsSignal.MAGNITUDE:
            return sumpf.Signal(channels=self.__spectrum.GetMagnitude(), samplingrate=1.0 / self.__spectrum.GetResolution(), labels=self.__spectrum.GetLabels())
        elif self.__data_set == SpectrumAsSignal.PHASE:
            return sumpf.Signal(channels=self.__spectrum.GetPhase(), samplingrate=1.0 / self.__spectrum.GetResolution(), labels=self.__spectrum.GetLabels())
        elif self.__data_set == SpectrumAsSignal.CONTINUOUS_PHASE:
            return sumpf.Signal(channels=self.__spectrum.GetContinuousPhase(), samplingrate=1.0 / self.__spectrum.GetResolution(), labels=self.__spectrum.GetLabels())
        elif self.__data_set == SpectrumAsSignal.GROUP_DELAY:
            return sumpf.Signal(channels=self.__spectrum.GetGroupDelay(), samplingrate=1.0 / self.__spectrum.GetResolution(), labels=self.__spectrum.GetLabels())
        elif self.__data_set == SpectrumAsSignal.REAL:
            return sumpf.Signal(channels=self.__spectrum.GetReal(), samplingrate=1.0 / self.__spectrum.GetResolution(), labels=self.__spectrum.GetLabels())
        elif self.__data_set == SpectrumAsSignal.IMAGINARY:
            return sumpf.Signal(channels=self.__spectrum.GetImaginary(), samplingrate=1.0 / self.__spectrum.GetResolution(), labels=self.__spectrum.GetLabels())
        else:
            raise ValueError("Unknown data set from a spectrum: %s" % self.__data_set)

    @sumpf.Input(sumpf.Spectrum, "GetSignal")
    def SetSpectrum(self, spectrum):
        """
        Sets the spectrum, that shall be converted.
        @param spectrum: a Spectrum instance
        """
        self.__spectrum = spectrum

    @sumpf.Input(int, "GetSignal")
    def SetDataSet(self, data_set):
        """
        Selects, which data from the complex valued Spectrum shall be copied to
        the real valued Signal.
        @param data_set: one of the flags, that are specified in this class (e.g. MAGNITUDE)
        """
        self.__data_set = data_set

