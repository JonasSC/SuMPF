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
try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy



class SignalMinimum(object):
    """
    A class for finding the minimum value(s) of a Signal. It is possible to
    retrieve the minima for each channel individually or to find the one global
    minimum.
    """
    def __init__(self, signal=None):
        """
        @param signal: the Signal, in which shall be looked for the minimum value(s)
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal

    @sumpf.Output(tuple)
    def GetMinima(self):
        """
        Returns the minimum values for each channel individually as a tuple.
        @retval : a tuple of floats
        """
        return tuple(min(c) for c in self.__signal.GetChannels())

    @sumpf.Output(float)
    def GetGlobalMinimum(self):
        """
        Returns the minimum sample of the whole signal.
        @retval : a float
        """
        return numpy.min(self.__signal.GetChannels())

    @sumpf.Input(sumpf.Signal, ("GetMinima", "GetGlobalMinimum"))
    def SetSignal(self, signal):
        """
        Sets the Signal, in which shall be looked for the minimum value(s).
        @param signal: a Signal instance
        """
        self.__signal = signal



class SignalMaximum(object):
    """
    A class for finding the maximum value(s) of a Signal. It is possible to
    retrieve the maxima for each channel individually or to find the one global
    maximum.
    """
    def __init__(self, signal=None):
        """
        @param signal: the Signal, in which shall be looked for the maximum value(s)
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal

    @sumpf.Output(tuple)
    def GetMaxima(self):
        """
        Returns the maximum values for each channel individually as a tuple.
        @retval : a tuple of floats
        """
        return tuple(max(c) for c in self.__signal.GetChannels())

    @sumpf.Output(float)
    def GetGlobalMaximum(self):
        """
        Returns the maximum sample of the whole signal.
        @retval : a float
        """
        return numpy.max(self.__signal.GetChannels())

    @sumpf.Input(sumpf.Signal, ("GetMaxima", "GetGlobalMaximum"))
    def SetSignal(self, signal):
        """
        Sets the Signal, in which shall be looked for the maximum value(s).
        @param signal: a Signal instance
        """
        self.__signal = signal



class SpectrumMinimum(object):
    """
    A class for finding the minimum value(s) of a real valued data set, that is
    of derived from a Spectrum. The data set can be the spectrum's magnitude, its
    phase, continuous phase or group delay or it can be the real or imaginary part
    of the spectrum.
    It is possible to retrieve the minima for each channel individually or to find
    the one global minimum.
    """
    # flags for the data that shall be minimized
    MAGNITUDE = 0
    PHASE = 1
    CONTINUOUS_PHASE = 2
    GROUP_DELAY = 3
    REAL = 4
    IMAGINARY = 5

    def __init__(self, spectrum=None, data_set=MAGNITUDE):
        """
        @param spectrum: the Spectrum, in which shall be looked for the minimum value(s)
        @param data_set: a flag, which data from the complex valued Spectrum shall be minimized
        """
        if spectrum is None:
            self.__spectrum = sumpf.Spectrum()
        else:
            self.__spectrum = spectrum
        self.__data_set = data_set

    @sumpf.Output(tuple)
    def GetMinima(self):
        """
        Returns the minimum values for each channel individually as a tuple.
        @retval : a tuple of floats
        """
        if self.__data_set == SpectrumMinimum.MAGNITUDE:
            data = self.__spectrum.GetMagnitude()
        elif self.__data_set == SpectrumMinimum.PHASE:
            data = self.__spectrum.GetPhase()
        elif self.__data_set == SpectrumMinimum.CONTINUOUS_PHASE:
            data = self.__spectrum.GetContinuousPhase()
        elif self.__data_set == SpectrumMinimum.GROUP_DELAY:
            data = self.__spectrum.GetGroupDelay()
        elif self.__data_set == SpectrumMinimum.REAL:
            data = self.__spectrum.GetReal()
        elif self.__data_set == SpectrumMinimum.IMAGINARY:
            data = self.__spectrum.GetImaginary()
        return tuple(min(c) for c in data)

    @sumpf.Output(float)
    def GetGlobalMinimum(self):
        """
        Returns the minimum sample of the whole signal.
        @retval : a float
        """
        if self.__data_set == SpectrumMinimum.MAGNITUDE:
            data = self.__spectrum.GetMagnitude()
        elif self.__data_set == SpectrumMinimum.PHASE:
            data = self.__spectrum.GetPhase()
        elif self.__data_set == SpectrumMinimum.CONTINUOUS_PHASE:
            data = self.__spectrum.GetContinuousPhase()
        elif self.__data_set == SpectrumMinimum.GROUP_DELAY:
            data = self.__spectrum.GetGroupDelay()
        elif self.__data_set == SpectrumMinimum.REAL:
            data = self.__spectrum.GetReal()
        elif self.__data_set == SpectrumMinimum.IMAGINARY:
            data = self.__spectrum.GetImaginary()
        return numpy.min(data)

    @sumpf.Input(sumpf.Spectrum, ("GetMinima", "GetGlobalMinimum"))
    def SetSpectrum(self, spectrum):
        """
        Sets the Spectrum, in which shall be looked for the minimum value(s).
        @param spectrum: a Signal instance
        """
        self.__spectrum = spectrum

    @sumpf.Input(int, ("GetMinima", "GetGlobalMinimum"))
    def SetDataSet(self, data_set):
        """
        Selects, which data from the complex valued Spectrum shall be minimized.
        @param data_set: one of the flags, that are specified in this class (e.g. MAGNITUDE)
        """
        self.__data_set = data_set



class SpectrumMaximum(object):
    """
    A class for finding the maximum value(s) of a real valued data set, that is
    of derived from a Spectrum. The data set can be the spectrum's magnitude, its
    phase, continuous phase or group delay or it can be the real or imaginary part
    of the spectrum.
    It is possible to retrieve the maxima for each channel individually or to find
    the one global maximum.
    """
    # flags for the data that shall be maximized
    MAGNITUDE = 0
    PHASE = 1
    CONTINUOUS_PHASE = 2
    GROUP_DELAY = 3
    REAL = 4
    IMAGINARY = 5

    def __init__(self, spectrum=None, data_set=MAGNITUDE):
        """
        @param spectrum: the Spectrum, in which shall be looked for the maximum value(s)
        @param data_set: a flag, which data from the complex valued Spectrum shall be maximized
        """
        if spectrum is None:
            self.__spectrum = sumpf.Spectrum()
        else:
            self.__spectrum = spectrum
        self.__data_set = data_set

    @sumpf.Output(tuple)
    def GetMaxima(self):
        """
        Returns the maximum values for each channel individually as a tuple.
        @retval : a tuple of floats
        """
        if self.__data_set == SpectrumMinimum.MAGNITUDE:
            data = self.__spectrum.GetMagnitude()
        elif self.__data_set == SpectrumMinimum.PHASE:
            data = self.__spectrum.GetPhase()
        elif self.__data_set == SpectrumMinimum.CONTINUOUS_PHASE:
            data = self.__spectrum.GetContinuousPhase()
        elif self.__data_set == SpectrumMinimum.GROUP_DELAY:
            data = self.__spectrum.GetGroupDelay()
        elif self.__data_set == SpectrumMinimum.REAL:
            data = self.__spectrum.GetReal()
        elif self.__data_set == SpectrumMinimum.IMAGINARY:
            data = self.__spectrum.GetImaginary()
        return tuple(max(c) for c in data)

    @sumpf.Output(float)
    def GetGlobalMaximum(self):
        """
        Returns the maximum sample of the whole signal.
        @retval : a float
        """
        if self.__data_set == SpectrumMinimum.MAGNITUDE:
            data = self.__spectrum.GetMagnitude()
        elif self.__data_set == SpectrumMinimum.PHASE:
            data = self.__spectrum.GetPhase()
        elif self.__data_set == SpectrumMinimum.CONTINUOUS_PHASE:
            data = self.__spectrum.GetContinuousPhase()
        elif self.__data_set == SpectrumMinimum.GROUP_DELAY:
            data = self.__spectrum.GetGroupDelay()
        elif self.__data_set == SpectrumMinimum.REAL:
            data = self.__spectrum.GetReal()
        elif self.__data_set == SpectrumMinimum.IMAGINARY:
            data = self.__spectrum.GetImaginary()
        return numpy.max(data)

    @sumpf.Input(sumpf.Spectrum, ("GetMaxima", "GetGlobalMaximum"))
    def SetSpectrum(self, spectrum):
        """
        Sets the Spectrum, in which shall be looked for the maximum value(s).
        @param spectrum: a Signal instance
        """
        self.__spectrum = spectrum

    @sumpf.Input(int, ("GetMaxima", "GetGlobalMaximum"))
    def SetDataSet(self, data_set):
        """
        Selects, which data from the complex valued Spectrum shall be maximized.
        @param data_set: one of the flags, that are specified in this class (e.g. MAGNITUDE)
        """
        self.__data_set = data_set

