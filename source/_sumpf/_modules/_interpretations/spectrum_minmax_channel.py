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

import numpy
import sumpf


class SpectrumMinimumChannel(object):
    # flags for the data that shall be minimized
    MAGNITUDE = 0
    PHASE = 1
    CONTINUOUS_PHASE = 2
    GROUP_DELAY = 3
    REAL = 4
    IMAGINARY = 5

    def __init__(self, spectrum=None, data_set=MAGNITUDE):
        if spectrum is None:
            self.__spectrum = sumpf.Spectrum()
        else:
            self.__spectrum = spectrum
        self.__data_set = data_set

    @sumpf.Output(sumpf.Spectrum)
    def GetMinimum(self):
        if self.__data_set == SpectrumMinimumChannel.MAGNITUDE:
            indices = numpy.argmin(self.__spectrum.GetMagnitude(), axis=0)
        elif self.__data_set == SpectrumMinimumChannel.PHASE:
            indices = numpy.argmin(self.__spectrum.GetPhase(), axis=0)
        elif self.__data_set == SpectrumMinimumChannel.CONTINUOUS_PHASE:
            indices = numpy.argmin(self.__spectrum.GetContinuousPhase(), axis=0)
        elif self.__data_set == SpectrumMinimumChannel.GROUP_DELAY:
            indices = numpy.argmin(self.__spectrum.GetGroupDelay(), axis=0)
        elif self.__data_set == SpectrumMinimumChannel.REAL:
            indices = numpy.argmin(self.__spectrum.GetReal(), axis=0)
        elif self.__data_set == SpectrumMinimumChannel.IMAGINARY:
            indices = numpy.argmin(self.__spectrum.GetImaginary(), axis=0)
        return sumpf.Spectrum(channels=(tuple(z[indices[i]] for i, z in enumerate(zip(*self.__spectrum.GetChannels()))),),
                              resolution=self.__spectrum.GetResolution(),
                              labels=self.__spectrum.GetLabels())

    @sumpf.Input(sumpf.Spectrum, "GetMinimum")
    def SetSpectrum(self, spectrum):
        self.__spectrum = spectrum

    @sumpf.Input(int, "GetMinimum")
    def SetDataSet(self, data_set):
        self.__data_set = data_set


class SpectrumMaximumChannel(object):
    # flags for the data that shall be maximized
    MAGNITUDE = 0
    PHASE = 1
    CONTINUOUS_PHASE = 2
    GROUP_DELAY = 3
    REAL = 4
    IMAGINARY = 5

    def __init__(self, spectrum=None, data_set=MAGNITUDE):
        if spectrum is None:
            self.__spectrum = sumpf.Spectrum()
        else:
            self.__spectrum = spectrum
        self.__data_set = data_set

    @sumpf.Output(sumpf.Spectrum)
    def GetMaximum(self):
        if self.__data_set == SpectrumMaximumChannel.MAGNITUDE:
            indices = numpy.argmax(self.__spectrum.GetMagnitude(), axis=0)
        elif self.__data_set == SpectrumMaximumChannel.PHASE:
            indices = numpy.argmax(self.__spectrum.GetPhase(), axis=0)
        elif self.__data_set == SpectrumMaximumChannel.CONTINUOUS_PHASE:
            indices = numpy.argmax(self.__spectrum.GetContinuousPhase(), axis=0)
        elif self.__data_set == SpectrumMaximumChannel.GROUP_DELAY:
            indices = numpy.argmax(self.__spectrum.GetGroupDelay(), axis=0)
        elif self.__data_set == SpectrumMaximumChannel.REAL:
            indices = numpy.argmax(self.__spectrum.GetReal(), axis=0)
        elif self.__data_set == SpectrumMaximumChannel.IMAGINARY:
            indices = numpy.argmax(self.__spectrum.GetImaginary(), axis=0)
        return sumpf.Spectrum(channels=(tuple(z[indices[i]] for i, z in enumerate(zip(*self.__spectrum.GetChannels()))),),
                              resolution=self.__spectrum.GetResolution(),
                              labels=self.__spectrum.GetLabels())

    @sumpf.Input(sumpf.Spectrum, "GetMaximum")
    def SetSpectrum(self, spectrum):
        self.__spectrum = spectrum

    @sumpf.Input(int, "GetMaximum")
    def SetDataSet(self, data_set):
        self.__data_set = data_set

