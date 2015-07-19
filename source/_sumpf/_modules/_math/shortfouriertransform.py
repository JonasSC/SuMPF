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


class ShortFourierTransform(object):
    """
    A class for a short fourier transformation of a Signal.
    This algorithm splits the input Signal into multiple blocks, which are fourier
    transformed individually and then summed up. The blocks should be faded in and
    out with a window function and they should have an overlap to avoid weird
    artifacts in the frequency domain.
    This algorithm is similar to the "short time fourier transform", which is used
    to calculate spectrograms. But instead of using the short time spectra to get
    a time dependent spectrum, they are summed up to get a spectrum with a length
    that is independent of the length of the input signal. In most cases, this will
    mean that the calculated spectrum is shorter, than the DFT-spectrum of the
    input signal. Therefore the name "ShortFourierTransform". Nevertheless, it is
    possible to create a Spectrum with this algorithm that is longer than the
    respective DFT-spectrum, by choosing a window that is longer than the input
    signal.
    """
    def __init__(self, signal=None, window=None, overlap=0.5):
        """
        @param signal: the Signal that shall be transformed
        @param window: a Signal instance that is multiplied with each block before the transformation. The length of the window defines the block length
        @param overlap: an integer number of samples by which the blocks shall overlap, or a float that specifies the overlap a factor of the block length
        """
        if signal is None:
            signal = sumpf.Signal()
        self.__signal = signal
        self.__window = window
        self.__SetOverlap(overlap)

    @sumpf.Input(sumpf.Signal, "GetSpectrum")
    def SetSignal(self, signal):
        """
        Sets the input Signal.
        @param signal: the input Signal that shall be transformed
        """
        self.__signal = signal

    @sumpf.Input(sumpf.Signal, "GetSpectrum")
    def SetWindow(self, window):
        """
        Sets a window that defines the block length of the short time fourier
        transfomation with its length. Each Block is multiplied with this window
        before the transformation, so it is recommended that window specifies a
        smooth fade in and fade out for the blocks, to avoid unwanted high frequency
        content from the abrupt endings of the blocks. It is possible to create
        such a window with the WindowGenerator module.
        Only the first channel of the window Signal is used.
        @param window: a Signal instance that specifies the block length and a fade in and out for the blocks
        """
        self.__window = window

    @sumpf.Input((int, float), "GetSpectrum")
    def SetOverlap(self, overlap):
        """
        Sets the number of samples by which blocks shall overlap.
        The overlap can be specified by two ways:
         - If overlap is an integer, it is interpreted as the number of samples
           of the overlap
         - If overlap is a float, it is interpreted as a factor that is multiplied
           with the block length to calculate the number of samples of the overlap
        @param overlap: an integer number of samples by which the blocks shall overlap, or a float that specifies the overlap a factor of the block length
        """
        self.__SetOverlap(overlap)

    @sumpf.Output(sumpf.Spectrum)
    def GetSpectrum(self):
        """
        Calculates and returns the short time fourier spectrum of the given input
        Signal.
        @retval : the Spectrum resulting from the transformation
        """
        window = self.__window
        if window is None:
            window = sumpf.modules.WindowGenerator(raise_interval=(0, 4096),
                                                   fall_interval=(4096, 8192),
                                                   function=sumpf.modules.WindowGenerator.Hanning(),
                                                   samplingrate=self.__signal.GetSamplingRate(),
                                                   length=8192).GetSignal()
        elif self.__signal.GetSamplingRate() != window.GetSamplingRate():
            raise ValueError("The window has a different sampling rate than the input signal")
        block_length = len(window)
        fft_block_length = block_length // 2 + 1
        resolution = self.__signal.GetSamplingRate() / len(window)
        overlap = self.__overlap
        if isinstance(overlap, float):
            overlap = int(round(overlap * block_length))
        elif overlap >= block_length:
            raise ValueError("The overlap has to be less than the window length")
        pre_zeros = (0.0,) * overlap
        post_zeros = (0.0,) * (len(self.__signal) + block_length)
        channels = []
        for c in self.__signal.GetChannels():
            padded_channel = pre_zeros + c + post_zeros
            channel = (0.0,) * fft_block_length
            for b in range(0, len(c) + overlap, block_length - overlap):
                block = padded_channel[b:b + block_length]
                windowed_block = numpy.multiply(block, window.GetChannels()[0])
                transformed_block = numpy.fft.rfft(windowed_block)
                group_delay_filter = sumpf.modules.DelayFilterGenerator(delay=(b - overlap) / self.__signal.GetSamplingRate(), resolution=resolution, length=fft_block_length).GetSpectrum()
                compensated_block = numpy.multiply(transformed_block, group_delay_filter.GetChannels()[0])
                channel = numpy.add(channel, compensated_block)
            channels.append(tuple(channel))
        return sumpf.Spectrum(channels=channels,
                              resolution=resolution,
                              labels=self.__signal.GetLabels())

    def __SetOverlap(self, overlap):
        """
        A private helper method to avoid, that the connector SetChannelCount is
        called in the constructor.
        @param overlap: an integer number of samples by which the blocks shall overlap, or a float that specifies the overlap a factor of the block length
        """
        if overlap < 0.0:
            raise ValueError("The overlap has to be greater than zero")
        elif isinstance(overlap, float) and overlap >= 1.0:
            raise ValueError("The overlap has to be less than the window length")
        else:
            self.__overlap = overlap

