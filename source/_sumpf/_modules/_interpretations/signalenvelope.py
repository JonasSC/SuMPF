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

import numpy    # In this file, NumPy is only used for pi. But the SignalEnvelope
                # module relies on the fourier transform modules, which themselves
                # need NumPy. So importing this file shall raise an import error
                # when NumPy is not available, so that SignalEnvelope is not
                # available, when the fourier transform modules are not available
                # either.
import sumpf


class SignalEnvelope(object):
    """
    A module that calculates the envelope of a given Signal.
    Two modes are available:
     - UPPER calculates the envelope by half wave rectification and using the positive
       half wave. This results in the envelope above the given input Signal.
     - LOWER calculates the envelope by half wave rectification and using the negative
       half wave. This results in the envelope below the given input Signal.
    """
    UPPER = 1.0
    LOWER = -1.0

    def __init__(self, signal=None, mode=UPPER, frequency=50.0, order=32):
        """
        @param signal: the input Signal, of which the envelope shall be calculated
        @param mode: the mode for calculating the envelope, which can be either UPPER or LOWER
        @param frequency: the corner frequency of the demodulation lowpass filter
        @param order: the order of the demodulation lowpass filter
        """
        if signal is not None:
            self.__signal = signal
        else:
            self.__signal = sumpf.Signal()
        self.__mode = mode
        self.__frequency = frequency
        self.__order = order

    @sumpf.Input(sumpf.Signal, "GetEnvelope")
    def SetSignal(self, signal):
        """
        Sets the Signal, of which the envelope shall be calculated.
        @param signal: a Signal instance
        """
        self.__signal = signal

    @sumpf.Input(float, "GetEnvelope")
    def SetMode(self, mode):
        """
        Sets mode for the envelope calculation. See this classes documentation
        for further information.
        @param signal: either UPPER or LOWER it is recommended to use the flags instead of the integers. which they represent
        """
        if mode not in [SignalEnvelope.UPPER, SignalEnvelope.LOWER]:
            raise ValueError("The given mode is not recognized")
        self.__mode = mode

    @sumpf.Input(float, "GetEnvelope")
    def SetFrequency(self, frequency):
        """
        Sets the corner frequency of the lowpass filter that does the demodulation.
        @param frequency: a frequency in Hz as a float
        """
        self.__frequency = frequency

    @sumpf.Input(int, "GetEnvelope")
    def SetOrder(self, order):
        """
        Sets the order of the lowpass filter that does the demodulation.
        @param order: an integer
        """
        self.__order = order

    @sumpf.Output(sumpf.Signal)
    def GetEnvelope(self):
        """
        Calculates and returns the envelope of the input Signal.
        @retval : a Signal instance
        """
        # append a sample if necessary, so nothing is lost in the fourier transformations
        signal = self.__signal
        zeros_appended = False
        if len(self.__signal) % 2 != 0:
            channels = list(self.__signal.GetChannels())
            for i in range(len(channels)):
                channels[i] = channels[i] + (0.0,)
            signal = sumpf.Signal(channels=channels, samplingrate=self.__signal.GetSamplingRate())
            zeros_appended = True
        # remove a low frequency offset, so the envelope follows the Signal more tightly
        spectrum = sumpf.modules.FourierTransform(signal=signal).GetSpectrum()
        lowpass = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BESSEL(order=self.__order), frequency=self.__frequency / 2.0, transform=False, resolution=spectrum.GetResolution(), length=len(spectrum)).GetSpectrum()
        time_shift = sumpf.modules.DelayFilterGenerator(delay=-1.0 / (numpy.pi * self.__frequency), resolution=spectrum.GetResolution(), length=len(spectrum)).GetSpectrum()
        copied = sumpf.modules.CopySpectrumChannels(input=lowpass * time_shift, channelcount=len(spectrum.GetChannels())).GetOutput()
        filtered_spectrum = spectrum * copied
        offset_signal = sumpf.modules.InverseFourierTransform(spectrum=filtered_spectrum).GetSignal()
        if offset_signal.GetSamplingRate() != self.__signal.GetSamplingRate():
            offset_signal = sumpf.Signal(channels=offset_signal.GetChannels(), samplingrate=self.__signal.GetSamplingRate())
        flat_signal = signal - offset_signal
        # calculate the envelope
        rectified = sumpf.modules.RectifySignal(signal=flat_signal).GetOutput()
        sign = self.__mode
        half_wave = flat_signal + sign * rectified
        unscaled_envelope = self.__CalculateUnscaledEnvelope(rectified_signal=half_wave)
        scaling_factors = self.__GetScalingFactors(original=half_wave, envelope=unscaled_envelope, sign=sign)
        envelope = sumpf.modules.AmplifySignal(input=unscaled_envelope, factor=scaling_factors).GetOutput()
        # add the low frequency offset back to the Signal
        result = envelope + offset_signal
        # delete the last sample if one has been appended before
        if zeros_appended:
            result = result[0:-1]
        # apply the original channel labels and return the envelope
        return sumpf.modules.CopyLabelsToSignal(data_input=result, label_input=self.__signal).GetOutput()

    def __CalculateUnscaledEnvelope(self, rectified_signal):
        """
        This private method does the low pass filtering for the calculation of
        the envelope
        """
        spectrum = sumpf.modules.FourierTransform(signal=rectified_signal).GetSpectrum()
        lowpass = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BESSEL(order=self.__order), frequency=self.__frequency, transform=False, resolution=spectrum.GetResolution(), length=len(spectrum)).GetSpectrum()
        time_shift = sumpf.modules.DelayFilterGenerator(delay=-1.0 / (2.0 * numpy.pi * self.__frequency), resolution=spectrum.GetResolution(), length=len(spectrum)).GetSpectrum()
        copied = sumpf.modules.CopySpectrumChannels(input=lowpass * time_shift, channelcount=len(spectrum.GetChannels())).GetOutput()
        filtered_spectrum = spectrum * copied
        unscaled_envelope = sumpf.modules.InverseFourierTransform(spectrum=filtered_spectrum).GetSignal()
        if unscaled_envelope.GetSamplingRate() != self.__signal.GetSamplingRate():
            unscaled_envelope = sumpf.Signal(channels=unscaled_envelope.GetChannels(), samplingrate=self.__signal.GetSamplingRate())
        return unscaled_envelope

    def __GetScalingFactors(self, original, envelope, sign):
        """
        Calculates the scaling factors by which the calculated envelope has to
        be amplified.
        """
        margin = int(0.25 * len(original))
        scaling_factors = []
        for c in range(len(original.GetChannels())):
            factor = 0.0
            for s in range(margin, len(original) - margin):
                if envelope.GetChannels()[c][s] * factor * sign < sign * original.GetChannels()[c][s]:
                    factor = original.GetChannels()[c][s] / envelope.GetChannels()[c][s]
            scaling_factors.append(factor / 2.0)
        return scaling_factors

