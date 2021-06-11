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

"""Contains the base container class for spectrums"""

import math
import numpy
import sumpf
import sumpf._internal as sumpf_internal
from .._sampled_data import SampledData

__all__ = ("Spectrum",)


class Spectrum(SampledData):
    """A base class for storing equidistantly sampled frequency data.

    This class can be instantiated directly, but *SuMPF* also provides sub-classes
    of this class, which can be used do generate specific spectrums for example
    those of colored noise. These sub-classes may feature additional functionality,
    that is specific for them and is therefore not comprised in this class.

    In addition to the functionality of its methods, this class has some operator
    overloads:

    * Common operators
       * checking the equality with ``==`` and ``!=``
       * slicing with ``[]``: returns a :class:`~sumpf.Spectrum` instance with
         the selected slice. Slicing in *SuMPF* works similar to slicing in
         :mod:`numpy`, so passing a tuple with a slice for the channels and another
         slice for the channels is possible. In addition to that, the indices can
         also be specified as floats between 0.0 and 1.0, where 0.0 indices the
         first element in the array and 1.0 is mapped to the length of the array.
         For example cropping a spectrum to the first half of its channels and the
         second half of its samples can be done like so: ``spectrum[0:0.5, 0.5:]``.
         Keep in mind, that cutting away the beginning of the spectrum's channels
         offsets the spectrum, because the first sample is always considered to
         be for a frequency of 0Hz.
    * Operators for built-in functions
       * getting the length with :func:`len`: this returns the number of channels,
         just like ``len(spectrums.channels())`` would. To get the number of samples
         per channel, use the :meth:`~sumpf.Spectrum.length` method.
       * casting to a mildly informative string with :class:`str`.
       * casting to a representation with :func:`repr`. If :func:`~numpy.array`,
         :class:`~numpy.complex128` (both from :mod:`numpy`) and :class:`~sumpf.Spectrum`
         (from *SuMPF*) are defined in the current name space, the spectrum can
         be reproduced by evaluating the representation (``eval(repr(spectrum))``).
         Keep in mind, that the string representation of :mod:`numpy`'s array does
         not include the float values with the full precision, so that the reproduced
         spectrum might differ slightly from the original.
       * computing the magnitude of the spectrum with :func:`abs`.
    * Math operators
       * computing the negative of the spectrum's samples with ``-spectrum``.
       * sample-wise algebra operations with ``+``, ``-``, ``*``, ``/`` and``**``:
         These operators work with spectrums, numbers and vectorial objects such as
         arrays, tuples or lists. Broadcasting is done like in :mod:`numpy` (e.g.
         adding a single-channel spectrum to a multi-channel one, will add the channel
         of the first signal to each of the second.)
    * Rededicated operators (operators, for which Python has intended a different function than for what it is used in the :class:`~sumpf.Spectrum` class)
       * inverting the spectrum with ``~spectrum``. The inverse of a spectrum is
         simply ``1 / spectrum``.
    """

    file_formats = sumpf_internal.spectrum_writers.Formats    #: an enumeration with file formats, whose flags can be passed to :meth:`~sumpf.Spectrum.save` (see the :class:`sumpf._internal._spectrum_writers.Formats` class).

    def __init__(self, channels=numpy.empty(shape=(1, 0)), resolution=1.0, labels=None):
        """
        :param channels: a two-dimensional :func:`numpy.array` of channels with complex samples
        :param resolution: the frequency resolution of the spectrum as a float
        :param labels: a sequence of string labels for the channels
        """
        SampledData.__init__(self, channels, labels)
        self.__resolution = resolution

    ###########################################
    # overloaded operators (non math-related) #
    ###########################################

    def __getitem__(self, key):
        """Operator overload for slicing the spectrum.

        :param key: an index, a slice or a tuple of indices or slices. Indices may
                    be integers or floats between 0.0 and 1.0.
        :returns: a :class:`~sumpf.Spectrum` instance
        """
        slices = sumpf_internal.key_to_slices(key, self._channels.shape)
        if isinstance(slices, tuple):
            c = slices[0]
        else:
            c = slices
        return Spectrum(channels=self._channels[slices],
                        resolution=self.__resolution,
                        labels=self._labels[c])

    def __str__(self):
        """Operator overload for generating a short description of the spectrum
        with the built-in function :class:`str`.

        :returns: a reasonably short string
        """
        return (f"<{self.__module__}.{self.__class__.__name__} object "
                f"(length: {self._length}, "
                f"resolution: {self.__resolution:.2f}, "
                f"channel count: {len(self)}) "
                f"at 0x{id(self):x}>")

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the spectrum, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        channels = numpy.array2string(self._channels,
                                      separator=",",
                                      formatter={"all": repr},
                                      threshold=self._channels.size).replace("\n", "").replace(" ", "")
        return (f"{self.__class__.__name__}(channels=array({channels}), "
                f"resolution={self.__resolution!r}, "
                f"labels={self._labels})")

    def __eq__(self, other):
        """Operator overload for comparing this spectrum to another object with ``==``"""
        if not isinstance(other, Spectrum):
            return False
        elif self.__resolution != other.resolution():
            return False
        return super().__eq__(other)

    def __hash__(self):
        """Operator overload for computing the hash of this spectrum with :func:`hash`"""
        return hash((super().__hash__(), self.__resolution))

    ###################################
    # overloaded unary math operators #
    ###################################

    def __abs__(self):
        """Operator overload for computing the magnitude of the spectrum with the
        built-in function :func:`abs`.

        :returns: a :class:`~sumpf.Spectrum` instance
        """
        return Spectrum(channels=numpy.absolute(self._channels, out=sumpf_internal.allocate_array(self.shape())),
                        resolution=self.__resolution,
                        labels=self._labels)

    def __neg__(self):
        """Operator for inverting the phase of the spectrum with ``-spectrum``.

        :returns: a :class:`~sumpf.Spectrum` instance
        """
        return Spectrum(channels=numpy.negative(self._channels, out=sumpf_internal.allocate_array(self.shape(),
                                                                                                  numpy.complex128)),
                        resolution=self.__resolution,
                        labels=self._labels)

    ####################################
    # overloaded binary math operators #
    ####################################

    def _algebra_function(self, other, function, other_pivot, label):
        """Protected helper function that implements the broadcasting of spectrums
        or arrays with different shapes when using the overloaded math operators.

        :param other: the object "on the other side of the operator"
        :param function: a function, that implements the computation for arrays (e.g. numpy.add)
        :param other_pivot: a default value, that is used as first operand for samples, where
                            only the other object has data (e.g. when the two spectrums don't
                            overlap due to different lengths). If ``other_pivot`` is ``None``,
                            the data from the other object is copied.
        :param label: the string label for the computed channels
        :returns: a :class:`~sumpf.Spectrum` instance
        """
        if isinstance(other, Spectrum):
            if len(self) == 1:
                channels = sumpf_internal.allocate_array(shape=(len(other), self._length), dtype=numpy.complex128)
                function(self._channels[0], other.channels(), out=channels)
            elif len(other) == 1:
                channels = sumpf_internal.allocate_array(shape=self.shape(), dtype=numpy.complex128)
                function(self._channels, other.channels()[0], out=channels)
            elif len(self) < len(other):
                channels = sumpf_internal.allocate_array(shape=(len(other), self._length), dtype=numpy.complex128)
                function(self._channels, other.channels()[0:len(self)], out=channels[0:len(self)])
                if other_pivot is None:
                    channels[len(self):] = other.channels()[len(self):]
                else:
                    function(other_pivot, other.channels()[len(self):], out=channels[len(self):])
            else:
                channels = sumpf_internal.allocate_array(shape=self.shape(), dtype=numpy.complex128)
                function(self._channels[0:len(other)], other.channels(), out=channels[0:len(other)])
                channels[len(other):] = self._channels[len(other):]
            return Spectrum(channels=channels, resolution=self.__resolution, labels=(label,) * len(channels))
        elif isinstance(other, (SampledData, sumpf.Filter)):
            return NotImplemented
        else:   # other is an array or a number
            try:
                return Spectrum(channels=function(self._channels,
                                                  other,
                                                  out=sumpf_internal.allocate_array(self.shape(), numpy.complex128)),
                                resolution=self.__resolution,
                                labels=self._labels)
            except TypeError:
                return NotImplemented

    def _algebra_function_right(self, other, function, other_pivot, label):
        """Protected helper function for overloading the right hand side operators.

        :param other: the object "on the left side of the operator"
        :param function: a function, that implements the computation for arrays (e.g. numpy.add)
        :param other_pivot: a default value, that is used as first operand for samples, where
                            only the other object has data (e.g. when the two spectrums don't
                            overlap due to different lengths). If ``other_pivot`` is ``None``,
                            the data from the other object is copied.
        :param label: the string label for the computed channels
        :returns: a :class:`~sumpf.Spectrum` instance
        """
        return Spectrum(channels=function(other,
                                          self._channels,
                                          out=sumpf_internal.allocate_array(self.shape(), numpy.complex128)),
                        resolution=self.__resolution,
                        labels=self._labels)

    #########################################
    # overloaded and misused math operators #
    #########################################

    def __invert__(self):
        """Rededicated operator overload for inverting this spectrum.
        The inverse of a spectrum is simply ``1 / spectrum``.

        :returns: a :class:`~sumpf.Spectrum` instance
        """
        return Spectrum(channels=numpy.divide(1.0,
                                              self._channels,
                                              out=sumpf_internal.allocate_array(self.shape(), numpy.complex128)),
                        resolution=self.__resolution,
                        labels=self._labels)

    #######################################################
    # parameters, that have been set with the constructor #
    #######################################################

    def resolution(self):
        """Returns the resolution of this spectrum.

        :returns: a float
        """
        return self.__resolution

    ######################
    # derived parameters #
    ######################

    def maximum_frequency(self):
        """Returns the maximum frequency of this spectrum in Hz.

        :returns: a float
        """
        return (self._length - 1) * self.__resolution

    def magnitude(self):
        """Returns the magnitude of this spectrum's channels.

        This method returns an array rather than a :class:`~sumpf.Spectrum`
        instance like ``abs(spectrum)``.

        :returns: a :func:`numpy.array`
        """
        return numpy.absolute(self._channels)

    def phase(self):
        """Returns the phase of this spectrum's channels.

        :returns: a :func:`numpy.array`
        """
        return numpy.angle(self._channels)

    def real(self):
        """Returns the real part of this spectrum's channels.

        :returns: a :func:`numpy.array`
        """
        return numpy.real(self._channels)

    def imaginary(self):
        """Returns the imaginary part of this spectrum's channels.

        :returns: a :func:`numpy.array`
        """
        return numpy.imag(self._channels)

    #######################
    # convenience methods #
    #######################

    def frequency_samples(self):
        """Returns an array with the frequency samples for each sample of the spectrum's channels.

        :returns: a one dimensional :func:`numpy.array`
        """
        return numpy.linspace(0.0, self.maximum_frequency(), self._length)

    def pad(self, length, value=0.0):
        """Returns a spectrum with the given length, which is achieved by either
        cropping or appending the given value.

        :param length: the length of the resulting spectrum
        :param value: the value with which the spectrum shall be padded
        :returns: a padded or cropped :class:`~sumpf.Spectrum`
        """
        if length == self._length:
            return self
        else:
            channels = sumpf_internal.allocate_array(shape=(len(self), length), dtype=numpy.complex128)
            if length < self._length:
                channels[:] = self._channels[:, 0:length]
            else:
                channels[:, 0:self._length] = self._channels
                channels[:, self._length:] = value
            return Spectrum(channels=channels,
                            resolution=self.__resolution,
                            labels=self._labels)

    def conjugate(self):
        """Returns a spectrum with the complex conjugate of this spectrum's channels.

        :returns: a :class:`~sumpf.Spectrum`
        """
        channels = sumpf_internal.allocate_array(shape=self.shape(), dtype=numpy.complex128)
        numpy.conjugate(self._channels, out=channels)
        return Spectrum(channels=channels, resolution=self.__resolution, labels=self._labels)

    #############################
    # signal processing methods #
    #############################

    def inverse_fourier_transform(self):
        """Computes the channel-wise inverse Fourier transform of this spectrum.

        :returns: a :class:`~sumpf.Signal` instance
        """
        if self._length == 0:
            return sumpf.Signal(channels=numpy.empty(shape=(len(self), 0)),
                                sampling_rate=0.0,
                                offset=0,
                                labels=self._labels)
        length = max(1, (self._length - 1) * 2)
        sampling_rate = self.__resolution * length
        channels = sumpf_internal.allocate_array(shape=(len(self._channels), length))
        channels[:, :] = numpy.fft.irfft(self._channels, n=length)
        return sumpf.Signal(channels=channels,
                            sampling_rate=sampling_rate,
                            offset=0,
                            labels=self._labels)

    def level(self, single_value=False):
        """Computes the root-mean-square-level of the spectrum's channels.

        :param single_value: if False, an :func:`~numpy.array` with the level of
                             each channel is returned, otherwise a single value
                             for some sort of "total spectrum level" is computed,
                             which is the same as the level of the concatenation
                             of all channels
        :returns: an :func:`~numpy.array` or a float
        """
        signal_length = max(1, (self._length - 1) * 2)
        abs_ = numpy.abs(self._channels)
        square = numpy.square(abs_, out=abs_)
        if single_value:
            sum_ = math.fsum(math.fsum((math.fsum(c[1:-1]) * 2, c[0], c[-1])) for c in square)
            return math.sqrt(sum_ / len(self)) / signal_length
        else:
            return numpy.fromiter((math.sqrt(math.fsum((math.fsum(c[1:-1]) * 2, c[0], c[-1]))) / signal_length for c in square),    # pylint: disable=line-too-long; don't know where to break without making the readability even worse
                                  dtype=numpy.float64)

    #######################
    # persistence methods #
    #######################

    @staticmethod
    def load(path):
        """A static method to load a :class:`~sumpf.Spectrum` instance from a file.

        :param path: the path to the file.
        :returns: the loaded :class:`~sumpf.Spectrum`
        """
        return sumpf_internal.read_file(path=path,
                                        readers=sumpf_internal.spectrum_readers.readers,
                                        reader_base_class=sumpf_internal.spectrum_readers.Reader)

    def save(self, path, file_format=file_formats.AUTO):
        """Saves the spectrum to a file. The file will be created if it does not
        exist.

        :param path: the path to the file
        :param file_format: an optional flag from the :attr:`sumpf.Spectrum.file_formats`
                            enumeration, that specifies the file format, in which
                            the spectrum shall be stored. If this parameter is omitted
                            or set to :attr:`~sumpf.Spectrum.file_formats`.\ ``AUTO``,
                            the format will be guessed from the ending of the filename.
        :returns: self
        """
        writer = sumpf_internal.get_writer(file_format=file_format,
                                           writers=sumpf_internal.spectrum_writers.writers,
                                           writer_base_class=sumpf_internal.spectrum_writers.Writer)
        writer(self, path)
        return self
