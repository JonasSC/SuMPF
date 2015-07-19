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


class CorrelateSignals(object):
    """
    A module for calculating the cross correlation of two Signals.
    If both input Signals are the same, an auto correlation will be calculated.

    This module is a wrapper for numpy.correlate, but in SuMPF the default
    mode is FULL, rather than "valid" like in NumPy.
    Also, the default behavior of this module is to circularly shift the output
    sequence of numpy.correlate, so that the zero-time sample is the first sample
    of the output Signal and the non-causal part of the correlation is at the end
    of the Signal.
    Set the "shift" parameter to True, if the correlation shall be returned in NumPy's
    fashion, where the non-causal part is at the beginning of the output Signal
    and the zero-time sample comes after that.

    Furthermore, this class offers the correlation mode SPECTRUM, which calculates
    the correlation in the frequency domain.

    The input Signals must have the same sampling rate and channel count. If the
    correlation mode SPECTRUM is used, the signals must also have the same length.
    """

    FULL = "full"
    SAME = "same"
    VALID = "valid"
    SPECTRUM = "spectrum"

    def __init__(self, signal1=None, signal2=None, mode=None, shift=False):
        """
        @param signal1: the first Signal-instance for calculating the cross correlation
        @param signal2: the second Signal-instance for calculating the cross correlation
        @param mode: either None or one of the available correlation modes (See SetCorrelationMode for details)
        @param shift: True, if the output Signal shall be shifted so that the non-causal part of the correlation is at the beginning and the zero-time sample is in the middle; False if the zero-time sample shall be the first sample
        """
        if signal1 is None:
            signal1 = sumpf.Signal()
        if signal2 is None:
            signal2 = sumpf.Signal()
        if mode is None:
            mode = CorrelateSignals.FULL
        self.__signal1 = signal1
        self.__signal2 = signal2
        self.__SetCorrelationMode(mode)
        self.__shift = shift

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput1(self, signal):
        """
        Sets the first Signal for calculating the cross correlation.
        If this Signal is the same as the second signal, an auto correlation will
        be calculated.
        @param signal: the first Signal instance for the correlation
        """
        self.__signal1 = signal

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput2(self, signal):
        """
        Sets the second Signal for calculating the cross correlation.
        If this Signal is the same as the first signal, an auto correlation will
        be calculated.
        @param signal: the second Signal instance for the correlation
        """
        self.__signal2 = signal

    @sumpf.Input(type(FULL), "GetOutput")
    def SetCorrelationMode(self, mode):
        """
        Sets the correlation mode.
        The mode can be one of the following:
          - CorrelateSignals.FULL
              for full length correlation. If M and N are the lengths of the
              input signals, the output's length will be M+N-1.
          - CorrelateSignals.SAME
              for an output with the same length as the longer input.
              (output_length=max(M,N))
          - CorrelateSignals.VALID
              for an output length of max(M,N)-min(M,N)+1
          - CorrelateSignals.SPECTRUM
              to do the correlation in the frequency domain. This will be a circular
              correlation which requires both input signals to have the same length.
              This will also be the length of the output signal.
        See help(numpy.convolve) for more details.
        @param mode: one of the modes from the description
        """
        self.__SetCorrelationMode(mode)

    @sumpf.Input(bool, "GetOutput")
    def SetShift(self, shift):
        """
        Sets if the output Signal shall be shifted so that the non-causal part
        of the correlation is at the beginning and the zero-time sample comes after
        that (this is NumPy's default behavior).
        Set shift to True, to apply the shift, set it to False, if the zero-time
        sample shall be the first sample of the output Signal.
        @param shift: a boolean
        """
        self.__shift = shift

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Calculates and returns the cross correlation Signal.
        The resulting Signal will have as many channels as the input Signal with
        the least channels.
        @retval : a Signal whose channels are the result of the cross correlation
        """
        label = "Cross Correlation "
        if self.__signal1 == self.__signal2:
            label = "Auto Correlation "
        if self.__signal1.GetSamplingRate() != self.__signal2.GetSamplingRate():
            raise ValueError("The given signals have a different sampling rate")
        elif len(self.__signal1.GetChannels()) != len(self.__signal2.GetChannels()):
            raise ValueError("The two Signals have a different number of channels")
        elif self.__mode == CorrelateSignals.SPECTRUM:
            spectrum1 = sumpf.modules.FourierTransform(signal=self.__signal1).GetSpectrum()
            reverse2 = sumpf.modules.ReverseSignal(signal=self.__signal2).GetOutput()
            spectrum2 = sumpf.modules.FourierTransform(signal=reverse2).GetSpectrum()
            output_spectrum = spectrum1 * spectrum2
            output_signal = sumpf.modules.InverseFourierTransform(spectrum=output_spectrum).GetSignal()
            result = sumpf.modules.RelabelSignal(input=output_signal, labels=tuple([label + str(c + 1) for c in range(len(self.__signal1.GetChannels()))])).GetOutput()
            if self.__shift:
                shift = len(self.__signal2) // 2 + 1
                result = sumpf.modules.ShiftSignal(signal=result, shift=shift, circular=True).GetOutput()
            else:
                result = sumpf.modules.ShiftSignal(signal=result, shift=1, circular=True).GetOutput()
            return result
        else:
            channels = []
            labels = []
            for c in range(len(self.__signal1.GetChannels())):
                channel = tuple(numpy.correlate(self.__signal1.GetChannels()[c], self.__signal2.GetChannels()[c], mode=self.__mode))
                if len(channel) == 1:
                    channel += (0.0,)
                channels.append(channel)
                labels.append(label + str(c + 1))
            result = sumpf.Signal(channels=channels, samplingrate=self.__signal1.GetSamplingRate(), labels=labels)
            if not self.__shift:
                shift = 0
                if self.__mode == sumpf.modules.CorrelateSignals.FULL:
                    shift = -len(self.__signal2) + 1
                elif self.__mode == sumpf.modules.CorrelateSignals.SAME:
                    shift = -(len(self.__signal2) // 2)
                result = sumpf.modules.ShiftSignal(signal=result, shift=shift, circular=True).GetOutput()
            return result

    def __SetCorrelationMode(self, mode):
        """
        A private helper method to avoid, that the connector SetCorrelationMode
        is called in the constructor.
        @param mode: one of the modes from the description
        """
        if mode not in ["full", "same", "valid", "spectrum"]:
            raise ValueError("Unrecognized Mode: " + str(mode))
        self.__mode = mode

