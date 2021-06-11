# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2021 Jonas Schulte-Coerne
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

"""Contains the base container class for signals."""

import math
import numpy
import sumpf
import sumpf._internal as sumpf_internal
from .._sampled_data import SampledData

__all__ = ("Signal",)

# pylint: disable=too-many-lines; this is one of the main classes in SuMPF


class Signal(SampledData):
    """A base class for storing equidistantly sampled time data.

    This class can be instantiated directly, but *SuMPF* also provides sub-classes
    of this class, which can be used do generate specific signals such as sweeps
    and window functions. These sub-classes may feature additional functionality,
    that is specific for them and is therefore not comprised in this class.

    In addition to the functionality of its methods, this class has some operator
    overloads:

    * Common operators
       * checking the equality with ``==`` and ``!=``
       * slicing with ``[]``: returns a :class:`~sumpf.Signal` instance with the
         selected slice. Slicing in *SuMPF* works similar to slicing in :mod:`numpy`,
         so passing a tuple with a slice for the channels and another slice for
         the channels is possible. In addition to that, the indices can also be
         specified as floats between 0.0 and 1.0, where 0.0 indices the first
         element in the array and 1.0 is mapped to the length of the array.
         For example cropping a signal to the first half of its channels and the
         second half of its samples can be done like so: ``signal[0:0.5, 0.5:]``
    * Operators for built-in functions
       * getting the length with :func:`len`: this returns the number of channels,
         just like ``len(signal.channels())`` would. To get the number of samples
         per channel, use the :meth:`~sumpf.Signal.length` method.
       * casting to a mildly informative string with :class:`str`.
       * casting to a representation with :func:`repr`. If :func:`~numpy.array`,
         :class:`~numpy.float64` (both from :mod:`numpy`) and :class:`~sumpf.Signal`
         (from *SuMPF*) are defined in the current name space, the signal can be
         reproduced by evaluating the representation (``eval(repr(signal))``).
         Keep in mind, that the string representation of :func:`numpy.array` does
         not include the float values with the full precision, so that the reproduced
         signal might differ slightly from the original.
       * computing the absolute of each sample with :func:`abs`.
       * reversing the signal with :func:`reversed`. Only the order of the samples
         is reversed, the channels remain in their original order.
    * Math operators
       * computing the negative of the signal's samples with ``-signal``.
       * sample-wise algebra operations with ``+``, ``-``, ``*``, ``/``, ``%`` and ``**``:
         These operators work with signals, numbers and vectorial objects such as
         arrays, tuples or lists. Broadcasting is done like in :mod:`numpy` (e.g.
         adding a single-channel signal to a multi-channel one, will add the channel
         of the first signal to each of the second.)
    * Rededicated operators (operators, for which Python has intended a different function than for what it is used in the :class:`~sumpf.Signal` class)
       * inverting the signal with ``~signal``. The inverse of a signal is computed
         as a division in the frequency domain: ``iFFT(1 / FFT(signal))``.
    """

    file_formats = sumpf_internal.signal_writers.Formats    #: an enumeration with file formats, whose flags can be passed to :meth:`~sumpf.Signal.save` (see the :class:`sumpf._internal._signal_writers.Formats` class).
    convolution_modes = sumpf_internal.ConvolutionMode      #: an enumeration with modes for the :meth:`~sumpf.Signal.convolve` and :meth:`~sumpf.Signal.correlate` methods (see the :class:`~sumpf._internal._enums.ConvolutionMode` class).
    shift_modes = sumpf_internal.ShiftMode                  #: an enumeration with modes for the :meth:`~sumpf.Signal.shift` method (see the :class:`~sumpf._internal._enums.ShiftMode` class).

    def __init__(self, channels=numpy.empty(shape=(1, 0)), sampling_rate=48000.0, offset=0, labels=None):
        """
        :param channels: a two-dimensional :func:`numpy.array` of channels with float samples.
        :param sampling_rate: the sampling rate of the signal as a float or integer.
        :param offset: an integer number of samples, by which the first sample of
                       the channel is delayed virtually. The offset can also be
                       negative, if the signal shall be non-causal.
        :param labels: a sequence of string labels for the channels.
        """
        SampledData.__init__(self, channels, labels)
        self.__sampling_rate = sampling_rate
        self.__offset = offset

    ###########################################
    # overloaded operators (non math-related) #
    ###########################################

    def __getitem__(self, key):
        """Operator overload for slicing the signal.

        :param key: an index, a slice or a tuple of indices or slices. Indices may
                    be integers or floats between 0.0 and 1.0.
        :returns: a :class:`~sumpf.Signal` instance
        """
        slices = sumpf_internal.key_to_slices(key, self._channels.shape)
        offset = self.__offset
        if isinstance(slices, tuple):
            if slices[1].start:
                if slices[1].start < 0:
                    offset += self._length + slices[1].start
                else:
                    offset += slices[1].start
            c = slices[0]
        else:
            c = slices
        return Signal(channels=self._channels[slices],
                      sampling_rate=self.__sampling_rate,
                      offset=offset,
                      labels=self._labels[c])

    def __str__(self):
        """Operator overload for generating a short description of the signal
        with the built-in function :class:`str`.

        :returns: a reasonably short string
        """
        return (f"<{self.__module__}.{self.__class__.__name__} object "
                f"(length: {self._length}, "
                f"sampling rate: {self.__sampling_rate:.2f}, "
                f"offset: {self.__offset}, "
                f"channel count: {len(self)}) "
                f"at 0x{id(self):x}>")

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the signal, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        channels = numpy.array2string(self._channels,
                                      separator=",",
                                      formatter={"all": repr},
                                      threshold=self._channels.size).replace("\n", "").replace(" ", "")
        return (f"{self.__class__.__name__}(channels=array({channels}), "
                f"sampling_rate={self.__sampling_rate!r}, "
                f"offset={self.__offset}, "
                f"labels={self._labels})")

    def __eq__(self, other):
        """Operator overload for comparing this signal to another object with ``==``"""
        if not isinstance(other, Signal):
            return False
        elif self.__sampling_rate != other.sampling_rate():
            return False
        elif self.__offset != other.offset():
            return False
        return super().__eq__(other)

    def __hash__(self):
        """Operator overload for computing the hash of this signal with :func:`hash`"""
        return hash((super().__hash__(), self.__sampling_rate, self.__offset))

    ###################################
    # overloaded unary math operators #
    ###################################

    def __abs__(self):
        """Operator overload for computing the sample-wise absolute of the signal
        with the built-in function :func:`abs`.

        :returns: a :class:`~sumpf.Signal` instance
        """
        return Signal(channels=numpy.fabs(self._channels, out=sumpf_internal.allocate_array(self.shape())),
                      sampling_rate=self.__sampling_rate,
                      offset=self.__offset,
                      labels=self._labels)

    def __reversed__(self):
        """Operator overload for reversing signal's channels with the built-in
        function :func:`reversed`.

        The offset of the reversed signal will be computed, so that the reversed
        signal equals the original signal for negative time values. E.g. a causal
        signal will therefore be shifted completely before the zero point in time.

        :returns: a :class:`~sumpf.Signal` instance
        """
        return Signal(channels=self._channels[:, ::-1],
                      sampling_rate=self.__sampling_rate,
                      offset=self._length - self.__offset - 1,
                      labels=self._labels)

    def __neg__(self):
        """Operator overload for computing the sample-wise negative of the signal
        with ``-signal``.

        :returns: a :class:`~sumpf.Signal` instance
        """
        return Signal(channels=numpy.negative(self._channels, out=sumpf_internal.allocate_array(self.shape())),
                      sampling_rate=self.__sampling_rate,
                      offset=self.__offset,
                      labels=self._labels)

    ####################################
    # overloaded binary math operators #
    ####################################

    def __mod__(self, other):
        """Operator overload for computing the remainder of a division of this
        signal by another signal, an array or number.

        :param other: a signal, an array or a number
        :returns: a :class:`~sumpf.Signal` instance
        """
        return self._algebra_function(other=other, function=numpy.mod, other_pivot=None, label="Modulo")

    def __rmod__(self, other):
        """Right hand side Operator overload for computing the remainder of a
        division another signal, an array or number by this signal.

        :param other: a :class:`~sumpf.Signal`, an array or a number
        :returns: a :class:`~sumpf.Signal` instance
        """
        return self._algebra_function_right(other=other, function=numpy.mod, other_pivot=None, label="Modulo")

    #########################################
    # overloaded and misused math operators #
    #########################################

    def __invert__(self):
        """Rededicated operator overload for inverting this signal.
        Convolving a signal with its inverse results in a unit impulse. The inverse
        is computing in the frequency domain: ``ifft(1 / fft(signal))``.

        :returns: a :class:`~sumpf.Signal` instance
        """
        channels = sumpf_internal.allocate_array(shape=self.shape())
        if self._length % 2 == 0:
            spectrum = numpy.fft.rfft(self._channels)
            channels[:] = numpy.fft.irfft(1.0 / spectrum)
        else:
            # odd-length signals require zero padding, so that there is no sample lost in the FFT
            padded = numpy.empty((len(self), 2 * self._length))
            padded[:, 0:self._length] = self._channels
            padded[:, self._length:] = 0.0
            spectrum = numpy.fft.rfft(padded)
            padded = numpy.fft.irfft(1.0 / spectrum)
            channels[:] = padded[:, 0:self._length]
            channels += padded[:, self._length:]
        return Signal(channels=channels,
                      sampling_rate=self.__sampling_rate,
                      offset=-self.__offset,
                      labels=self._labels)

    #######################################################
    # parameters, that have been set with the constructor #
    #######################################################

    def sampling_rate(self):
        """Returns the sampling rate of this signal.

        :returns: a number
        """
        return self.__sampling_rate

    def offset(self):
        """Returns the offset of this signal.
        Positive offsets mean, that the signal is delayed by that number of samples,
        while signals with negative offsets are preponed.
        The time value for the first sample in the channels is ``offset / sampling_rate``

        :returns: an integer
        """
        return self.__offset

    ######################
    # derived parameters #
    ######################

    def duration(self):
        """Returns the duration of this signal in seconds.

        :returns: a float
        """
        return self._length / self.__sampling_rate

    #######################
    # convenience methods #
    #######################

    def time_samples(self):
        """Returns an array with the time samples for each sample of the signal's channels.

        :returns: a one dimensional :func:`numpy.array`
        """
        return numpy.linspace(self.__offset / self.__sampling_rate,
                              (self._length + self.__offset - 1) / self.__sampling_rate,
                              self._length)

    def pad(self, length, value=0.0):
        """Returns a signal with the given length, which is achieved by either
        cropping or appending the given value.

        :param length: the length of the resulting signal
        :param value: the value with which the signal shall be padded
        :returns: the padded or cropped :class:`~sumpf.Signal`
        """
        if length == self._length:
            return self
        else:
            channels = sumpf_internal.allocate_array(shape=(len(self), length))
            if length < self._length:
                channels[:] = self._channels[:, 0:length]
            else:
                channels[:, 0:self._length] = self._channels
                channels[:, self._length:] = value
            return Signal(channels=channels,
                          sampling_rate=self.__sampling_rate,
                          offset=self.__offset,
                          labels=self._labels)

    def shift(self, shift, mode=sumpf_internal.ShiftMode.OFFSET):
        """Returns a signal, which is shifted in time.

        Positive shifts result in a delayed signal, while negative shifts prepone it.
        In mode ``OFFSET``, it is allowed to pass ``None`` for the ``shift`` parameter,
        which sets the offset of the resulting :class:`~sumpf.Signal` to 0.

        The shift can be performed in different ways, which can be specified with
        the ``mode`` parameter. The flags, that can be passed to this parameter
        are defined and documented in the :class:`sumpf.Signal.shift_modes`
        enumeration.

        :param shift: an integer number of samples, by which the signal shall be shifted
        :param mode: a flag from the :class:`sumpf.Signal.shift_modes` enumeration
        :returns: the shifted :class:`~sumpf.Signal`
        """
        if shift == 0:
            return self
        elif mode == Signal.shift_modes.OFFSET:
            if shift is None:
                return Signal(channels=self._channels,
                              sampling_rate=self.__sampling_rate,
                              offset=0,
                              labels=self._labels)
            else:
                return Signal(channels=self._channels,
                              sampling_rate=self.__sampling_rate,
                              offset=self.__offset + shift,
                              labels=self._labels)
        else:
            if mode == Signal.shift_modes.CROP:
                channels = sumpf_internal.allocate_array(shape=self._channels.shape)
                if shift < 0:
                    channels[:, 0:shift] = self._channels[:, -shift:]
                    channels[:, shift:] = 0.0
                else:
                    channels[:, 0:shift] = 0.0
                    channels[:, shift:] = self._channels[:, 0:-shift]
            elif mode == Signal.shift_modes.PAD:
                channels = sumpf_internal.allocate_array(shape=(len(self), self._length + abs(shift)))
                if shift < 0:
                    channels[:, 0:self._length] = self._channels
                    channels[:, self._length:] = 0.0
                else:
                    channels[:, 0:shift] = 0.0
                    channels[:, shift:] = self._channels
            elif mode == Signal.shift_modes.CYCLE:
                channels = sumpf_internal.allocate_array(shape=self._channels.shape)
                channels[:, 0:shift] = self._channels[:, -shift:]
                channels[:, shift:] = self._channels[:, 0:-shift]
            return Signal(channels=channels,
                          sampling_rate=self.__sampling_rate,
                          offset=self.__offset,
                          labels=self._labels)

    #############################
    # signal processing methods #
    #############################

    def fourier_transform(self, window=None, overlap=0.5, pad=True):
        """Computes the channel-wise Fourier transform of this signal.

        If a window is specified, the Fourier transform is performed block-wise
        with the window defining the block size and being applied to each block
        before the transform.

        The offset of the signal is taken into account as a constant addition to
        the group delay.

        :param window: either None to transform the signal in a single transform
                       and have a spectrum with the full resolution. Or a window
                       function, that is used for a block-wise transform of the
                       signal. The window function can be passed as a :class:`~sumpf.Signal`,
                       as an iterable or an integer window length. See
                       :func:`~sumpf._internal._functions.get_window` for details.
        :param overlap: the overlap of the signal segments. It can be passed as
                        an integer number of samples or a float fraction of the
                        window's length. Negative numbers will be added to the
                        window's length. This parameter is only considered when
                        performing a block-wise Fourier transform.
        :param pad: True, if the signal shall be padded with zeros to fit an integer
                    number of segments. False, if the samples at the end of the
                    signal, that do not fit a full segment, shall be ignored. This
                    parameter is only considered when performing a block-wise
                    Fourier transform.
        :returns: a :class:`~sumpf.Spectrum` instance
        """
        if window is None:
            channels, resolution = self.__full_fourier_transform()
        else:
            channels, resolution = self.__block_wise_fourier_transform(window, overlap, pad)
        return sumpf.Spectrum(channels=channels,
                              resolution=resolution,
                              labels=self._labels)

    def __full_fourier_transform(self):
        """Helper method for computing a full Fourier transform of this signal."""
        length = self._length // 2 + 1
        if len(self._channels) == 0:                                            # pylint: disable=len-as-condition; self._channels is a numpy array, that does not evaluate to False if empty
            resolution = self.__sampling_rate / max(self._length, 1)
            channels = sumpf_internal.allocate_array(shape=(0, length), dtype=numpy.complex128)
        elif self._length == 0:
            resolution = self.__sampling_rate
            channels = sumpf_internal.allocate_array(shape=(len(self._channels), 1), dtype=numpy.complex128)
            channels[:, :] = 0.0
        else:
            resolution = self.__sampling_rate / self._length
            channels = sumpf_internal.allocate_array(shape=(len(self._channels), length), dtype=numpy.complex128)
            spectrum = numpy.fft.rfft(self._channels)
            if self.__offset == 0:
                channels[:, :] = spectrum
            else:  # add a group delay for the offset
                max_compensation = (length - 1) * resolution * -2j * math.pi * self.__offset / self.__sampling_rate
                compensation = numpy.linspace(0.0, max_compensation, length, dtype=numpy.complex128)
                numpy.exp(compensation, out=compensation)
                numpy.multiply(spectrum, compensation, out=channels)
        return channels, resolution

    def __block_wise_fourier_transform(self, window, overlap, pad):
        """Helper method for computing a block-wise Fourier transform of this signal."""
        window = sumpf_internal.get_window(window, overlap, symmetric=False, sampling_rate=self.__sampling_rate)
        window_length = window.length()
        length = window_length // 2 + 1
        if len(self._channels) == 0 or len(window) == 0 or window_length == 0:  # pylint: disable=len-as-condition; these are numpy arrays, that do not evaluate to False if empty
            resolution = window.sampling_rate() / max(window_length, 1)
            channels = sumpf_internal.allocate_array(shape=(max(len(self._channels), len(window)), length),
                                                     dtype=numpy.complex128)
            channels[:, :] = 0.0
        else:
            window_channels = window.channels()
            overlap = sumpf_internal.index(overlap, window_length)
            resolution = window.sampling_rate() / window_length
            channels = sumpf_internal.allocate_array(shape=(max(len(self._channels), len(window)), length),
                                                     dtype=numpy.complex128)
            channels[:, :] = 0.0
            windowed = numpy.empty(shape=(max(len(self._channels), len(window)), window_length))
            compensated = numpy.empty(shape=channels.shape, dtype=channels.dtype)
            compensation_factor = (length - 1) * resolution * -2j * math.pi
            step = window_length - overlap
            if pad:
                for i in range(-step, -window_length, -step):
                    l = min(window_length + i, self._length)
                    windowed[:, 0:-i] = 0.0
                    windowed[:, l - i:] = 0.0
                    numpy.multiply(self._channels[:, 0:l],
                                   window_channels[:, -i:l - i],
                                   out=windowed[:, -i:l - i])
                    spectrum = numpy.fft.rfft(windowed)
                    max_compensation = compensation_factor * (self.__offset + i) / self.__sampling_rate
                    compensation = numpy.linspace(0.0, max_compensation, length, dtype=numpy.complex128)
                    numpy.exp(compensation, out=compensated)
                    compensated *= spectrum
                    channels += compensated
            i = 0
            for i in range(0, self._length - window_length + 1, step):
                numpy.multiply(self._channels[:, i:window_length + i],
                               window_channels,
                               out=windowed)
                spectrum = numpy.fft.rfft(windowed)
                max_compensation = compensation_factor * (self.__offset + i) / self.__sampling_rate
                compensation = numpy.linspace(0.0, max_compensation, length, dtype=numpy.complex128)
                numpy.exp(compensation, out=compensated)
                compensated *= spectrum
                channels += compensated
            if pad:
                for i in range(i + step, self._length, step):
                    k = self._length - i
                    windowed[:, k:] = 0.0
                    numpy.multiply(self._channels[:, i:],
                                   window_channels[:, 0:k],
                                   out=windowed[:, 0:k])
                    spectrum = numpy.fft.rfft(windowed)
                    max_compensation = compensation_factor * (self.__offset + i) / self.__sampling_rate
                    compensation = numpy.linspace(0.0, max_compensation, length, dtype=numpy.complex128)
                    numpy.exp(compensation, out=compensated)
                    compensated *= spectrum
                    channels += compensated
            channels.transpose()[:] *= sumpf_internal.scaling_factor(window, overlap)
        return channels, resolution

    def short_time_fourier_transform(self, window=4096, overlap=0.5, pad=True):
        """Computes a :class:`~sumpf.Spectrogram` from this signal.

        This method requires :mod:`scipy` to be installed.

        The spectrogram's offset is rounded to the nearest integer, which corresponds
        to the scaled offset of this signal. The remainder is then taken into account
        as a constant addition to the group delay.

        :param window: the window function, that is used to segment this signal.
                       It can be passed as a :class:`~sumpf.Signal`, as an iterable
                       or an integer window length. See :func:`~sumpf._internal._functions.get_window`
                       for details.
        :param overlap: the overlap of the signal segments. It can be passed as
                        an integer number of samples or a float fraction of the
                        window's length. Negative numbers will be added to the
                        window's length.
        :param pad: True, if the signal shall be padded with zeros to fit an integer
                    number of segments. False, if the samples at the end of the
                    signal, that do not fit a full segment, shall be ignored.
        """
        import scipy.signal  # pylint: disable=import-outside-toplevel; having this as a top-level import would make this whole class unavailable, if the scipy library is not installed
        # create some necessary objects
        window = sumpf_internal.get_window(window=window,
                                           overlap=overlap,
                                           symmetric=False,
                                           sampling_rate=self.__sampling_rate)
        window_length = window.length()
        overlap = sumpf_internal.index(overlap, window_length)
        step = window_length - overlap
        # compute the STFT
        if len(window) == 1:
            stft = scipy.signal.stft(self._channels,
                                     fs=self.__sampling_rate,
                                     window=window.channels()[0],
                                     nperseg=window_length,
                                     noverlap=overlap,
                                     boundary="zeros" if pad else None,
                                     padded=pad)[2]
        else:
            stft = []
            for c, w in zip(self._channels, window.channels()):
                stft.append(scipy.signal.stft(c,
                                              fs=self.__sampling_rate,
                                              window=w,
                                              nperseg=window_length,
                                              noverlap=overlap,
                                              boundary="zeros" if pad else None,
                                              padded=pad)[2])
        channels = sumpf_internal.allocate_array(shape=numpy.shape(stft), dtype=numpy.complex128)
        channels[:] = stft
        # deal with the offset
        resolution = self.__sampling_rate / window_length
        offset = int(round(self.__offset / step))
        offset_remainder = self.__offset - (offset * step)
        if offset_remainder:
            max_frequency = (window_length - 1) * resolution
            compensation = numpy.linspace(0.0, max_frequency, window_length // 2 + 1, dtype=numpy.complex128)
            compensation *= -1j * 2.0 * math.pi * (offset_remainder / self.__sampling_rate)
            numpy.exp(compensation, out=compensation)
            for c in channels:
                t = c.transpose()
                t *= compensation
        # return the spectrogram
        return sumpf.Spectrogram(channels=channels,
                                 resolution=resolution,
                                 sampling_rate=self.__sampling_rate / step,
                                 offset=offset,
                                 labels=self._labels)

    def level(self, single_value=False):
        """Computes the root-mean-square-level of the signal's channels.

        :param single_value: if False, an :func:`~numpy.array` with the level of
                             each channel is returned, otherwise a single value
                             for some sort of "total signal level" is computed,
                             which is the same as the level of the concatenation
                             of all channels
        :returns: an :func:`~numpy.array` or a float
        """
        if single_value:
            return numpy.linalg.norm(self._channels) / math.sqrt(len(self) * self._length)
        else:
            return numpy.linalg.norm(self._channels, axis=1) / math.sqrt(self._length)

    def level_vs_time(self, integration_time=1.0, pad=False):   # pylint: disable=too-many-branches; with the comments, this is relatively straight forward
        """Computes a time-dependent level of the signal.

        The level is computed individually for each sample with the integration
        interval being placed symmetrically around the given sample.

        :param integration_time: the time span in seconds, that shall be taken into
                                 account when computing the level. Common values
                                 are 1.0s and 0.125s.
        :param pad: if True, it is assumed, that the signal is zero for those points
                    in time, where the integration interval spans beyond the signal.
                    If False, the integration time is reduced for the samples at
                    the beginning and the end of the signal, so that the whole
                    integration interval is covered by the signal.
        """
        window_length = integration_time * self.__sampling_rate
        if window_length <= 1.0:
            return abs(self)
        half_window_length_float = (window_length - 1.0) / 2.0
        half_window_length = int(math.ceil(half_window_length_float))
        channels = sumpf_internal.allocate_array(shape=self._channels.shape)
        if 1 + half_window_length >= self._length:
            # if half the integration time is longer than the whole signal, the level is constant over time
            if pad:
                levels = numpy.linalg.norm(self._channels, axis=1) / math.sqrt(window_length)
            else:
                levels = self.level()
            for c, l in zip(channels, levels):
                c[:] = l
        else:
            # generate a window, that does the averaging of the squared signal
            remainder = half_window_length - half_window_length_float
            window = numpy.full(1 + 2 * half_window_length, 1.0 / window_length)
            if remainder:
                corner = remainder / window_length
                window[0] = corner
                window[-1] = corner
            square = numpy.square(self._channels)
            if len(window) < self._length:
                # compute the levels by convolving the squared signal with the window
                for s, c in zip(square, channels):
                    numpy.sqrt(numpy.convolve(s, window, mode="same"), out=c)
                if not pad:
                    # compute a compensation for the start and the end of the level signal, where the convolution has assumed a zero padding
                    effective_window_lengths = numpy.linspace(1 + half_window_length_float,
                                                              half_window_length + half_window_length_float,
                                                              half_window_length)
                    correction = numpy.sqrt(window_length / effective_window_lengths)
                    channels[:, 0:half_window_length] *= correction
                    channels[:, -half_window_length:] *= correction[::-1]
            else:
                # if the window is longer than the signal itself, there is no sample, that is computed with a whole integration window
                a = (len(window) + 1 - self._length) // 2
                b = a + self._length
                for s, c in zip(square, channels):
                    numpy.sqrt(numpy.convolve(s, window, mode="same")[a:b], out=c)
                if not pad:
                    # compute a compensation for the start and the end of the level signal, where the convolution has assumed a zero padding
                    correction = numpy.empty(self._length)
                    correction[0:half_window_length] = numpy.linspace(1 + half_window_length_float,
                                                                      half_window_length + half_window_length_float,
                                                                      half_window_length)
                    half_correction = correction[0:(self._length + 1) // 2]
                    numpy.clip(half_correction, a_min=0, a_max=self._length, out=half_correction)
                    numpy.divide(window_length, half_correction, out=half_correction)
                    numpy.sqrt(half_correction, out=half_correction)
                    correction[self._length - 1:(self._length + 1) // 2 - 1:-1] = correction[0:self._length // 2]   # copy the first half of the correction to the second half and reverse it
                    channels *= correction
        return sumpf.Signal(channels=channels,
                            sampling_rate=self.__sampling_rate,
                            offset=self.__offset,
                            labels=self._labels)

    def convolve(self, other, mode=sumpf_internal.ConvolutionMode.SPECTRUM_PADDED):
        """Convolves this signal with another signal or an :func:`~numpy.array`.

        The convolution can be performed in different modes, which can be specified
        by passing a flag from the :class:`sumpf.Signal.convolution_modes` enumeration
        as the ``mode`` parameter of this method.

        :param other: the :class:`~sumpf.Signal` or :func:`~numpy.array`, with which
                      this signal shall be convolved
        :param mode: a flag from the :class:`sumpf.Signal.convolution_modes` enumeration
        :returns: the convolution result as a :class:`~sumpf.Signal`
        """
        if isinstance(other, Signal):
            channels, offset = self.__convolve_with_array(other=other.channels(),
                                                          other_offset=other.offset(),
                                                          function=sumpf_internal.convolution,
                                                          mode=mode)
            labels = ("Convolution",) * len(self._channels)
        else:
            channels, offset = self.__convolve_with_array(other=other,
                                                          other_offset=0,
                                                          function=sumpf_internal.convolution,
                                                          mode=mode)
            labels = self._labels
        return Signal(channels=channels,
                      sampling_rate=self.__sampling_rate,
                      offset=offset,
                      labels=labels)

    def correlate(self, other, mode=sumpf_internal.ConvolutionMode.SPECTRUM_PADDED):
        """Computes the cross-correlation between this signal and a given signal
        or :func:`~numpy.array`.

        The convolution can be performed in different modes, which can be specified
        by passing a flag from the :class:`sumpf.Signal.convolution_modes` enumeration
        as the ``mode`` parameter of this method.

        The resulting signal will have the same channels as a convolution of the
        reverse of this signal with the given data set. This seems to be the more
        common implementation of a cross correlation. :mod:`numpy`'s :func:`~numpy.correlate`
        function, on the other hand, reverses the other data set instead of this
        signal. For the modes ``FULL`` and ``VALID``, this means, that *SuMPF*'s
        correlation results are the reverse of :mod:`numpy`'s. For the ``SAME`` mode,
        *SuMPF* uses :func:`~numpy.convolve` with the first data set reversed.

        :param other: the :class:`~sumpf.Signal` or :func:`~numpy.array`, with which
                      this signal shall be correlated
        :param mode: a flag from the :class:`sumpf.Signal.convolution_modes` enumeration
        :returns: the cross correlation result as a :class:`~sumpf.Signal`
        """
        if isinstance(other, Signal):
            channels, offset = self.__convolve_with_array(other=other.channels(),
                                                          other_offset=other.offset(),
                                                          function=sumpf_internal.correlation,
                                                          mode=mode)
            labels = ("Correlation",) * len(self._channels)
        else:
            channels, offset = self.__convolve_with_array(other=other,
                                                          other_offset=0,
                                                          function=sumpf_internal.correlation,
                                                          mode=mode)
            labels = self._labels
        return Signal(channels=channels,
                      sampling_rate=self.__sampling_rate,
                      offset=offset,
                      labels=labels)

    ####################################################
    # methods for statistical parameters of the signal #
    ####################################################

    def mean(self, single_value=False):
        """Computes the mean of the signal's channels.

        :param single_value: if False, a :func:`numpy.array` with the mean of each
                             channel is returned, otherwise the mean of all samples
                             is computed as a single value
        :returns: a :func:`numpy.array` or a float
        """
        if single_value:
            return numpy.mean(self._channels)
        else:
            return numpy.mean(self._channels, axis=1)

    def standard_deviation(self, single_value=False):
        """Computes the mean of the signal's channels.

        :param single_value: if False, a :func:`numpy.array` with the standard deviation
                             of each channel is returned, otherwise the standard
                             deviation of all samples is computed as a single value
        :returns: a :func:`numpy.array` or a float
        """
        if single_value:
            return numpy.std(self._channels)
        else:
            return numpy.std(self._channels, axis=1)

    def variance(self, single_value=False):
        """Computes the variance of the signal's channels.

        :param single_value: if False, a :func:`numpy.array` with the variance of each
                             channel is returned, otherwise the variance of all
                             samples is computed as a single value
        :returns: a :func:`numpy.array` or a float
        """
        if single_value:
            return numpy.var(self._channels)
        else:
            return numpy.var(self._channels, axis=1)

    def skewness(self, single_value=False):
        """Computes the skewness of the signal's channels.

        This method requires :mod:`scipy` to be installed.

        :param single_value: if False, a :func:`numpy.array` with the skewness of each
                             channel is returned, otherwise the skewness of all
                             samples is computed as a single value
        :returns: a :func:`numpy.array` or a float
        """
        import scipy.stats  # pylint: disable=import-outside-toplevel; having this as a top-level import would make this whole class unavailable, if the scipy library is not installed
        if single_value:
            return scipy.stats.skew(self._channels, axis=None)
        else:
            return scipy.stats.skew(self._channels, axis=1)

    def kurtosis(self, single_value=False):
        """Computes the kurtosis of the signal's channels.

        This method requires :mod:`scipy` to be installed.

        :param single_value: if False, a :func:`numpy.array` with the kurtosis of each
                             channel is returned, otherwise the kurtosis of all
                             samples is computed as a single value
        :returns: a :func:`numpy.array` or a float
        """
        import scipy.stats  # pylint: disable=import-outside-toplevel; having this as a top-level import would make this whole class unavailable, if the scipy library is not installed
        if single_value:
            return scipy.stats.kurtosis(self._channels, axis=None)
        else:
            return scipy.stats.kurtosis(self._channels, axis=1)

    #######################
    # persistence methods #
    #######################

    @staticmethod
    def load(path):
        """A static method to load a :class:`~sumpf.Signal` instance from a file.

        :param path: the path to the file.
        :raises ValueError: if the file cannot be read (e.g. because the library
                            for the file's format is missing)
        :returns: the loaded :class:`~sumpf.Signal`
        """
        return sumpf_internal.read_file(path=path,
                                        readers=sumpf_internal.signal_readers.readers,
                                        reader_base_class=sumpf_internal.signal_readers.Reader)

    def save(self, path, file_format=file_formats.AUTO):
        """Saves the signal to a file. The file will be created if it does not exist.

        :param path: the path to the file
        :param file_format: an optional flag from the :attr:`sumpf.Signal.file_formats`
                            enumeration, that specifies the file format, in which
                            the filter shall be stored. If this parameter is omitted
                            or set to :attr:`~sumpf.Signal.file_formats`.\ ``AUTO``,
                            the format will be guessed from the ending of the filename.
        :raises ValueError: if the file cannot be written (e.g. because the library
                            for the requested format is missing)
        :returns: self
        """
        writer = sumpf_internal.get_writer(file_format=file_format,
                                           writers=sumpf_internal.signal_writers.writers,
                                           writer_base_class=sumpf_internal.signal_writers.Writer)
        writer(self, path)
        return self

    ########################################################################
    # private helper methods for implementing math related functionalities #
    ########################################################################

    def _algebra_function(self, other, function, other_pivot, label):
        """Protected helper function that implements the broadcasting of signals
        or arrays with different shapes when using the overloaded math operators.

        :param other: the object "on the other side of the operator"
        :param function: a function, that implements the computation for arrays (e.g. numpy.add)
        :param other_pivot: a default value, that is used as first operand for samples, where
                            only the other object has data (e.g. when the two signals don't
                            overlap due to offsets). If ``other_pivot`` is ``None``, the data
                            from the other object is copied.
        :param label: the string label for the computed channels
        :returns: a :class:`~sumpf.Signal` instance
        """
        if isinstance(other, Signal):
            if len(self) == len(other) and self._length == other.length() and self.__offset == other.offset():
                # both signals overlap completely
                return self.__algebra_function_signals_overlap(other, function, label)
            elif len(self) == 1 and self._length == other.length() and self.__offset == other.offset():
                # both signals have the same length and offset, but this signal
                # has only one channel, so that the computation combines this
                # channel with each of the other signal's channels
                return self.__algebra_function_self_has_one_channel(other, function, label)
            elif len(other) == 1 and self._length == other.length() and self.__offset == other.offset():
                # both signals have the same length and offset, but the other
                # signal has only one channel, so that the computation combines
                # this channel with each of this signal's channels
                return self.__algebra_function_other_has_one_channel(other, function, label)
            else:
                # the signals have different lengths or offsets, which makes things complicated
                return self.__algebra_function_different_shapes(other, function, other_pivot, label)
        elif isinstance(other, (SampledData, sumpf.Filter)):
            return NotImplemented
        else:   # other is an array or a number
            return self.__algebra_function_different_type(other, function)

    def _algebra_function_right(self, other, function, other_pivot, label):
        """Protected helper function for overloading the right hand side operators.

        :param other: the object "on the left side of the operator"
        :param function: a function, that implements the computation for arrays (e.g. numpy.add)
        :param other_pivot: a default value, that is used as first operand for samples, where
                            only the other object has data (e.g. when the two data sets don't
                            overlap due to different lengths). If ``other_pivot`` is ``None``,
                            the data from the other object is copied.
        :param label: the string label for the computed channels
        :returns: a :class:`~sumpf.Signal` instance
        """
        return Signal(channels=function(other, self._channels, out=sumpf_internal.allocate_array(self.shape())),
                      sampling_rate=self.__sampling_rate,
                      offset=self.__offset,
                      labels=self._labels)

    def __algebra_function_signals_overlap(self, other, function, label):
        channels = sumpf_internal.allocate_array(shape=self.shape())
        function(self._channels, other.channels(), out=channels)
        return Signal(channels=channels,
                      sampling_rate=self.__sampling_rate,
                      offset=self.__offset,
                      labels=(label,) * len(self))

    def __algebra_function_self_has_one_channel(self, other, function, label):
        channels = sumpf_internal.allocate_array(shape=other.shape())
        function(self._channels[0], other.channels(), out=channels)
        return Signal(channels=channels,
                      sampling_rate=self.__sampling_rate,
                      offset=self.__offset,
                      labels=(label,) * len(other))

    def __algebra_function_other_has_one_channel(self, other, function, label):
        channels = sumpf_internal.allocate_array(shape=self.shape())
        function(self._channels, other.channels()[0], out=channels)
        return Signal(channels=channels,
                      sampling_rate=self.__sampling_rate,
                      offset=self.__offset,
                      labels=(label,) * len(self))

    def __algebra_function_different_shapes(self, other, function, other_pivot, label):
        # allocate the channels array
        start = min(self.__offset, other.offset())
        stop = max(self.__offset + self._length, other.offset() + other.length())
        length = stop - start
        channelcount = max(len(self), len(other))
        shape = (channelcount, length)
        channels = sumpf_internal.allocate_array(shape)
        # copy the two signals
        channels[:] = 0.0
        channels[0:len(self), self.__offset - start:self.__offset + self._length - start] = self._channels
        if len(self) == 1:
            for c in range(1, len(channels)):
                channels[c, self.__offset - start:self.__offset + self._length - start] = self._channels[0]
        if other_pivot is None:
            channels[0:len(other), other.offset() - start:other.offset() + other.length() - start] = other.channels()
            if len(other) == 1:
                for c in range(1, len(channels)):
                    channels[c, other.offset() - start:other.offset() + other.length() - start] = other.channels()[0]
        else:
            channel_slice = slice(other.offset() - start, other.offset() + other.length() - start)
            function(other_pivot, other.channels(), out=channels[0:len(other), channel_slice])
            if len(other) == 1:
                for c in range(1, len(channels)):
                    channels[c, channel_slice] = channels[0, channel_slice]
        # apply the function to the overlapping parts of the two signals
        overlap_start = max(self.__offset, other.offset())
        overlap_stop = min(self.__offset + self._length, other.offset() + other.length())
        if overlap_start < overlap_stop:
            if len(self._channels) == 1:
                function(self._channels[0, overlap_start - self.__offset:overlap_stop - self.__offset],
                         other.channels()[:, overlap_start - other.offset():overlap_stop - other.offset()],
                         out=channels[:, overlap_start - start:overlap_stop - start])
            elif len(other.channels()) == 1:
                function(self._channels[:, overlap_start - self.__offset:overlap_stop - self.__offset],
                         other.channels()[0, overlap_start - other.offset():overlap_stop - other.offset()],
                         out=channels[:, overlap_start - start:overlap_stop - start])
            else:
                overlap_channelcount = min(len(self), len(other))
                function(self._channels[0:overlap_channelcount,
                                        overlap_start - self.__offset:overlap_stop - self.__offset],
                         other.channels()[0:overlap_channelcount,
                                          overlap_start - other.offset():overlap_stop - other.offset()],
                         out=channels[0:overlap_channelcount, overlap_start - start:overlap_stop - start])
        # assemble and return the result signal
        return Signal(channels=channels,
                      sampling_rate=self.__sampling_rate,
                      offset=start,
                      labels=(label,) * channelcount)

    def __algebra_function_different_type(self, other, function):
        channels = sumpf_internal.allocate_array(self.shape())
        try:
            function(self._channels, other, out=channels)
        except TypeError:
            return NotImplemented
        else:
            return Signal(channels=channels,
                          sampling_rate=self.__sampling_rate,
                          offset=self.__offset,
                          labels=self._labels)

    def __convolve_with_array(self, other, other_offset, function, mode):
        shape = numpy.shape(other)
        if len(shape) == 0:     # pylint: disable=len-as-condition; this is more consistent, since the length is compared to one below
            return self.__convolve_with_scalar(other)
        elif len(shape) == 1:
            return function[mode].with_vector(matrix=self._channels,
                                              vector=other,
                                              offsets=(self.__offset, other_offset))
        elif len(other) == 1:
            return function[mode].with_vector(matrix=self._channels,
                                              vector=other[0],
                                              offsets=(self.__offset, other_offset))
        elif len(self) == 1:
            return function[mode].with_vector2(vector=self._channels[0],
                                               matrix=other,
                                               offsets=(self.__offset, other_offset))
        else:
            return function[mode].with_matrix(a=self._channels,
                                              b=other,
                                              offsets=(self.__offset, other_offset))

    def __convolve_with_scalar(self, other):
        channels = sumpf_internal.allocate_array(shape=self._channels.shape)
        numpy.multiply(self._channels, other, out=channels)
        return channels, self.__offset
