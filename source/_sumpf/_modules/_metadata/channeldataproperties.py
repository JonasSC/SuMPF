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


class ChannelDataProperties(object):
    """
    A class whose instances provide compatible format information for the two
    ChannelData subclasses "Signal" and "Spectrum". This helps to generate
    Signals whose Fourier transformation is compatible in length and resolution
    to a generated Spectrum. Of course the transformed Spectrum will also be
    compatible to the generated Signal.
    Compatibility means that the length and the sampling rate or resolution are
    equal. This is often required. For example for merging the data sets or
    for algebraic operations.
    """
    def __init__(self, signal_length=None, samplingrate=None, spectrum_length=None, resolution=None):
        """
        All parameters are optional.
        @param signal_length: the length for Signals (overrides spectrum_length if both are given)
        @param samplingrate: the sampling rate for Signals (overrides resolution if both are given)
        @param spectrum_length: the length for Spectrums
        @param resolution: the resolution for Spectrums
        """
        # set length and sampling rate to defaults
        try:
            self.__SetSignalLength(sumpf.config.get("default_signal_length"))
        except ValueError:
            self.__SetSignalLength(sumpf.config.get("default_signal_length") - 1)
        self.__SetSamplingRate(sumpf.config.get("default_samplingrate"))
        # set length and sampling rate according to constructor arguments
        if signal_length is not None:
            self.__SetSignalLength(signal_length)
            if spectrum_length not in [None, self.__length // 2 + 1]:
                raise ValueError("The given lengths for signals and spectrums contradict each other.")
        elif spectrum_length is not None:
            self.__SetSpectrumLength(spectrum_length)
        if samplingrate is not None:
            self.__SetSamplingRate(samplingrate)
            if resolution is not None:
                if round(self.__samplingrate / resolution) != self.__samplingrate / resolution:
                    raise ValueError("The given combination of sampling rate and frequency resolution does not result in an integer signal length")
                else:
                    if signal_length is not None or spectrum_length is not None:
                        if self.__length != int(self.__samplingrate / resolution):
                            raise ValueError("The given length(s) contradict the given sampling rate or frequency resolution.")
                    else:
                        self.__SetSignalLength(int(self.__samplingrate / resolution))
        elif resolution is not None:
            self.__SetResolution(resolution)

    @sumpf.Input(int, ["GetSignalLength", "GetSpectrumLength", "GetResolution"])
    def SetSignalLength(self, length):
        """
        Sets the length for Signals.
        Odd numbers are not allowed to avoid the loss of a sample when a Signal
        is transformed to the frequency domain.
        The sampling rate is assumed to be constant, so the resolution for
        Spectrums changes as well.
        @param length: the length for Signals
        """
        self.__SetSignalLength(length)

    @sumpf.Input(float, ["GetSamplingRate", "GetResolution"])
    def SetSamplingRate(self, samplingrate):
        """
        Sets the sampling rate for Signals.
        @param samplingrate: the sampling rate for Signals
        """
        self.__SetSamplingRate(samplingrate)

    @sumpf.Input(int, ["GetSignalLength", "GetSpectrumLength", "GetSamplingRate"])
    def SetSpectrumLength(self, length):
        """
        Sets the length for Spectrums.
        The resolution is assumed to be constant, so the sampling rate for
        Signals changes as well.
        @param length: the length for Spectrums
        """
        self.__SetSpectrumLength(length)

    @sumpf.Input(float, ["GetSamplingRate", "GetResolution"])
    def SetResolution(self, resolution):
        """
        Sets the resolution for Spectrums.
        @param resolution: the resolution for Spectrums
        """
        self.__SetResolution(resolution)

    @sumpf.Output(int, caching=False)
    def GetSignalLength(self):
        """
        Returns the length for Signals.
        @retval : the length for Signals
        """
        return self.__length

    @sumpf.Output(float, caching=False)
    def GetSamplingRate(self):
        """
        Returns the sampling rate for Signals.
        @retval : the sampling rate for Signals
        """
        return self.__samplingrate

    @sumpf.Output(int)
    def GetSpectrumLength(self):
        """
        Returns the length for Spectrums.
        @retval : the length for Spectrums
        """
        return self.__length // 2 + 1

    @sumpf.Output(float)
    def GetResolution(self):
        """
        Returns the resolution for Spectrums.
        @retval : the resolution for Spectrums as a float
        """
        return self.__samplingrate / self.__length

    def __SetSignalLength(self, length):
        """
        Private method for setting the length for Signals.
        Odd numbers are not allowed to avoid the loss of a sample when a Signal
        is transformed to the frequency domain.
        The sampling rate is assumed to be constant, so the resolution for
        Spectrums changes as well.
        @param length: the length for Signals as an integer
        """
        if length % 2 != 0:
            raise ValueError("The signal length has to be even, otherwise a sample will be lost in a fourier transform")
        self.__length = int(length)

    def __SetSamplingRate(self, samplingrate):
        """
        Private method for setting the sampling rate for Signals.
        @param samplingrate: the sampling rate for Signals as a number
        """
        self.__samplingrate = float(samplingrate)

    def __SetSpectrumLength(self, length):
        """
        Private method for setting the length for Spectrums.
        The resolution is assumed to be constant, so the sampling rate for
        Signals changes as well.
        @param length: the length for Spectrums as an integer
        """
        resolution = self.__samplingrate / self.__length    # here, self.__length is the old Signal length
        self.__length = int((length - 1) * 2)
        self.__samplingrate = resolution * self.__length    # here, self.__length is the newly calculated Signal length

    def __SetResolution(self, resolution):
        """
        Private method for setting the resolution for Spectrums.
        @param resolution: the resolution for Spectrums as a float
        """
        self.__samplingrate = round(resolution * self.__length, 7)  # The resolution is rounded to get "clean" sampling rates that work well with sound card interfaces

