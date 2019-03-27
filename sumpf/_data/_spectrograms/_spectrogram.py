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

"""Contains the container class for spectrograms."""

import numpy
import sumpf
import sumpf._internal as sumpf_internal
from .._sampled_data import SampledData

__all__ = ("Spectrogram",)


class Spectrogram(SampledData):
    """A base class for storing data, that is equidistantly sampled over time
    and frequency.

    The data of a spectrogram is three-dimensional and complex-valued:

    1. the first index selects the channel
    2. the second index selects the frequency bin
    3. the third index selects the time sample

    In addition to the functionality of its methods, this class has some operator
    overloads:

    * Common operators
       * checking the equality with ``==`` and ``!=``
       * slicing with ``[]``: returns a :class:`~sumpf.Spectrogram` instance with
         the selected slice. Slicing in *SuMPF* works similar to slicing in
         :mod:`numpy`, so passing a tuple with a slice for the channels and another
         slice for the channels is possible. In addition to that, the indices can
         also be specified as floats between 0.0 and 1.0, where 0.0 indices the
         first element in the array and 1.0 is mapped to the length of the array.
         For example cropping a spectrogram to the first half of its channels and the
         second half of its time samples can be done like so: ``spectrogram[0:0.5, :, 0.5:]``
    * Operators for built-in functions
       * getting the length with :func:`len`: this returns the number of channels,
         just like ``len(spectrogram.channels())`` would. To get the number of
         frequency bins per channel, use the :meth:`~sumpf.Spectrogram.number_of_frequencies`
         method. To get the number of time samples per bin, use the :meth:`~sumpf.Spectrogram.length`
         method.
       * casting to a mildly informative string with :class:`str`.
       * casting to a representation with :func:`repr`. If :func:`~numpy.array`,
         :class:`~numpy.complex128` (both from :mod:`numpy`) and :class:`~sumpf.Spectrogram`
         (from *SuMPF*) are defined in the current name space, the spectrogram can
         be reproduced by evaluating the representation (``eval(repr(spectrogram))``).
         Keep in mind, that the string representation of :func:`numpy.array` does
         not include the float values with the full precision, so that the reproduced
         spectrogram might differ slightly from the original.
       * computing the absolute of each sample with :func:`abs`.
    * Math operators
       * computing the negative of the spectrogram's samples with ``-signal``.
       * sample-wise algebra operations with ``+``, ``-``, ``*``, ``/``, and ``**``:
         These operators work with signals, numbers and vectorial objects such as
         arrays, tuples or lists. Broadcasting is done like in :mod:`numpy` (e.g.
         adding a single-channel spectrogram to a multi-channel one, will add the channel
         of the first spectrogram to each of the second.)
    """
    file_formats = sumpf_internal.spectrogram_writers.Formats   #: an enumeration with file formats, whose flags can be passed to :meth:`~sumpf.Spectrogram.save` (see the :class:`sumpf._internal._spectrogram_writers.Formats` class).
    shift_modes = sumpf_internal.ShiftMode                      #: an enumeration with modes for the :meth:`~sumpf.Spectrogram.shift` method (see the :class:`~sumpf._internal._enums.ShiftMode` class).

    def __init__(self,
                 channels=numpy.empty(shape=(1, 1, 0)),
                 resolution=1.0,
                 sampling_rate=48000.0,
                 offset=0,
                 labels=None):
        """
        :param channels: a three-dimensional :func:`numpy.array` of channels with complex samples
        :param resolution: the resolution of the spectrogram's frequency bins as a float
        :param sampling_rate: the sampling rate of the time samples as a float or integer
        :param offset: an integer number of samples, by which the first sample of
                       the channel is delayed virtually. The offset can also be
                       negative, if the spectrogram shall be non-causal.
        :param labels: a sequence of string labels for the channels
        """
        SampledData.__init__(self, channels, labels)
        self.__resolution = resolution
        self.__sampling_rate = sampling_rate
        self.__offset = offset
        self.__frequencies = channels.shape[1]

    ###########################################
    # overloaded operators (non math-related) #
    ###########################################

    def __getitem__(self, key):
        """Operator overload for slicing the spectrogram.

        :param key: an index, a slice or a tuple of indices or slices. Indices may
                    be integers or floats between 0.0 and 1.0.
        :returns: a Spectrogram
        """
        slices = sumpf_internal.key_to_slices(key, self._channels.shape)
        offset = self.__offset
        if isinstance(slices, tuple):
            if len(slices) == 3:
                if slices[2].start:
                    if slices[2].start < 0:
                        offset += self._length + slices[2].start
                    else:
                        offset += slices[2].start
            c = slices[0]
        else:
            c = slices
        return Spectrogram(channels=self._channels[slices],
                           resolution=self.__resolution,
                           sampling_rate=self.__sampling_rate,
                           offset=offset,
                           labels=self._labels[c])

    def __str__(self):
        """Operator overload for generating a short description of the spectrogram
        with the built-in function :class:`str`.

        :returns: a reasonably short string
        """
        return (f"<{self.__module__}.{self.__class__.__name__} object "
                f"(shape: {self._channels.shape}, "
                f"resolution: {self.__resolution:.2f}, "
                f"sampling rate: {self.__sampling_rate:.2f}, "
                f"offset: {self.__offset}, "
                f"at 0x{id(self):x}>")

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the spectrogram, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        if self._length:
            channels = repr(self._channels).replace("\n", "").replace(" ", "")
        else:
            channels = "array([[[]]])"
        return (f"{self.__class__.__name__}(channels={channels}, "
                f"resolution={self.__resolution}, "
                f"sampling_rate={self.__sampling_rate!r}, "
                f"offset={self.__offset}, "
                f"labels={self._labels})")

    def __eq__(self, other):
        """Operator overload for comparing this spectrogram to another object with ``==``"""
        if not isinstance(other, Spectrogram):
            print("not a spectrogram")
            return False
        elif self.__resolution != other.resolution():
            print("wrong resolution")
            return False
        elif self.__sampling_rate != other.sampling_rate():
            print("wrong sampling rate")
            return False
        elif self.__offset != other.offset():
            print("wrong offset")
            return False
        return super().__eq__(other)

    def __hash__(self):
        """Operator overload for computing the hash of this spectrogram with :func:`hash`"""
        return hash((super().__hash__(), self.__resolution, self.__sampling_rate, self.__offset))

    ###################################
    # overloaded unary math operators #
    ###################################

    def __abs__(self):
        """Operator overload for computing the magnitude of the spectrogram with
        the built-in function :func:`abs`.

        :returns: a :class:`sumpf.Spectrogram` instance
        """
        return Spectrogram(channels=numpy.absolute(self._channels, out=sumpf_internal.allocate_array(self.shape())),
                           resolution=self.__resolution,
                           sampling_rate=self.__sampling_rate,
                           offset=self.__offset,
                           labels=self._labels)

    def __neg__(self):
        """Operator for inverting the phase of the spectrogram with ``-spectrogram``.

        :returns: a :class:`sumpf.Spectrogram` instance
        """
        channels = sumpf_internal.allocate_array(shape=self.shape(), dtype=numpy.complex128)
        numpy.negative(self._channels, out=channels)
        return Spectrogram(channels=channels,
                           resolution=self.__resolution,
                           sampling_rate=self.__sampling_rate,
                           offset=self.__offset,
                           labels=self._labels)

    #######################################################
    # parameters, that have been set with the constructor #
    #######################################################

    def number_of_frequencies(self):
        """Returns the number of frequency bins of this spectrogram.

        :returns: an integer
        """
        return self.__frequencies

    def resolution(self):
        """Returns the frequency resolution of this spectrogram.

        :returns: a float
        """
        return self.__resolution

    def sampling_rate(self):
        """Returns the sampling rate of this spectrogram.

        :returns: a number
        """
        return self.__sampling_rate

    def offset(self):
        """Returns the offset of this spectrogram.
        Positive offsets mean, that the spectrogram is delayed by that number of
        samples, while signals with negative offsets are preponed.
        The time value for the first sample in the channels is ``offset / sampling_rate``

        :returns: an integer
        """
        return self.__offset

    ######################
    # derived parameters #
    ######################

    def maximum_frequency(self):
        """Returns the maximum frequency of this spectrogram in Hz.

        :returns: a float
        """
        return (self.__frequencies - 1) * self.__resolution

    def duration(self):
        """Returns the duration of this spectrogram in seconds.

        :returns: a float
        """
        return self._length / self.__sampling_rate

    def magnitude(self):
        """Returns the magnitude of this spectrogram's channels.

        This method returns an array rather than a :class:`sumpf.Spectrogram`
        instance like ``abs(spectrogram)``.

        :returns: a :func:`numpy.array`
        """
        return numpy.absolute(self._channels)

    def phase(self):
        """Returns the phase of this spectrogram's channels.

        :returns: a :func:`numpy.array`
        """
        return numpy.angle(self._channels)

    def real(self):
        """Returns the real part of this spectrogram's channels.

        :returns: a :func:`numpy.array`
        """
        return numpy.real(self._channels)

    def imaginary(self):
        """Returns the imaginary part of this spectrogram's channels.

        :returns: a :func:`numpy.array`
        """
        return numpy.imag(self._channels)

    #######################
    # convenience methods #
    #######################

    def frequency_samples(self):
        """Returns an array with the frequency samples for each sample of the spectrogram's channels.

        :returns: a one dimensional :func:`numpy.array`
        """
        return numpy.linspace(0.0, self.maximum_frequency(), self.__frequencies)

    def time_samples(self):
        """Returns an array with the time samples for each sample of the spectrogram's channels.

        :returns: a one dimensional :func:`numpy.array`
        """
        return numpy.linspace(self.__offset / self.__sampling_rate,
                              (self._length + self.__offset - 1) / self.__sampling_rate,
                              self._length)

    def pad(self, length, value=0.0):
        """Returns a spectrogram with the given length, which is achieved by either
        cropping or appending the given value to the time series.

        :param length: the length of the resulting spectrogram
        :param value: the value with which the spectrogram shall be padded
        :returns: the padded or cropped :class:`~sumpf.Spectrogram`
        """
        if length == self._length:
            return self
        else:
            channels = sumpf_internal.allocate_array(shape=(len(self), self.__frequencies, length),
                                                     dtype=numpy.complex128)
            if length < self._length:
                channels[:] = self._channels[:, :, 0:length]
            else:
                channels[:, :, 0:self._length] = self._channels
                channels[:, :, self._length:] = value
            return Spectrogram(channels=channels,
                               resolution=self.__resolution,
                               sampling_rate=self.__sampling_rate,
                               offset=self.__offset,
                               labels=self._labels)

    def shift(self, shift, mode=sumpf_internal.ShiftMode.OFFSET):
        """Returns a spectrogram, which is shifted in time.

        Positive shifts result in a delayed spectrogram, while negative shifts prepone it.
        In mode ``OFFSET``, it is allowed to pass ``None`` for the ``shift`` parameter,
        which sets the offset of the resulting :class:`~sumpf.Spectrogram` to 0.

        The shift can be performed in different ways, which can be specified with
        the ``mode`` parameter. The flags, that can be passed to this parameter
        are defined and documented in the :class:`sumpf.Spectrogram.shift_modes`
        enumeration.

        :param shift: an integer number of samples, by which the spectrogram shall be shifted
        :param mode: a flag from the :class:`sumpf.Spectrogram.shift_modes` enumeration
        :returns: the shifted :class:`~sumpf.Spectrogram`
        """
        if shift == 0:
            return self
        elif mode == Spectrogram.shift_modes.OFFSET:
            if shift is None:
                return Spectrogram(channels=self._channels,
                                   resolution=self.__resolution,
                                   sampling_rate=self.__sampling_rate,
                                   offset=0,
                                   labels=self._labels)
            else:
                return Spectrogram(channels=self._channels,
                                   resolution=self.__resolution,
                                   sampling_rate=self.__sampling_rate,
                                   offset=self.__offset + shift,
                                   labels=self._labels)
        else:
            if mode == Spectrogram.shift_modes.CROP:
                channels = sumpf_internal.allocate_array(shape=self._channels.shape, dtype=numpy.complex128)
                if shift < 0:
                    channels[:, :, 0:shift] = self._channels[:, :, -shift:]
                    channels[:, :, shift:] = 0.0
                else:
                    channels[:, :, 0:shift] = 0.0
                    channels[:, :, shift:] = self._channels[:, :, 0:-shift]
            elif mode == Spectrogram.shift_modes.PAD:
                channels = sumpf_internal.allocate_array(shape=(len(self),
                                                                self.__frequencies,
                                                                self._length + abs(shift)),
                                                         dtype=numpy.complex128)
                if shift < 0:
                    channels[:, :, 0:self._length] = self._channels
                    channels[:, :, self._length:] = 0.0
                else:
                    channels[:, :, 0:shift] = 0.0
                    channels[:, :, shift:] = self._channels
            elif mode == Spectrogram.shift_modes.CYCLE:
                channels = sumpf_internal.allocate_array(shape=self._channels.shape, dtype=numpy.complex128)
                channels[:, :, 0:shift] = self._channels[:, :, -shift:]
                channels[:, :, shift:] = self._channels[:, :, 0:-shift]
            return Spectrogram(channels=channels,
                               resolution=self.__resolution,
                               sampling_rate=self.__sampling_rate,
                               offset=self.__offset,
                               labels=self._labels)

    def conjugate(self):
        """Returns a spectrogram with the complex conjugate of this spectrogram's channels.

        :returns: a :class:`sumpf.Spectrogram`
        """
        channels = sumpf_internal.allocate_array(shape=self.shape(), dtype=numpy.complex128)
        numpy.conjugate(self._channels, out=channels)
        return Spectrogram(channels=channels,
                           resolution=self.__resolution,
                           sampling_rate=self.__sampling_rate,
                           offset=self.__offset,
                           labels=self._labels)

    #############################
    # signal processing methods #
    #############################

    def inverse_short_time_fourier_transform(self, window=4096, overlap=0.5, pad=True):
        """Computes a :class:`~sumpf.Signal` from this spectrogram.

        This method requires :mod:`scipy` to be installed.

        :param window: the window function, that was used to compute this spectrogram.
                       It can be passed as a :class:`~sumpf.Signal`, as an iterable
                       or an integer window length. See :func:`~sumpf._internal._functions.get_window`
                       for details.
        :param overlap: the overlap of the windowed segments. It can be passed as
                        an integer number of samples or a float fraction of the
                        window's length. Negative numbers will be added to the
                        window's length.
        :param pad: True, if the signal was padded with zeros to fit an integer
                    number of segments. False, if the samples at the end of the
                    signal, that did not fit a full segment, were ignored.
                    The results when setting this to False may be unexpected...
        """
        import scipy.signal
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
            istft = scipy.signal.istft(self._channels,
                                       fs=self.__sampling_rate,
                                       window=window.channels()[0],
                                       nperseg=window_length,
                                       noverlap=overlap,
                                       boundary=pad)[1]
        else:
            istft = []
            for c, w in zip(self._channels, window.channels()):
                istft.append(scipy.signal.istft(c,
                                                fs=self.__sampling_rate,
                                                window=w,
                                                nperseg=window_length,
                                                noverlap=overlap,
                                                boundary=pad)[1])
        channels = sumpf_internal.allocate_array(shape=numpy.shape(istft))
        channels[:] = istft
        # return the spectrogram
        return sumpf.Signal(channels=channels,
                            sampling_rate=self.__sampling_rate * step,
                            offset=self.__offset * step,
                            labels=self._labels)

    #######################
    # persistence methods #
    #######################

    @staticmethod
    def load(path):
        """A static method to load a :class:`~sumpf.Spectrogram` instance from a file.

        :param path: the path to the file.
        :returns: the loaded :class:`~sumpf.Spectrogram`
        """
        return sumpf_internal.read_file(path=path,
                                        readers=sumpf_internal.spectrogram_readers.readers,
                                        reader_base_class=sumpf_internal.spectrogram_readers.Reader)

    def save(self, path, file_format=file_formats.AUTO):
        """Saves the spectrogram to a file. The file will be created if it does
        not exist.

        :param path: the path to the file
        :param file_format: an optional flag from the :attr:`sumpf.Spectrogram.file_formats`
                            enumeration, that specifies the file format, in which
                            the spectrogram shall be stored. If this parameter is omitted
                            or set to :attr:`~sumpf.Spectrogram.file_formats`.\ ``AUTO``,
                            the format will be guessed from the ending of the filename.
        :returns: self
        """
        writer = sumpf_internal.get_writer(file_format=file_format,
                                           writers=sumpf_internal.spectrogram_writers.writers,
                                           writer_base_class=sumpf_internal.spectrogram_writers.Writer)
        writer(self, path)
        return self

    ########################################################################
    # private helper methods for implementing math related functionalities #
    ########################################################################

    def _algebra_function(self, other, function, other_pivot, label):
        """Protected helper function that implements the broadcasting of spectrograms
        or arrays with different shapes when using the overloaded math operators.

        :param other: the object "on the other side of the operator"
        :param function: a function, that implements the computation for arrays (e.g. numpy.add)
        :param other_pivot: a default value, that is used as first operand for
                            samples, where only the other object has data (e.g.
                            when the two spectrograms don't overlap due to offsets).
                            If ``other_pivot`` is ``None``, the data from the other
                            object is copied.
        :param label: the string label for the computed channels
        :returns: a :class:`~sumpf.Spectrogram` instance
        """
        if isinstance(other, Spectrogram):
            if len(self) == len(other) and \
               self.__frequencies == other.number_of_frequencies() and \
               self._length == other.length() and \
               self.__offset == other.offset():
                # both spectrograms overlap completely
                return self.__algebra_function_spectrograms_overlap(other, function, label)
            elif (len(self) == 1 and
                  self.__frequencies == other.number_of_frequencies() and
                  self._length == other.length() and
                  self.__offset == other.offset()):
                # both spectrograms have the same length and offset, but this
                # spectrogram has only one channel, so that the computation combines
                # this channel with each of the other spectrogram's channels
                return self.__algebra_function_self_has_one_channel(other, function, label)
            elif (len(other) == 1 and
                  self.__frequencies == other.number_of_frequencies() and
                  self._length == other.length() and
                  self.__offset == other.offset()):
                # both spectrograms have the same length and offset, but the other
                # spectrograms has only one channel, so that the computation combines
                # this channel with each of this spectrogram's channels
                return self.__algebra_function_other_has_one_channel(other, function, label)
            else:
                # the spectrograms have different shapes or offsets, which makes things complicated
                return self.__algebra_function_different_shapes(other, function, other_pivot, label)
        else:
            # other is an array or a number
            return self.__algebra_function_different_type(other, function)

    def _algebra_function_right(self, other, function):
        """Protected helper function for overloading the right hand side operators.

        :param other: the object "on the left side of the operator"
        :param function: a function, that implements the computation for arrays (e.g. numpy.add)
        :returns: a :class:`~sumpf.Signal` instance
        """
        channels = sumpf_internal.allocate_array(shape=self.shape(), dtype=numpy.complex128)
        try:
            function(other, self._channels, out=channels)
        except TypeError:
            return NotImplemented
        else:
            return Spectrogram(channels=channels,
                               resolution=self.__resolution,
                               sampling_rate=self.__sampling_rate,
                               offset=self.__offset,
                               labels=self._labels)

    def __algebra_function_spectrograms_overlap(self, other, function, label):
        channels = sumpf_internal.allocate_array(shape=self.shape(), dtype=numpy.complex128)
        function(self._channels, other.channels(), out=channels)
        return Spectrogram(channels=channels,
                           resolution=self.__resolution,
                           sampling_rate=self.__sampling_rate,
                           offset=self.__offset,
                           labels=(label,) * len(self))

    def __algebra_function_self_has_one_channel(self, other, function, label):
        channels = sumpf_internal.allocate_array(shape=other.shape(), dtype=numpy.complex128)
        function(self._channels[0], other.channels(), out=channels)
        return Spectrogram(channels=channels,
                           resolution=self.__resolution,
                           sampling_rate=self.__sampling_rate,
                           offset=self.__offset,
                           labels=(label,) * len(self))

    def __algebra_function_other_has_one_channel(self, other, function, label):
        channels = sumpf_internal.allocate_array(shape=self.shape(), dtype=numpy.complex128)
        function(self._channels, other.channels()[0], out=channels)
        return Spectrogram(channels=channels,
                           resolution=self.__resolution,
                           sampling_rate=self.__sampling_rate,
                           offset=self.__offset,
                           labels=(label,) * len(self))

    def __algebra_function_different_shapes(self, other, function, other_pivot, label):     # pylint: disable=too-many-locals; having all those index variables is more readable than computing them inside the []-braces
        # allocate the channels array
        start = min(self.__offset, other.offset())
        stop = max(self.__offset + self._length, other.offset() + other.length())
        length = stop - start
        frequencies = max(self.__frequencies, other.number_of_frequencies())
        channelcount = max(len(self), len(other))
        shape = (channelcount, frequencies, length)
        channels = sumpf_internal.allocate_array(shape=shape, dtype=numpy.complex128)
        # compute a few indices to make the slicing more readable
        sc = len(self)
        sf = self.__frequencies
        sa = self.__offset - start
        sb = sa + self._length
        oc = len(other)
        of = other.number_of_frequencies()
        oa = other.offset() - start
        ob = oa + other.length()
        # copy the two signals
        channels[:] = 0.0
        channels[0:sc, 0:sf, sa:sb] = self._channels
        if sc == 1:
            for c in range(1, channelcount):
                channels[c, 0:sf, sa:sb] = self._channels[0]
        if other_pivot is None:
            channels[0:oc, 0:of, oa:ob] = other.channels()
            if oc == 1:
                for c in range(1, channelcount):
                    channels[c, 0:of, oa:ob] = other.channels()[0]
        else:
            function(other_pivot, other.channels(), out=channels[0:oc, 0:of, oa:ob])
            if oc == 1:
                for c in range(1, channelcount):
                    channels[c, 0:of, oa:ob] = channels[0, 0:of, oa:ob]
        # apply the function to the overlapping parts of the two Signals
        bc = min(len(self), len(other))
        bf = min(self.__frequencies, other.number_of_frequencies())
        ba = max(self.__offset, other.offset()) - start
        bb = min(self.__offset + self._length, other.offset() + other.length()) - start
        sx = ba + start - self.__offset
        sy = bb + start - self.__offset
        ox = ba + start - other.offset()
        oy = bb + start - other.offset()
        if bf and ba < bb:
            if sc == 1:
                function(self._channels[0, 0:bf, sx:sy],
                         other.channels()[:, 0:bf, ox:oy],
                         out=channels[:, 0:bf, ba:bb])
            elif len(other.channels()) == 1:
                function(self._channels[:, 0:bf, sx:sy],
                         other.channels()[0, 0:bf, ox:oy],
                         out=channels[:, 0:bf, ba:bb])
            else:
                function(self._channels[0:bc, 0:bf, sx:sy],
                         other.channels()[0:bc, 0:bf, ox:oy],
                         out=channels[0:bc, 0:bf, ba:bb])
        # assemble and return the result signal
        return Spectrogram(channels=channels,
                           resolution=self.__resolution,
                           sampling_rate=self.__sampling_rate,
                           offset=start,
                           labels=(label,) * channelcount)

    def __algebra_function_different_type(self, other, function):
        channels = sumpf_internal.allocate_array(shape=self.shape(), dtype=numpy.complex128)
        try:
            function(self._channels, other, out=channels)
        except TypeError:
            return NotImplemented
        else:
            return Spectrogram(channels=channels,
                               resolution=self.__resolution,
                               sampling_rate=self.__sampling_rate,
                               offset=self.__offset,
                               labels=self._labels)
