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

"""Contains the base container class for signals."""

import math
import numpy
import sumpf
import sumpf._internal as sumpf_internal
from .._sampled_data import SampledData

__all__ = ("Signal",)


class Signal(SampledData):
    """A base class for storing equidistantly sampled time data.
    This class can be instantiated directly, but SuMPF also provides sub-classes
    of this class, which can be used do generate specific signals such as sweeps
    and window functions. These sub-classes may feature additional functionality,
    that is specific for them and is therefore not comprised in this class.

    In addition to the functionality of its methods, this class has some operator
    overloads:

    * Common operators
       * checking the equality with ``==`` and ``!=``
       * slicing with ``[]``: returns a Signal instance with the selected slice.
         Slicing in SuMPF works similar to slicing in :mod:`numpy`, so passing a
         tuple with a slice for the channels and another slice for the channels
         is possible. In addition to that, the indices can also be specified as
         floats between 0.0 and 1.0, where 0.0 indices the first element in the
         array and 1.0 is mapped to the length of the array.
         For example cropping a signal to the first half of its channels and the
         second half of its samples can be done like so: ``signal[0:0.5, 0.5:]``
    * Operators for built-in functions
       * getting the length with :func:`len`: this returns the number of channels,
         just like ``len(signal.channels())`` would. To get the number of samples
         per channel, use the :meth:`~sumpf.Signal.length` method.
       * casting to a mildly informative string with :func:`str()`.
       * casting to a representation with :func:`repr()`. If :func:`~numpy.array`,
         :class:`~numpy.float64` (both from :mod:`numpy`) and :class:`~sumpf.Signal`
         (from *SuMPF*) are defined in the current name space, the signal can be
         reproduced by evaluating the representation (``eval(repr(signal))``).
         Keep in mind, that the string representation of :func:`numpy.array` does
         not include the float values with the full precision, so that the reproduced
         signal might differ slightly from the original.
       * computing the absolute of each sample with :func:`abs()`.
       * reversing the signal with :func:`reversed()`. Only the order of the samples
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

    file_formats = sumpf_internal.signal_writers.Formats    # an enumeration with file formats, whose flags can be passed to :meth:`~sumpf.Signal.save`.
    convolution_modes = sumpf_internal.ConvolutionMode      # an enumeration with modes for the :meth:`~sumpf.Signal.convolve` and :meth:`~sumpf.Signal.correlate` methods
    shift_modes = sumpf_internal.ShiftMode                  # an enumeration with modes for the :meth:`~sumpf.Signal.shift` method

    def __init__(self, channels=numpy.empty(shape=(1, 0)), sampling_rate=48000.0, offset=0, labels=None):
        """
        :param channels: a two-dimensional :func:`numpy.array` of channels with float samples
        :param sampling_rate: the sampling rate of the signal as a float or integer
        :param offset: an integer number of samples, by which the first sample of
                       the channel is delayed virtually. The offset can also be
                       negative, if the signal shall be non-causal.
        :param labels: a sequence of string labels for the channels
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
        :returns: a Signal
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
        with the built-in function :func:`str()`.

        :returns: a reasonably short string
        """
        return ("<{module}.{class_} object "
                "(length: {length}, "
                "sampling rate: {sampling_rate:.2f}, "
                "offset: {offset}, "
                "channel count: {channel_count}) "
                "at 0x{address:x}>").format(module=self.__module__,
                                            class_=self.__class__.__name__,
                                            length=self._length,
                                            sampling_rate=self.__sampling_rate,
                                            offset=self.__offset,
                                            channel_count=len(self),
                                            address=id(self))

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the signal, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        # pylint: disable=duplicate-code; this looks similar to the spectrum's __repr__ method
        if self._length:
            signal_channels = repr(self._channels).replace("\n", "").replace(" ", "")
        else:
            signal_channels = "array([[]])"
        return ("{class_}(channels={channels}, "
                "sampling_rate={sampling_rate!r}, "
                "offset={offset}, "
                "labels={labels})").format(class_=self.__class__.__name__,
                                           channels=signal_channels,
                                           sampling_rate=self.__sampling_rate,
                                           offset=self.__offset,
                                           labels=self._labels)

    def __eq__(self, other):
        """Operator overload for comparing this signal to another object with ``==``"""
        if not isinstance(other, Signal):
            return False
        elif self.__sampling_rate != other.sampling_rate():
            return False
        elif self.__offset != other.offset():
            return False
        return super().__eq__(other)

    ###################################
    # overloaded unary math operators #
    ###################################

    def __abs__(self):
        """Operator overload for computing the sample-wise absolute of the signal
        with the built-in function :func:`abs`.

        :returns: a Signal instance
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

        :returns: a Signal instance
        """
        return Signal(channels=self._channels[:, ::-1],
                      sampling_rate=self.__sampling_rate,
                      offset=self._length - self.__offset - 1,
                      labels=self._labels)

    def __neg__(self):
        """Operator overload for computing the sample-wise negative of the signal
        with ``-signal``.

        :returns: a Signal instance
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
        :returns: a Signal instance
        """
        return self._algebra_function(other=other, function=numpy.mod, other_pivot=None, label="Modulo")

    def __rmod__(self, other):
        """Right hand side Operator overload for computing the remainder of a
        division another signal, an array or number by this signal.

        :param other: a signal, an array or a number
        :returns: a Signal instance
        """
        return self._algebra_function_right(other=other, function=numpy.mod)

    #########################################
    # overloaded and misused math operators #
    #########################################

    def __invert__(self):
        """Rededicated operator overload for inverting this signal.
        Convolving a signal with its inverse results in a unit impulse. The inverse
        is computing in the frequency domain: ``ifft(1 / fft(signal))``.

        :returns: a Signal instance
        """
        channels = sumpf_internal.allocate_array(shape=self.shape())
        spectrum = numpy.fft.rfft(self._channels)
        inverse = numpy.divide(1.0, spectrum)
        channels[:] = numpy.fft.irfft(inverse)
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
            return sumpf.Signal(channels=channels,
                                sampling_rate=self.__sampling_rate,
                                offset=self.__offset,
                                labels=self._labels)

    def shift(self, shift, mode=sumpf_internal.ShiftMode.OFFSET):
        """Returns a signal, which is shifted in time.

        Positive shifts result in a delayed signal, while negative shifts prepone it.

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
        elif mode == sumpf.Signal.shift_modes.OFFSET:
            if shift is None:
                return sumpf.Signal(channels=self._channels,
                                    sampling_rate=self.__sampling_rate,
                                    offset=0,
                                    labels=self._labels)
            else:
                return sumpf.Signal(channels=self._channels,
                                    sampling_rate=self.__sampling_rate,
                                    offset=self.__offset + shift,
                                    labels=self._labels)
        else:
            if mode == sumpf.Signal.shift_modes.CROP:
                channels = sumpf_internal.allocate_array(shape=self._channels.shape)
                if shift < 0:
                    channels[:, 0:shift] = self._channels[:, -shift:]
                    channels[:, shift:] = 0.0
                else:
                    channels[:, 0:shift] = 0.0
                    channels[:, shift:] = self._channels[:, 0:-shift]
            elif mode == sumpf.Signal.shift_modes.PAD:
                channels = sumpf_internal.allocate_array(shape=(len(self), self._length + abs(shift)))
                if shift < 0:
                    channels[:, 0:self._length] = self._channels
                    channels[:, self._length:] = 0.0
                else:
                    channels[:, 0:shift] = 0.0
                    channels[:, shift:] = self._channels
            elif mode == sumpf.Signal.shift_modes.CYCLE:
                channels = sumpf_internal.allocate_array(shape=self._channels.shape)
                channels[:, 0:shift] = self._channels[:, -shift:]
                channels[:, shift:] = self._channels[:, 0:-shift]
            return sumpf.Signal(channels=channels,
                                sampling_rate=self.__sampling_rate,
                                offset=self.__offset,
                                labels=self._labels)

    #############################
    # signal processing methods #
    #############################

    def fourier_transform(self):
        """Computes the channel-wise Fourier transform of this signal.
        The offset of the signal is taken into account as a constant addition to
        the group delay.

        :returns: a :class:`~sumpf.Spectrum` instance
        """
        length = self._length // 2 + 1
        resolution = self.__sampling_rate / self._length
        channels = sumpf_internal.allocate_array(shape=(len(self._channels), length), dtype=numpy.complex128)
        spectrum = numpy.fft.rfft(self._channels)
        if self.__offset == 0:
            channels[:, :] = spectrum
        else:   # add a group delay for the offset
            delay_factor = -1j * 2.0 * math.pi * (self.__offset / self.__sampling_rate)
            frequencies = numpy.linspace(0.0, (length - 1) * resolution, length)
            phase_shift = numpy.multiply(delay_factor, frequencies)
            exp = numpy.exp(phase_shift)
            numpy.multiply(spectrum, exp, out=channels)
        return sumpf.Spectrum(channels=channels,
                              resolution=resolution,
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
        if isinstance(other, sumpf.Signal):
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
        return sumpf.Signal(channels=channels,
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
        if isinstance(other, sumpf.Signal):
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
        return sumpf.Signal(channels=channels,
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
        import scipy.stats
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
        import scipy.stats
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
        :returns: the loaded signal
        """
        return sumpf_internal.read_file(path=path,
                                        readers=sumpf_internal.signal_readers.readers,
                                        reader_base_class=sumpf_internal.signal_readers.Reader)

    def save(self, path, file_format=file_formats.AUTO):
        """Saves the signal to a file. The file will be created if it does not
        exist.

        :param path: the path to the file
        :param file_format: an optional flag from the :attr:`sumpf.Signal.file_formats`
                            enumeration, that specifies the file format, in which
                            the filter shall be stored. If this parameter is omitted
                            or set to :attr:`~sumpf.Signal.file_formats.AUTO`, the
                            format will be guessed from the ending of the filename.
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
        :returns: a Signal instance
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
        else:   # other is an array or a number
            return self.__algebra_function_different_type(other, function)

    def _algebra_function_right(self, other, function):
        """Protected helper function for overloading the right hand side operators.

        :param other: the object "on the left side of the operator"
        :param function: a function, that implements the computation for arrays (e.g. numpy.add)
        :returns: a Signal instance
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
        # apply the function to the overlapping parts of the two Signals
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
