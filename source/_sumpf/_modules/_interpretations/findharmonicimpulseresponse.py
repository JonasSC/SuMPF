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

import math
import sumpf
import numpy    # the FindHarmonicImpulseResponse class needs NumPy for the fourier transforms, so importing this file shall fail, when NumPy is not available


class FindHarmonicImpulseResponse(object):
    """
    Calculates the impulse response of a harmonic from a given impulse response.

    To make this possible, the given full impulse response must have been measured
    with a sweep whose frequency increases exponentially over time. This makes
    the time difference between the excitation of a certain frequency by nonlinear
    distortion and its later excitation by the sweep independent of the frequency,
    so that the impulse responses of the harmonics occur as peaks in the non causal
    part of the at the full impulse response. If the deconvolution is done by
    division in the frequency domain, these non causal artifacts are "wrapped around"
    to the end of the impulse response.

    The peaks, that have been cut out of the full impulse response, are time stretched
    to become the impulse response of the harmonic. This becomes clear, when considering
    that the spectrum of the unscaled impulse response of the n-th harmonic would
    be a transfer function in dependency of n times the frequency. Therefore, the
    resulting impulse response has a sampling rate, that is n times smaller than
    that of the original impulse response and may have to be resampled.

    To locate the impulse responses of the harmonics, the sweep rate of the excitation
    signal has to be known. This rate can be calculated by the sweep's start frequency,
    its stop frequency and the time it took to sweep between the two.
    """
    def __init__(self,
                 impulse_response=None,
                 harmonic_order=2,
                 sweep_start_frequency=20.0,
                 sweep_stop_frequency=20000.0,
                 sweep_duration=None):
        """
        @param impulse_response: the impulse response Signal, from which the impulse responses of the harmonics shall be cut out
        @param harmonic_order: the integer order of the harmonic, whose impulse response shall be determined
        @param sweep_start_frequency: the start frequency of the exponential sweep, that has been used to measure the given impulse response
        @param sweep_stop_frequency: the stop frequency of the exponential sweep, that has been used to measure the given impulse response
        @param sweep_duration: the time in seconds that it took the sweep to go from the start frequency to the stop frequency
        """
        if harmonic_order < 2:
            raise ValueError("The harmonic order has to be at least 2.")
        self.__impulse_response = impulse_response
        if impulse_response is None:
            self.__impulse_response = sumpf.modules.ImpulseGenerator().GetSignal()
        self.__harmonic_order = harmonic_order
        self.__sweep_start_frequency = sweep_start_frequency
        self.__sweep_stop_frequency = sweep_stop_frequency
        self.__sweep_duration = sweep_duration

    @sumpf.Input(sumpf.Signal, "GetHarmonicImpulseResponse")
    def SetImpulseResponse(self, impulse_response):
        """
        Sets the impulse response from which the impulse response of the harmonic
        shall be cut out.
        @param impulse_response: a Signal instance
        """
        self.__impulse_response = impulse_response

    @sumpf.Input(int, "GetHarmonicImpulseResponse")
    def SetHarmonicOrder(self, order):
        """
        Sets the order of the harmonic, whose impulse response shall be determined.
        The given order has to be at least two. To separate the impulse response
        of the fundamental from the measured nonlinearities, use the CutSignal
        and the WindowGenerator classes.
        @param order: the order as an integer (at least 2)
        """
        if order < 2:
            raise ValueError("The harmonic order has to be at least 2.")
        self.__harmonic_order = order

    @sumpf.Input(float, "GetHarmonicImpulseResponse")
    def SetSweepStartFrequency(self, frequency):
        """
        Sets the start frequency of the sweep, with which the given impulse response
        has been recorded and calculated.
        @param frequency: the frequency in Hertz as a float
        """
        self.__sweep_start_frequency = frequency

    @sumpf.Input(float, "GetHarmonicImpulseResponse")
    def SetSweepStopFrequency(self, frequency):
        """
        Sets the stop frequency of the sweep, with which the given impulse response
        has been recorded and calculated.
        @param frequency: the frequency in Hertz as a float
        """
        self.__sweep_stop_frequency = frequency

    @sumpf.Input(float, "GetHarmonicImpulseResponse")
    def SetSweepDuration(self, duration):
        """
        Sets the time that it took the sweep to go from its start frequency to
        its stop frequency.
        If the duration is set to None, it is assumed, that the sweep duration
        is the same as the duration of the given impulse response.
        @param frequency: the time in seconds as a float or None
        """
        self.__sweep_duration = duration

    @sumpf.Output(sumpf.Signal)
    def GetHarmonicImpulseResponse(self):
        """
        Cuts the impulse response of the harmonic out of the given full impulse
        response and scales to the correct length.
        Note that the returned impulse response is shorter than the full impulse
        response and might have to be extended with zeros.
        @retval : the harmonic impulse response as a Signal
        """
        # get the sample indices between the impulse response can be found
        sweep_duration = self.__sweep_duration
        if sweep_duration is None:
            sweep_duration = self.__impulse_response.GetDuration()
        sweep_rate = (self.__sweep_stop_frequency / self.__sweep_start_frequency) ** (1.0 / sweep_duration)
        harmonic_start_time = self.__impulse_response.GetDuration() - math.log(self.__harmonic_order, sweep_rate)
        harmonic_start_sample = sumpf.modules.DurationToLength(duration=harmonic_start_time, samplingrate=self.__impulse_response.GetSamplingRate(), even_length=False).GetLength()
        harmonic_stop_sample = len(self.__impulse_response)
        if self.__harmonic_order > 2:
            harmonic_stop_time = self.__impulse_response.GetDuration() - math.log(self.__harmonic_order - 1, sweep_rate)
            harmonic_stop_sample = sumpf.modules.DurationToLength(duration=harmonic_stop_time, samplingrate=self.__impulse_response.GetSamplingRate(), even_length=False).GetLength()
        # prepare the labels
        labels = []
        affix = " (%s harmonic)" % sumpf.helper.counting_number(self.__harmonic_order)
        for l in self.__impulse_response.GetLabels():
            if l is None:
                labels.append("Impulse Response" + affix)
            else:
                labels.append(l + affix)
        # crop to the impulse response of the wanted harmonic
        cropped = self.__impulse_response[harmonic_start_sample:harmonic_stop_sample]
        harmonic = sumpf.Signal(channels=cropped.GetChannels(), samplingrate=cropped.GetSamplingRate() / self.__harmonic_order, labels=tuple(labels))
        if len(harmonic) % 2 != 0:
            harmonic = sumpf.Signal(channels=tuple([c + (0.0,) for c in harmonic.GetChannels()]), samplingrate=harmonic.GetSamplingRate(), labels=harmonic.GetLabels())
        return harmonic

