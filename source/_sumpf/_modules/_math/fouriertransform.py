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

import numpy
import sumpf


class FourierTransform(object):
    """
    A class for fourier transformation of a Signal.
    The Signal is always treated as if it is causal, so the first sample is at time 0.
    Each channel of the input Signal will be transformed into a channel of the output Spectrum.
    """
    def __init__(self, signal=None):
        """
        @param signal: Optional parameter, the Signal that shall be transformed
        """
        if signal is None:
            signal = sumpf.Signal()
        self.__signal = signal

    @sumpf.Input(sumpf.Signal, "GetSpectrum")
    def SetSignal(self, signal):
        """
        @param signal: The input Signal that shall be transformed
        """
        self.__signal = signal

    @sumpf.Output(sumpf.Spectrum)
    def GetSpectrum(self):
        """
        @retval : The Spectrum resulting from the transformation
        """
        channels = []
        for c in self.__signal.GetChannels():
            channels.append(tuple(numpy.fft.rfft(c)))
        return sumpf.Spectrum(channels=channels,
                              resolution=self.__signal.GetSamplingRate() / len(self.__signal),
                              labels=self.__signal.GetLabels())



class InverseFourierTransform(object):
    """
    A class for the inverse fourier transformation of a Spectrum.
    The Spectrum is expected to be symmetric, so it only contains the positive
    frequencies.
    Each channel of the input Spectrum will be transformed into a channel of the output Signal.
    """
    def __init__(self, spectrum=None):
        """
        @param spectrum: Optional parameter, the Spectrum that shall be transformed
        """
        if spectrum is None:
            spectrum = sumpf.Spectrum()
        self.__spectrum = spectrum

    @sumpf.Input(sumpf.Spectrum, "GetSignal")
    def SetSpectrum(self, spectrum):
        """
        @param spectrum: The input Spectrum that shall be transformed
        """
        self.__spectrum = spectrum

    @sumpf.Output(sumpf.Signal)
    def GetSignal(self):
        """
        @retval : The Signal resulting from the inverse transformation
        """
        channels = []
        for c in self.__spectrum.GetChannels():
            channels.append(tuple(numpy.fft.irfft(c)))
        return sumpf.Signal(channels=channels,
                            samplingrate=2 * self.__spectrum.GetResolution() * (len(self.__spectrum) - 1),
                            labels=self.__spectrum.GetLabels())

