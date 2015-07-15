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


class RegularizedSpectrumInversion(object):
    """
    This is a module that calculates the inverse of a spectrum so it can be used
    for deconvolution.
    The regularization becomes necessary, when the spectrum has a very low amplitude
    at certain frequencies. A deconvolution by dividing by this spectrum would
    amplify these frequencies massively, which leads to a very noisy impulse
    response whose plots are hard to interpret. Instead of dividing by the spectrum
    directly, it might be necessary, to multiply with the regularized inverse
    of this spectrum. The regularization tries to avoid the massive amplification
    of certain frequencies.

    This implementation is remotely similar to some ideas, that have been described
    by Ole Kirkeby and Angelo Farina. However I have not spent enough time yet,
    to work through their papers thoroughly, so this implementation is just a
    very rough estimation of the brilliant things, they thought of and it still
    might lack a lot of precision and scientific correctness. As soon as I think,
    that I've got an idea of what they are doing, I will improve this implementation.

    The following is an example to describe how this implementation is working:
    In this example, a transfer function is measured with a swept sine with a
    start frequency and a stop frequency. The transfer function shall be calculated
    by dividing the spectrum of the response signal by the spectrum of the swept
    sine.
     - S is the spectrum of the swept sine.
     - Y is the spectrum of the response signal.
     - G is the desired transfer function.
     - S* is the complex conjugate of the swept sine's spectrum.
    The quotient G = Y / S would show a massive amplification of the noise below
    the start frequency and above the stop frequency of the swept sine.
    Instead, this class calculates the quotient T = S* / (S* * S + E).
    The deconvolution can then be calculated by G = Y * T.
    E is zero for all frequencies between the start and the stop frequency. So
    the interesting frequencies are not affected by the regularization. Above
    and below that, it has a small, but non-zero value, so T does not become
    excessively large, when S becomes small. This way, the amplification of noise
    is greatly reduced. As long as S is large compared to E, the errors that are
    made by the regularization are minimal, even outside the interval of the start
    and stop frequencies.
    To avoid jumps in the calculated inverse, E fades between zero and the non-zero
    value with a hanning window.
    """
    def __init__(self, spectrum=None, start_frequency=20.0, stop_frequency=20000.0, transition_length=100, epsilon_max=0.1):
        """
        @param spectrum: the input Spectrum, that shall be inverted
        @param start_frequency: a float in Hz, that defines the low end of the interval that shall not be affected by the regularization
        @param stop_frequency: a float in Hz, that defines the top end of the interval that shall not be affected by the regularization
        @param transition_length: an integer number of samples that defines the length of the fade of E between zero and the non-zero value
        @param epsilon_max: the maximum value for E
        """
        if spectrum is None:
            self.__spectrum = sumpf.Spectrum(channels=((1.0, 1.0),))
        else:
            self.__spectrum = spectrum
        self.__start_frequency = start_frequency
        self.__stop_frequency = stop_frequency
        self.__transition_length = transition_length
        self.__epsilon_max = epsilon_max

    @sumpf.Output(sumpf.Spectrum)
    def GetOutput(self):
        """
        Calculates and returns the regularized inversion of the input Spectrum.
        @retval : a Spectrum instance
        """
        # generate epsilon-curve
        length = len(self.__spectrum)
        resolution = self.__spectrum.GetResolution()
        unaffected_start = int(round(self.__start_frequency / resolution))
        unaffected_end = int(round(self.__stop_frequency / resolution)) + 1
        window = tuple(numpy.hanning(2 * self.__transition_length + 2))[1:-1]
        epsilon_samples = [self.__epsilon_max] * (unaffected_start - self.__transition_length)
        for i in range(self.__transition_length, 2 * self.__transition_length):
            epsilon_samples.append(self.__epsilon_max * window[i])
        if len(epsilon_samples) > unaffected_start:
            epsilon_samples = epsilon_samples[len(epsilon_samples) - unaffected_start:]
        for i in range(unaffected_start, unaffected_end):
            epsilon_samples.append(0.0)
        for i in range(self.__transition_length):
            epsilon_samples.append(self.__epsilon_max * window[i])
        for i in range(unaffected_end + self.__transition_length, length):
            epsilon_samples.append(self.__epsilon_max)
        if len(epsilon_samples) > length:
            epsilon_samples = epsilon_samples[0:length]
        epsilon_spectrum = sumpf.Spectrum(channels=(tuple(epsilon_samples),) * len(self.__spectrum.GetChannels()), resolution=resolution)
        # calculate regularized inverse, relabel and return
        conjugated_spectrum = sumpf.modules.ConjugateSpectrum(spectrum=self.__spectrum).GetOutput()
        regularized_inversion = conjugated_spectrum / (conjugated_spectrum * self.__spectrum + epsilon_spectrum)
        return sumpf.Spectrum(channels=regularized_inversion.GetChannels(), resolution=regularized_inversion.GetResolution(), labels=self.__spectrum.GetLabels())

    @sumpf.Input(sumpf.Spectrum, "GetOutput")
    def SetSpectrum(self, spectrum):
        """
        Sets the input spectrum, that shall be inverted.
        @param spectrum: a Spectrum instance
        """
        self.__spectrum = spectrum

    @sumpf.Input(float, "GetOutput")
    def SetStartFrequency(self, frequency):
        """
        Sets the start frequency for the inversion.
        All frequencies between the start and the stop frequency are not affected
        by the regularization.
        @param frequency: a frequency value in Hz as a float
        """
        self.__start_frequency = frequency

    @sumpf.Input(float, "GetOutput")
    def SetStopFrequency(self, frequency):
        """
        Sets the stop frequency for the inversion.
        All frequencies between the start and the stop frequency are not affected
        by the regularization.
        @param frequency: a frequency value in Hz as a float
        """
        self.__stop_frequency = frequency

    @sumpf.Input(int, "GetOutput")
    def SetTransitionLength(self, length):
        """
        Sets the length of the fade between zero and the non-zero value in the
        regularization term (That's E in the example from the class description).
        @param length: an integer number of samples
        """
        self.__transition_length = length

    @sumpf.Input(float, "GetOutput")
    def SetEpsilonMax(self, epsilon_max):
        """
        Sets the maximum value of the regularization term (That's E in the example
        from the class description).
        epsilon_max is a linear floating point value, not a dB value.
        @param epsilon_max: a floating point value
        """
        self.__epsilon_max = epsilon_max

