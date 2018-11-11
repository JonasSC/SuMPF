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
    def __init__(self, signal=None, window=8192, overlap=0.5):
        """
        @param signal: the Signal that shall be transformed
        @param window: a window Signal that is multiplied with each block before the transformation. Can be abbreviated by passing the integer block length. See the SetWindow method for details
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
        Sets a window Signal, with which each block of the input Signal is multiplied
        This window defines the block length of the short time fourier transfomation.
        It is recommended that window specifies a smooth fade in and fade out for
        the blocks, to avoid unwanted high frequency content from the abrupt endings
        of the blocks. It is possible to create such a window with the WindowGenerator
        module.
        If the window Signal has more than one channel, its channel count has to
        be equal to that of the input Signal.
        The definition of the window Signal can be abbreviated by passing the integer
        block length of the transformation. A window with the given length will
        then be created internally. If the overlap is 0, the window will have a
        rectangular shape. Otherwise the window will use the VonHann-function.
        @param window: a Signal instance or an integer
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
        # prepare the window
        if isinstance(self.__window, int):
            if self.__overlap == 0:
                function = sumpf.modules.WindowGenerator.Rectangle()
            else:
                function = sumpf.modules.WindowGenerator.VonHann()
            window = sumpf.modules.WindowGenerator(rise_interval=(0, self.__window // 2),
                                                   fall_interval=(self.__window // 2, self.__window),
                                                   function=function,
                                                   samplingrate=self.__signal.GetSamplingRate(),
                                                   length=self.__window).GetSignal()
        else:
            window = self.__window
            if self.__signal.GetSamplingRate() != window.GetSamplingRate():
                raise ValueError("The window has a different sampling rate than the input signal")
            if len(window.GetChannels()) > 1 and len(window.GetChannels()) != len(self.__signal.GetChannels()):
                raise ValueError("The window has a different number of channels than the input signal")
        window = sumpf.modules.CopySignalChannels(signal=window, channelcount=len(self.__signal.GetChannels())).GetOutput()
        # precompute some values
        block_length = len(window)
        fft_block_length = block_length // 2 + 1
        resolution = self.__signal.GetSamplingRate() / len(window)
        overlap = self.__overlap
        if isinstance(overlap, float):
            overlap = int(round(overlap * block_length))
        elif overlap >= block_length:
            raise ValueError("The overlap has to be less than the block length")
        pre_zeros = (0.0,) * overlap
        post_zeros = (0.0,) * block_length
        # create a DelayFilterGenerator for taking the block's phases into account
        delay_filter = sumpf.modules.DelayFilterGenerator(resolution=resolution, length=fft_block_length)
        # compute the transformation
        channels = []
        for c, w in zip(self.__signal.GetChannels(), window.GetChannels()):
            padded_channel = pre_zeros + c + post_zeros
            channel = (0.0,) * fft_block_length
            number_of_blocks = 0
            for b in range(0, len(c) + overlap, block_length - overlap):
                block = padded_channel[b:b + block_length]
                windowed_block = numpy.multiply(block, w)
                transformed_block = numpy.fft.rfft(windowed_block)
                delay_filter.SetDelay(float(b - overlap) / self.__signal.GetSamplingRate())
                group_delay_filter = delay_filter.GetSpectrum()
                compensated_block = numpy.multiply(transformed_block, group_delay_filter.GetChannels()[0])
                channel = numpy.add(channel, compensated_block)
                number_of_blocks += 1
            channels.append(tuple(numpy.divide(channel, 1.0)))
        # create and return the signal
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

