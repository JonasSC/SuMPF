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


class RudinShapiroNoiseGenerator(object):
    """
    A class for generating a white pseudo noise with a low crest factor.
    The noise is generated in the frequency domain by defining the sign (phase)
    of the respective samples according to a Rudin-Shapiro sequence. This procedure
    is well described in the paper "Multitone Signals with Low Crest Factor" by
    Stephen Boyd (IEEE Transactions on circuits and systems, october 1986).
    If the length of the Rudin-Shapiro sequence is a power of two, the crest factor
    of the generated pseudo noise is near its theoretical minimum of 6dB.
    """
    def __init__(self, start_frequency=0.0, stop_frequency=None, samplingrate=None, length=None):
        """
        @param start_frequency: a float for the start frequency in Hz, below which the noise signal shall have no energy
        @param stop_frequency: None or a float for the stop frequency in Hz, above which the noise signal shall have no energy
        @param samplingrate: a float for the sampling rate in Hz
        @param length: the integer number of samples of the noise signal
        """
        self.__start_frequency = start_frequency
        self.__stop_frequency = stop_frequency
        if samplingrate is None:
            self.__samplingrate = sumpf.config.get("default_samplingrate")
        else:
            self.__samplingrate = samplingrate
        if length is None:
            self.__length = sumpf.config.get("default_signal_length")
        else:
            self.__length = length

    @sumpf.Output(sumpf.Signal)
    def GetSignal(self):
        """
        Computes the noise signal and returns it.
        @retval : a Signal instance
        """
        spectrum_length, start_index, sequence_length = self.__GetRudinShapiroSequenceParameters()
        # generate the spectrum
        f_samples = numpy.empty(spectrum_length)
        f_samples[0:start_index] = 0.0
        if start_index < spectrum_length and 0 < sequence_length:
            f_samples[start_index] = 1.0
            if start_index + 1 < spectrum_length and 1 < sequence_length:
                f_samples[start_index + 1] = 1.0
                i = 2
                while i < sequence_length:
                    j = min(i // 2, sequence_length - i)
                    f_samples[start_index + i:start_index + i + j] = f_samples[start_index:start_index + j]
                    if i + i // 2 < sequence_length:
                        j = min(i, sequence_length - i)
                        f_samples[start_index + i + i // 2:start_index + i + j] = -f_samples[start_index + i // 2:start_index + j]
                    i *= 2
        f_samples[start_index + sequence_length:] = 0.0
        # transform the spectrum to the time_domain
        t_samples = numpy.fft.irfft(f_samples)
        if len(t_samples) == self.__length:
            return sumpf.Signal(channels=(tuple(t_samples),), samplingrate=self.__samplingrate, labels=("Noise",))
        else:
            return sumpf.Signal(channels=(tuple(t_samples) + (0.0,),), samplingrate=self.__samplingrate, labels=("Noise",))

    @sumpf.Output(int)
    def GetRudinShapiroSequenceLength(self):
        """
        Returns the length of the Rudin-Shapiro sequence, that is taken to define
        the phase of the noise spectrum. If this length is a power of two, the
        crest factor of the resulting noise is near its theoretical minimum of 6dB.
        @retval : the length of the Rudin-Shapiro sequence as an integer.
        """
        return self.__GetRudinShapiroSequenceParameters()[2]

    @sumpf.Input(float, ("GetSignal", "GetRudinShapiroSequenceLength"))
    def SetStartFrequency(self, frequency):
        """
        Sets the start frequency below which the noise signal shall have no energy.
        @param frequency: the start frequency as a float in Hz
        """
        self.__start_frequency = frequency

    @sumpf.Input((float, type(None)), ("GetSignal", "GetRudinShapiroSequenceLength"))
    def SetStopFrequency(self, frequency):
        """
        Sets the stop frequency above which the noise signal shall have no energy.
        Setting the frequency to None causes the stop frequency to be the Nyquist
        frequency of the signal.
        @param frequency: the stop frequency as a float in Hz or None
        """
        self.__stop_frequency = frequency

    @sumpf.Input(float, ("GetSignal", "GetRudinShapiroSequenceLength"))
    def SetSamplingRate(self, samplingrate):
        """
        Sets the sampling rate of the output Signal.
        @param samplingrate: the sampling rate in Hz
        """
        self.__samplingrate = float(samplingrate)

    @sumpf.Input(int, ("GetSignal", "GetRudinShapiroSequenceLength"))
    def SetLength(self, length):
        """
        Sets the length of the output Signal.
        @param length: the number of samples of the signal
        """
        self.__length = int(length)

    def __GetRudinShapiroSequenceParameters(self):
        """
        Computes the necessary parameters for generating the spectrum of the noise.
        @retval : a tuple with the length of the spectrum, the start index of the Rudin-Shapiro sequence and its length
        """
        if self.__length % 2 == 0:
            properties = sumpf.modules.ChannelDataProperties(signal_length=self.__length, samplingrate=self.__samplingrate)
        else:
            properties = sumpf.modules.ChannelDataProperties(signal_length=self.__length - 1, samplingrate=self.__samplingrate)
        resolution = properties.GetResolution()
        spectrum_length = properties.GetSpectrumLength()
        start_index = int(round(self.__start_frequency / resolution))
        if self.__stop_frequency is None:
            stop_index = spectrum_length
        else:
            stop_index = int(round(self.__stop_frequency / resolution)) + 1
        length = min(stop_index - start_index, spectrum_length)
        return spectrum_length, start_index, length

