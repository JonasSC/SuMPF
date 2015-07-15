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
import numpy

samplerate_available = True
try:
    import scikits.samplerate
except ImportError:
    samplerate_available = False



class ResampleSignal(object):
    """
    A module for changing the sampling rate of a Signal.
    The sampling rate can be increased or decreased. It is not necessary that
    the output sampling rate is an integer fraction or multiple of the input
    sampling rate.
    """
    SPECTRUM = 0

    def __init__(self, signal=None, samplingrate=None, algorithm=SPECTRUM):
        """
        All parameters are optional.
        @param signal: the input Signal that shall be resampled
        @param samplingrate: the desired sampling rate of the output Signal or None, to keep the sampling rate of the input Signal
        @param algorithm: a flag for the resampling algorithm that shall be used. See SetAlgorithm for details
        """
        self.__signal = signal
        if signal is None:
            self.__signal = sumpf.Signal()
        self.__samplingrate = samplingrate
        self.__algorithm = algorithm

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        """
        Sets the input Signal that shall be resampled.
        @param signal: the input Signal that shall be resampled
        """
        self.__signal = signal

    @sumpf.Input(float, "GetOutput")
    def SetSamplingRate(self, samplingrate):
        """
        Sets the sampling rate of the output Signal.
        If the sampling rate is set to None, the input Signal will be passed
        to the output and no sampling rate conversion will be done.
        @param samplingrate: the desired sampling rate of the output Signal or None, to keep the sampling rate of the input Signal
        """
        self.__samplingrate = samplingrate

    @sumpf.Input(int, "GetOutput")
    def SetAlgorithm(self, algorithm):
        """
        Sets the algorithm for the resampling of the Signal.
        Currently, there are two algorithms available, SPECTRUM and SINC.
        SPECTRUM is the default algorithm, as it only requires the external library
        numpy to be available. It transforms the input Signal to the frequency
        domain and adjusts the resulting Spectrum's length according to the target
        sampling rate. For upsampling, zeros are appended to the Spectrum. For
        downsampling, the Spectrum will be cropped.
        SINC is only available, when the external libraries numpy and scikits.samplerate
        are available. It uses the "sinc_best" mode from scikits.samplerate, which
        itself uses the resampling algorithm from libsamplerate. This high quality
        resampling algorithm should yield better results than the SPECTRUM algorithm.
        @param algorithm: a flag for the resampling algorithm that shall be used (e.g. ResampleSignal.SPECTRUM)
        """
        self.__algorithm = algorithm

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Calculates the resampled output Signal and returns it.
        @retval : a Signal instance with the given sampling rate
        """
        if self.__samplingrate is None or self.__samplingrate == self.__signal.GetSamplingRate():
            return self.__signal
        if self.__algorithm == ResampleSignal.SPECTRUM:
            spectrum = sumpf.modules.FourierTransform(signal=self.__signal).GetSpectrum()
            spectrum_length = sumpf.modules.ChannelDataProperties(samplingrate=self.__samplingrate,
                                                                  resolution=spectrum.GetResolution()).GetSpectrumLength()
            channels = []
            for c in spectrum.GetChannels():
                channel = []
                for i in range(min(len(spectrum), spectrum_length)):
                    channel.append(c[i])
                for i in range(len(spectrum), spectrum_length):
                    channel.append(0.0)
                channels.append(tuple(channel))
            resampled_spectrum = sumpf.Spectrum(channels=tuple(channels), resolution=spectrum.GetResolution(), labels=spectrum.GetLabels())
            factor = self.__samplingrate / self.__signal.GetSamplingRate()
            return sumpf.modules.InverseFourierTransform(spectrum=resampled_spectrum).GetSignal() * factor
        elif hasattr(ResampleSignal, "SINC") and self.__algorithm == ResampleSignal.SINC:
            factor = self.__samplingrate / self.__signal.GetSamplingRate()
            channels = []
            for c in self.__signal.GetChannels():
                in_channel = numpy.array(c)
                out_channel = scikits.samplerate.resample(in_channel, factor, 'sinc_best')
                channels.append(tuple(out_channel))
            return sumpf.Signal(channels=tuple(channels), samplingrate=self.__samplingrate, labels=self.__signal.GetLabels())
        else:
            raise ValueError("Unknown resampling algorithm")



# add the possibility to use the resampling algorithm from scikits.samplerate,
# if that library is available
if samplerate_available:
    ResampleSignal.SINC = 1

