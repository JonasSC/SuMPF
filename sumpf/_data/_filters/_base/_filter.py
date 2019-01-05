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

"""Contains the base container class for signals"""

import numpy
import sumpf
import sumpf._internal as sumpf_internal
from ._s import S
from . import _terms as terms
from . import _persistence as persistence

__all__ = ("Filter",)


class Filter:
    """A base class for defining transfer functions of filters.
    Other than Spectrum instances, which contain sampled data, Filter instances
    contain a mathematical description of the filter's spectrum.

    This class can be instantiated directly, but SuMPF also provides sub-classes
    of this class, which can be used do generate specific filters like Butterworth
    filters or weighting functions. These sub-classes may feature additional
    functionality, that is specific for them and is therefore not comprised in
    this class.

    A filter's transfer functions are constructed from terms, that are provided
    as static attributes of the Filter class:

    * :attr:`~Filter.Constant` defines a constant value, which it expects as
      constructor parameter
    * :attr:`~Filter.Polynomial` defines a polynomial of the frequency variable
      ``s = 2j * pi * f``. It expects a sequence of polynomial coefficients as
      constructor parameter, where the first coefficient is that of the highest
      power of ``s``.
    * :attr:`~Filter.Exp` defines an exponential function with the multiplication
      of ``s`` and a coefficient in the exponent. The coefficient can be passed
      as constructor parameter.
    * :attr:`~Filter.Absolute` defines the absolute value (magnitude) of the term,
      that it gets passed as constructor parameter.
    * :attr:`~Filter.Negative` defines the negative (inverted phase) of the term,
      that it gets passed as constructor parameter.
    * :attr:`~Filter.Sum` defines the sum of all terms, that it gets passed in a
      sequence as constructor parameter.
    * :attr:`~Filter.Difference` defines the difference of the two terms, that
      it gets passed as constructor parameters.
    * :attr:`~Filter.Product` defines the product of all terms, that it gets passed
      in a sequence as constructor parameter.
    * :attr:`~Filter.Quotient` defines the quotient of the two terms, that it
      gets passed as constructor parameters.

    All terms' constructors accept a boolean parameter ``transform``, which, if
    ``True``, enables a lowpass-to-highpass transform, that replaces ``s`` with
    ``1 / s`` during the computation of the term. In order to avoid zero division
    errors, transformed terms are not evaluated at a frequency of 0 and their result
    is set to 0 for this frequency.

    The terms have operator overloads for ``+``, ``-``, ``*``, ``/``, :func:`abs`,
    ``-term`` and ``~term`` (``1 / term``), so it is not necessary to instantiate
    all terms manually. For example the transfer function of a first order Butterworth
    lowpass with a cutoff frequency of ``1 / pi`` could be defined as
    ``Quotient(Constant(1.0), Polynomial([0.5, 1.0]))``, but the inversion can also
    be abbreviated with the ``~`` operator: ``~Polynomial([0.5, 1.0])``.

    In addition to the functionality of its methods, this class has some operator
    overloads:

    * Common operators
       * checking the equality with ``==`` and ``!=``
       * calling the Filter instance with a number or an array of frequencies:
         returns the computed complex samples in a tuple with one element for each
         channel of the filter.
    * Operators for builtin functions
       * getting the length with :func:`len`: this returns the number of channels.
       * casting to a mildly informative string with :func:`str()`.
       * casting to a representation with :func:`repr()`. If :class:`~sumpf.Filter`
         (from SuMPF) is defined in the current name space, the filter can be
         reproduced by evaluating the representation (``eval(repr(filter_))``).
       * computing the absolute of the filter function with :func:`abs()`.
    * Math operators
       * computing the negative of the filter function with ``-filter_``.
       * algebra operations with ``+``, ``-``, ``*`` and ``/``:
         These operators work only with other filters, except for the multiplication,
         which can be used to apply the filter to Signal or Spectrum instances.
         Broadcasting is done like in :mod:`numpy` (e.g. adding a single-channel
         filter to a multi-channel one, will add the channel of the first filter
         to each of the second.)
    * Rededicated operators (operators, for which Python has intended a different function than for what it is used in the :class:`~sumpf.Filter` class)
       * inverting the filter with ``~filter_``. The inverse of a spectrum is
         simply ``1 / filter_``.
    """
    # terms for defining transfer functions
    Constant = terms.Constant.factory
    Polynomial = terms.Polynomial.factory
    Exp = terms.Exp.factory
    Absolute = terms.Absolute.factory
    Negative = terms.Negative.factory
    Sum = terms.Sum.factory
    Difference = terms.Difference.factory
    Product = terms.Product.factory
    Quotient = terms.Quotient.factory

    # supported file formats
    file_formats = persistence.formats

    def __init__(self, transfer_functions=(Constant(1.0),), labels=("",)):
        """
        :param transfer_functions: a sequence of transfer functions (terms), one for each channel
        :param labels: a sequence of string labels for the channels
        """
        self.__transfer_functions = transfer_functions
        self.__labels = sumpf_internal.sanitize_labels(labels=labels, number=len(transfer_functions))

    ###########################################
    # overloaded operators (non math-related) #
    ###########################################

    def __call__(self, frequencies):
        """Samples the transfer function of the filter at the given frequencies.

        :param frequencies: a number or a sequence of numbers
        :returns: a tuple of channels, where each channel is a number, if ``frequencies``
                  is a number or an array, if ``frequencies`` is a sequence.
        """
        if not numpy.shape(frequencies):    # create an array if frequencies is a scalar value
            s = S(numpy.reshape(frequencies, (1, 1)))
            return tuple(tf(s)[0, 0] for tf in self.__transfer_functions)
        else:
            s = S(frequencies)
            return tuple(tf(s) for tf in self.__transfer_functions)

    def __len__(self):
        """Operator overload for retrieving the filter's number of channels with
        the built-in function :func:`len()`.

        :returns: an integer
        """
        return len(self.__transfer_functions)

    def __str__(self):
        """Operator overload for generating a short description of the filter
        with the built-in function :func:`str()`.

        :returns: a reasonably short string
        """
        return ("<{module}.{class_} object "
                "(channel count: {channel_count}) "
                "at 0x{address:x}>").format(module=self.__module__,
                                            class_=self.__class__.__name__,
                                            channel_count=len(self.__transfer_functions),
                                            address=id(self))

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the filter, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        return ("{class_}(transfer_functions={transfer_functions!r}, "
                "labels={labels})").format(class_=self.__class__.__name__,
                                           transfer_functions=self.__transfer_functions,
                                           labels=self.__labels)

    def __eq__(self, other):
        """Operator overload for comparing this filter to another object with ``==``"""
        if not isinstance(other, Filter):
            return False
        elif len(self.__transfer_functions) != len(other):
            return False
        elif any(t1 != t2 for t1, t2 in zip(self.__transfer_functions, other.transfer_functions())):
            return False
        elif self.__labels != other.labels():
            return False
        return True

    def __ne__(self, other):
        """Operator overload for comparing this filter to another object with ``!=``"""
        return not self == other

    ###################################
    # overloaded unary math operators #
    ###################################

    def __abs__(self):
        """Operator overload for computing the magnitude of the filter with the
        built-in function :func:`abs`.

        :returns: a Filter instance
        """
        return Filter(transfer_functions=tuple(abs(tf) for tf in self.__transfer_functions),
                      labels=self.__labels)

    def __neg__(self):
        """Operator for inverting the phase of the filter with ``-filter_``.

        :returns: a Filter instance
        """
        return Filter(transfer_functions=tuple(-tf for tf in self.__transfer_functions),
                      labels=self.__labels)

    ####################################
    # overloaded binary math operators #
    ####################################

    def __algebra_function(self, other, function, label):
        """Private helper function that implements the broadcasting of filters with
        different numbers of channels, when using the overloaded math operators.

        :param other: the other filter
        :param function: a function, that implements the computation
        :param label: the string label for the computed channels
        :returns: a Filter instance
        """
        if len(self.__transfer_functions) == 1:
            tf1 = self.__transfer_functions[0]
            return Filter(transfer_functions=tuple(function(tf1, tf2) for tf2 in other.transfer_functions()),
                          labels=(label,) * len(other))
        elif len(other) == 1:
            tf2 = other.transfer_functions()[0]
            return Filter(transfer_functions=tuple(function(tf1, tf2) for tf1 in self.__transfer_functions),
                          labels=(label,) * len(self.__transfer_functions))
        elif len(self.__transfer_functions) == len(other):
            transfer_functions = zip(self.__transfer_functions, other.transfer_functions())
            return Filter(transfer_functions=tuple(function(tf1, tf2) for tf1, tf2 in transfer_functions),
                          labels=(label,) * len(other))
        else:
            raise ValueError(("cannot compute the {} of Filters "
                              "with channel counts {} and {}").format(label,
                                                                      len(self.__transfer_functions),
                                                                      len(other)))

    def __add__(self, other):
        """Operator overload for adding another filter to this filter.

        :param other: a Filter instance
        :returns: a Filter instance
        """
        if isinstance(other, Filter):
            return self.__algebra_function(other=other,
                                           function=lambda a, b: a + b,
                                           label="Sum")
        else:
            return NotImplemented

    def __sub__(self, other):
        """Operator overload for subtracting another filter from this filter.

        :param other: a Filter instance
        :returns: a Filter instance
        """
        if isinstance(other, Filter):
            return self.__algebra_function(other=other,
                                           function=lambda a, b: a - b,
                                           label="Difference")
        else:
            return NotImplemented

    def __mul__(self, other):
        """Operator overload for multiplying this filter with another filter or
        for applying this filter to a Signal or a Spectrum instance.

        :param other: a Filter, Signal or Spectrum instance
        :returns: a Filter, Signal or Spectrum instance
        """
        if isinstance(other, Filter):
            return self.__algebra_function(other=other,
                                           function=lambda a, b: a * b,
                                           label="Product")
        elif isinstance(other, sumpf.Spectrum):
            filter_ = self.spectrum(resolution=other.resolution(),
                                    length=other.length())
            return filter_ * other
        elif isinstance(other, sumpf.Signal):
            spectrum = other.fourier_transform()
            filter_ = self.spectrum(resolution=spectrum.resolution(),
                                    length=spectrum.length())
            filtered = filter_ * spectrum
            return filtered.inverse_fourier_transform()
        else:
            return NotImplemented

    def __rmul__(self, other):
        """Right hand side operator overload for applying this filter to a Signal
        or a Spectrum instance.

        :param other: a Signal or Spectrum instance
        :returns: a Signal or Spectrum instance
        """
        return self * other

    def __truediv__(self, other):
        """Operator overload for dividing this filter by another filter.

        :param other: a Filter instance
        :returns: a Filter instance
        """
        if isinstance(other, Filter):
            return self.__algebra_function(other=other,
                                           function=lambda a, b: a / b,
                                           label="Quotient")
        else:
            return NotImplemented

    #########################################
    # overloaded and misused math operators #
    #########################################

    def __invert__(self):
        """Rededicated operator overload for inverting this filter.
        The inverse of a filter is simply ``1 / filter_``.

        :returns: a Filter instance
        """
        return Filter(transfer_functions=tuple(~tf for tf in self.__transfer_functions),
                      labels=self.__labels)

    #######################################################
    # parameters, that have been set with the constructor #
    #######################################################

    def transfer_functions(self):
        """Returns the transfer functions of this filter.

        :returns: a tuple of terms
        """
        return self.__transfer_functions

    def labels(self):
        """Returns the labels for the channels of this filter.

        :returns: a sequence of labels
        """
        return self.__labels

    #######################
    # convenience methods #
    #######################

    def spectrum(self, resolution, length):
        """Samples the transfer functions with the given resolution and given number
        of samples and returns the result as a spectrum.

        :param resolution: the frequency resolution of the resulting spectrum
        :param length: the number of samples per channel of the resulting spectrum
        :returns: a Spectrum instance
        """
        frequencies = numpy.linspace(0.0, (length - 1) * resolution, length)
        s = S(frequencies)
        channels = sumpf_internal.allocate_array(shape=(len(self.__transfer_functions), length), dtype=numpy.complex128)
        for tf, c in zip(self.__transfer_functions, channels):
            tf(s, out=c)
        return sumpf.Spectrum(channels=channels, resolution=resolution, labels=self.__labels)

    #######################
    # persistence methods #
    #######################

    @staticmethod
    def load(path):
        """A static method to load a :class:`~sumpf.Filter` instance from a file.

        :param path: the path to the file.
        :returns: the loaded filter
        """
        return sumpf_internal.read_file(path=path,
                                        readers=persistence.readers,
                                        reader_base_class=persistence.Reader)

    def save(self, path, file_format=file_formats.AUTO):
        """Saves the filter to a file. The file will be created if it does not
        exist.

        :param path: the path to the file
        :param file_format: an optional flag from the :attr:`sumpf.Filter.file_formats`
                            enumeration, that specifies the file format, in which
                            the filter shall be stored. If this parameter is omitted
                            or set to :attr:`~sumpf.Filter.file_formats.AUTO`, the
                            format will be guessed from the ending of the filename.
        :returns: self
        """
        writer = sumpf_internal.get_writer(file_format=file_format,
                                           writers=persistence.writers,
                                           writer_base_class=persistence.Writer)
        writer(self, path)
        return self
