# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2019 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""Contains implementations of signals for window functions."""

import collections
import math
import numpy
import sumpf._internal as sumpf_internal
from ._signal import Signal

__all__ = ("RectangularWindow", "BartlettWindow",
           "HannWindow", "HammingWindow", "BlackmanWindow", "KaiserWindow")

##############
# Base class #
##############


class Window(Signal):
    """Abstract base class for signals, that can be used as window functions."""

    def __init__(self, plateau=0, sampling_rate=48000.0, length=8192):
        """
        :param plateau: an integer length or a float factor for the signal length,
                        that specifies, how many samples in the middle of the signal
                        shall be 1.0 without being affected by the window's fade
                        in and fade out.
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the window function
        """
        if not isinstance(plateau, int):
            plateau = int(round(plateau * length))
        channels = sumpf_internal.allocate_array(shape=(1, length), dtype=numpy.float64)
        if plateau == 0:
            channels[0, :] = self._function(length)
        else:
            fade_length = (length - plateau) // 2       # the length of the fade in or the fade out
            fade = self._function(2 * fade_length)
            channels[0, 0:fade_length] = fade[0:fade_length]
            channels[0, fade_length:length - fade_length] = 1.0
            channels[0, length - fade_length:] = fade[fade_length:]
        Signal.__init__(self, channels=channels, sampling_rate=sampling_rate, offset=0, labels=(self._label(),))

    def bandwidth(self, oversampling=8):
        """Computes the bandwidth of the window.

        The bandwidth is the frequency, at which the magnitude of the window
        function's spectrum drops below -3dB of its maximum value. A high bandwidth
        window function results in a smoothed spectrum of the processed signal,
        which is often undesired. Increasing the window's length helps reducing
        its bandwidth.

        The bandwidth is computed numerically by appending zeros to the window
        signal (to increase frequency resolution) and then transforming it to the
        frequency domain, where the crossing of the -3dB threshold is determined
        with linear interpolation of the spectrum's samples. A high value for the
        `oversampling` parameter increases the number of appended zeros and with
        that, the accuracy of this method at the cost of higher computational
        effort.

        :param oversampling: an integer factor for the signal length, that specifies
                             how long the padded signal shall be, that is transformed
                             to the frequency domain.
        :returns: the bandwidth as a float in Hz
        """
        padded_channel = numpy.empty(oversampling * self._length)
        padded_channel[0:self._length] = self._channels[0]
        padded_channel[self._length:] = 0.0
        spectrum = numpy.fft.rfft(padded_channel)
        threshold = abs(spectrum[0]) / math.sqrt(2.0)
        i = 0
        amplitude = 0.0
        for i, amplitude in enumerate(spectrum[1:]):
            if abs(amplitude) < threshold:
                break
        x2 = abs(amplitude)
        x1 = abs(spectrum[i])
        frequency_bin = 2.0 * (i + (threshold - x1) / (x2 - x1))
        resolution = 1.0 / self.duration() / oversampling
        return frequency_bin * resolution

    def scalloping_loss(self):
        """Computes the amplitude error in the frequency domain of the window
        function. This error is often referred to as *scalloping loss*. It is
        defined as the ratio of the magnitude's spectrum at 0Hz and at the first
        half frequency bin.

        It is computed by doubling the signal's length with zero padding and then
        transforming it into the frequency domain. This oversampled spectrum's
        first sample corresponds to the half frequency bin of the original signal's
        spectrum.

        :returns: the scalloping loss as a float factor
        """
        # append zeros to the window to double the frequency resolution of the spectrum
        padded_channel = numpy.empty(2 * self._length)
        padded_channel[0:self._length] = self._channels[0]
        padded_channel[self._length:] = 0.0
        spectrum = numpy.fft.rfft(padded_channel)
        # due to the doubled frequency resolution, the amplitude error at the
        # 0.5-frequency bins in the original resolution is now the ratio between
        # the first and the second bin
        return abs(spectrum[1] / spectrum[0])

    def recommended_overlap(self):
        """Computes the recommended overlap for block-wise signal processing algorithms,
        that operate on signals, that are split and weighted with this window function.
        The recommended overlap, that maximizes the difference between the amplitude
        flatness and the overlap correlation, which is often a good compromise,
        that achieves good accuracy with reasonable computational effort.

        The recommended overlap was proposed by G. Heinzel, A. Rüdiger and
        R. Schilling in their paper *`Spectrum and spectral density estimation by
        the Discrete Fourier transform (DFT), including a comprehensive list of
        window functions and some new flat-top windows <https://holometer.fnal.gov/GH_FFT.pdf#page=17>`_*,
        which was published by
        the Max-Planck-Institut für Gravitationsphysik in February 2002.

        :returns: the recommended overlap as an integer number of samples
        """
        overlap = numpy.arange(0, self._length)
        af = self.amplitude_flatness(overlap)
        oc = self.overlap_correlation(overlap)
        return numpy.min(numpy.argmax(af - oc))

    def scaling_factor(self, overlap):
        """Computes a correction factor for block-wise processed signals, that are
        split and weighted with this window, that maintains the original signal's
        amplitude in the processed signal.

        :param overlap: the overlap of the weighted segments as an integer of samples,
                        a float factor of the window's length or as an array to
                        compute the scaling factor for multiple overlaps at once.
        :returns: the scaling factor as a float, if the given overlap is a scalar
                  value, or as an array, if an array of overlaps has been given.
        """
        if isinstance(overlap, collections.Iterable):
            return numpy.vectorize(self.scaling_factor, otypes=(numpy.float64,))(overlap)
        if not isinstance(overlap, int):
            overlap = int(round(overlap * self._length))
        step = self._length - overlap
        if step == 0:
            return 0.0
        added = 0.0
        for shift in range(0, self._length, step):
            added += numpy.sum(self._channels[0, 0:self._length - shift])
            if shift != 0:
                added += numpy.sum(self._channels[0, shift:])
        return self._length / added

    def amplitude_flatness(self, overlap):
        """Computes the ratio of the minimum and the maximum of a sum of overlapping
        repetitions of this window. This is related to the amplitude error, that
        is being made in a block-wise processing of a signal with this window.

        :param overlap: the overlap of the weighted segments as an integer of samples,
                        a float factor of the window's length or as an array to
                        compute the scaling factor for multiple overlaps at once.
        :returns: the amplitude flatness as a float, if the given overlap is a
                  scalar value, or as an array, if an array of overlaps has been
                  given.
        """
        if isinstance(overlap, collections.Iterable):
            return numpy.vectorize(self.amplitude_flatness, otypes=(numpy.float64,))(overlap)
        if not isinstance(overlap, int):
            overlap = int(round(overlap * self._length))
        if overlap == 0:
            minimum = self._channels[0, 0]
            maximum = minimum
        elif overlap == self._length:
            return 1.0
        else:
            step = self._length - overlap
            period = min(overlap, step)
            overlapping = numpy.zeros(period)
            for start in range(0, self._length, step):
                stop = min(start + period, self._length)
                overlapping[0:stop - start] += self._channels[0, start:stop]
            minimum = min(overlapping)
            maximum = max(overlapping)
        if overlap * 2 < self._length:
            non_overlapping = self._channels[0, overlap:(self._length + 1) // 2]    # length+1, so the division result is rounded up
            minimum = min(minimum, min(non_overlapping))
            maximum = max(maximum, max(non_overlapping))
        return minimum / maximum

    def power_flatness(self, overlap):
        """Computes the ratio of the minimum and the maximum of a squared sum of
        overlapping repetitions of this window. This is related to the power error,
        that is being made in a block-wise processing of a signal with this window.

        :param overlap: the overlap of the weighted segments as an integer of samples,
                        a float factor of the window's length or as an array to
                        compute the scaling factor for multiple overlaps at once.
        :returns: the power flatness as a float, if the given overlap is a scalar
                  value, or as an array, if an array of overlaps has been given.
        """
        if isinstance(overlap, collections.Iterable):
            return numpy.vectorize(self.power_flatness, otypes=(numpy.float64,))(overlap)
        if not isinstance(overlap, int):
            overlap = int(round(overlap * self._length))
        if overlap == 0:
            minimum = self._channels[0, 0] ** 2
            maximum = minimum
        elif overlap == self._length:
            return 1.0
        else:
            step = self._length - overlap
            period = min(overlap, step)
            overlapping = numpy.zeros(period)
            for start in range(0, self._length, step):
                stop = min(start + period, self._length)
                overlapping[0:stop - start] += numpy.square(self._channels[0, start:stop])
            minimum = min(overlapping)
            maximum = max(overlapping)
        if overlap * 2 < self._length:
            non_overlapping = self._channels[0, overlap:(self._length + 1) // 2]    # length+1, so the division result is rounded up
            squared = numpy.square(non_overlapping)
            minimum = min(minimum, min(squared))
            maximum = max(maximum, max(squared))
        return minimum / maximum

    def overlap_correlation(self, overlap):
        """Computes an estimate for the wasted computational effort in a block-wise
        processing of a signal with this window and the given overlap. The term
        overlap correlation was introduced by F. Harris in his paper *On the Use
        of Windows for Harmonic Analysis with the Discrete Fourier Transform*,
        which was published by the IEEE in January 1978.

        :param overlap: the overlap of the weighted segments as an integer of samples,
                        a float factor of the window's length or as an array to
                        compute the scaling factor for multiple overlaps at once.
        :returns: the overlap correlation as a float, if the given overlap is a
                  scalar value, or as an array, if an array of overlaps has been
                  given.
        """
        if isinstance(overlap, collections.Iterable):
            return numpy.vectorize(self.overlap_correlation, otypes=(numpy.float64,))(overlap)
        if not isinstance(overlap, int):
            overlap = int(round(overlap * self._length))
        numerator = numpy.sum(self._channels[0, 0:overlap] * self._channels[0, self._length - overlap:])
        denominator = numpy.sum(numpy.square(self._channels[0]))
        if denominator == 0.0:
            return 1.0
        else:
            return numerator / denominator

    def _function(self, length):
        """An abstract method, in which derived classes shall implement the generation
        of the window function.

        The generated window shall be symmetrical (no cropping of the last sample)
        and it shall not deal with the plateau, because this is implemented in
        this base class.

        :param length: the length of the window function as an integer number of samples
        :returns: the window function in a one-dimensional :func:`numpy.array`
        """
        raise NotImplementedError("This method has to be implemented in a derived class")

    def _label(self):
        """An abstract method, in which derived classes shall implement the generation
        of a label for the window function.

        :returns: a string
        """
        raise NotImplementedError("This method has to be implemented in a derived class")

##############################################################
# Classes with NumPy implementations of the window functions #
##############################################################


class RectangularWindow(Window):
    """Rectangular windows are mostly used in applications, where a repeated signal
    shall be reduced to a single repetition by a block-wise processing without
    an overlap. In other applications, the high level of the side lobes and the
    large scalloping loss make this window a sub-optimal choice.
    """

    def _function(self, length):
        return numpy.ones(length)

    def _label(self):
        return "Rectangular window"


class BartlettWindow(Window):
    """The Bartlett window is a triangular window with linearly rising and falling
    edges. It has a low bandwidth, but due to the high level of the side lobes,
    this window is unsuitable for most applications.
    """

    def _function(self, length):
        return numpy.bartlett(length)

    def _label(self):
        return "Bartlett window"


class HannWindow(Window):
    """The Hann window is a raised cosine window with two terms, that is optimized
    for a fast decay of the side lobes.
    """

    def _function(self, length):
        return numpy.hanning(length)

    def _label(self):
        return "Hann window"


class HammingWindow(Window):
    """The Hamming window is a raised cosine window with two terms, that is optimized
    for a minimal amplitude of the highest side lobe.
    """

    def _function(self, length):
        return numpy.hamming(length)

    def _label(self):
        return "Hamming window"


class BlackmanWindow(Window):
    """The Blackman is a three-term raised cosine window, that approximates the
    "exact Blackman window", which in turn has the same rate of decay of the side
    lobes as the Hann window, while using the remaining degree of freedom to
    optimize the attenuation of the highest side lobe.
    """

    def _function(self, length):
        return numpy.blackman(length)

    def _label(self):
        return "Blackman window"


class KaiserWindow(Window):
    """The Kaiser window uses a Bessel function and is therefore also known as
    the Kaiser-Bessel window. It is an approximation of the DPSS window.

    The Kaiser window features a parameter *beta*, that allows to trade in a low
    bandwidth (low *beta*) for good amplitude flatness and a high attenuation of
    the side lobes (high *beta*).
    """

    def __init__(self, beta=9.4248, plateau=0, sampling_rate=48000.0, length=8192):
        """
        :param beta: the *beta* parameter for the kaiser window. Some literature
                     specifies an *alpha* parameter here, where *beta* = *pi* * *alpha*
        :param plateau: an integer length or a float factor for the signal length,
                        that specifies, how many samples in the middle of the signal
                        shall be 1.0 without being affected by the window's fade
                        in and fade out.
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the window function
        """
        self.__beta = beta
        Window.__init__(self, plateau=plateau, sampling_rate=sampling_rate, length=length)

    def _function(self, length):
        return numpy.kaiser(length, self.__beta)

    def _label(self):
        return "Kaiser window"
