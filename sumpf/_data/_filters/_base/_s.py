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

"""Contains classes, which manage the frequency variable ``s`` in filter calculations"""

import math
import weakref
import numpy

__all__ = ("S",)


class S:
    """Instances of this class compute and store the frequency variable ``s = 2j * pi * f``
    for sampling a filter's transfer function. If required, they also create and
    cache a manager for ``1 / s``, if a lowpass-to-highpass transformation requires it.
    """

    def __init__(self, frequencies):
        """
        :param frequencies: a float or an array of float for frequencies in Hz.
        """
        self.__frequencies = frequencies
        self.__s = None
        self.__transformed = None

    def __call__(self):
        """Returns the values for ``s``

        :returns: a :func:`numpy.array` of complex frequency values
        """
        if self.__s is None:
            self.__s = numpy.multiply(2.0j * math.pi, self.__frequencies)
        return self.__s

    def frequencies(self):
        """Returns the frequency values in Hz instead of angular frequencies.
        Also, these frequencies are not affected by a lowpass-to-highpass transform.

        :returns: a sequence of float frequency values
        """
        return self.__frequencies

    def fix(self, result):
        """Replaces the samples of the filter's transfer function for 0Hz with 0.0,
        if a lowpass-to-highpass transform has made them invalid, because ``1 / s``
        is a division by zero in this case.

        :param result: the resulting array of the sampling (the samples will be replaced in place)
        :returns: the resulting array
        """
        if self.__transformed:
            return self.__transformed.fix(result)
        else:
            return result

    def transform(self):
        """Returns a manager for the lowpass-to-highpass-transformed array for ``1 / s``.
        The manager will be created if necessary.

        :returns: a TransformedS instance
        """
        if self.__transformed is None:
            self.__transformed = TransformedS(self)
        return self.__transformed


class TransformedS:
    """Computes the values of ``1 / s`` for sampling a lowpass-to-highpass-transformed
    transfer function.
    """

    def __init__(self, origin):
        """
        :param origin: the :class:`sumpf._data._filters._base._s.S` instance, from
                       which the ``1 / s`` values shall be computed
        """
        self.__origin = weakref.proxy(origin)
        self.__s = None
        self.__invalid = None

    def __call__(self):
        """Returns the values for ``1 / s``

        :returns: a :func:`numpy.array` of complex frequency values
        """
        if self.__s is None:
            s = self.__origin()
            zero = s == 0
            if zero.any():  # avoid zero division errors by defining the result of a transformed term to be zero at s=0
                self.__invalid = zero.nonzero()
                self.__s = numpy.divide(1.0, s, where=(s != 0))
            else:
                self.__invalid = None
                self.__s = numpy.divide(1.0, s)
        return self.__s

    def frequencies(self):
        """Returns the frequency values in Hz instead of angular frequencies.
        Also, these frequencies are not affected by a lowpass-to-highpass transform.

        :returns: a sequence of float frequency values
        """
        return self.__origin.frequencies()

    def fix(self, result):
        """Replaces the samples of the filter's transfer function for 0Hz with 0.0,
        if a lowpass-to-highpass transform has made them invalid, because ``1 / s``
        is a division by zero in this case.

        :param result: the resulting array of the sampling (the samples will be replaced in place)
        :returns: the resulting array
        """
        if self.__invalid:
            result[self.__invalid] = 0.0
        return result

    def transform(self):
        """Returns the original manager for the frequency variable ``s``.

        :returns: an :class:`sumpf._data._filters._base._s.S` instance
        """
        return self.__origin
