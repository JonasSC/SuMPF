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

"""Contains helper classes for the computation of convolutions and correlations."""

import numpy
from ._functions import allocate_array
from ._enums import ConvolutionMode

__all__ = ("convolution", "correlation")


class Convolution:
    """A base class for the convolution classes below, that implements the with_vector2
    method, because other than a correlation, a convolution is commutative."""

    @staticmethod
    def with_vector(matrix, vector, offsets):
        """Abstract method, that has to be implemented in derived classes

        :param matrix: a two dimensional :func:`numpy.array`
        :param vector: a one dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        raise NotImplementedError("This method should have been implemented in a derived class.")

    @classmethod
    def with_vector2(cls, vector, matrix, offsets):
        """
        :param vector: a one dimensional :func:`numpy.array`
        :param matrix: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        return cls.with_vector(matrix, vector, offsets)


class FullConvolution(Convolution):
    """A helper class, that computes convolutions with :mod:`numpy`'s :func:`~numpy.convolve`
    function in ``full`` mode.
    """

    @staticmethod
    def with_vector(matrix, vector, offsets):
        """
        :param matrix: a two dimensional :func:`numpy.array`
        :param vector: a one dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        mc, ml = matrix.shape
        channels = allocate_array(shape=(mc, ml + len(vector) - 1))
        for c, channel in zip(matrix, channels):
            channel[:] = numpy.convolve(c, vector, mode="full")
        return channels, sum(offsets)

    @staticmethod
    def with_matrix(a, b, offsets):
        """
        :param a: a two dimensional :func:`numpy.array`
        :param b: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        ac, al = a.shape
        bc, bl = b.shape
        channels = allocate_array(shape=(min(ac, bc), al + bl - 1))
        for c, d, channel in zip(a, b, channels):
            channel[:] = numpy.convolve(c, d, mode="full")
        return channels, sum(offsets)


class SameConvolution(Convolution):
    """A helper class, that computes convolutions with :mod:`numpy`'s :func:`~numpy.convolve`
    function in ``same`` mode.
    """

    @staticmethod
    def with_vector(matrix, vector, offsets):
        """
        :param matrix: a two dimensional :func:`numpy.array`
        :param vector: a one dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        mc, ml = matrix.shape
        vl = len(vector)
        channels = allocate_array(shape=(mc, max(ml, vl)))
        for c, channel in zip(matrix, channels):
            channel[:] = numpy.convolve(c, vector, mode="same")
        return channels, sum(offsets) + (min(ml, vl) - 1) // 2

    @staticmethod
    def with_matrix(a, b, offsets):
        """
        :param a: a two dimensional :func:`numpy.array`
        :param b: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        ac, al = a.shape
        bc, bl = b.shape
        channels = allocate_array(shape=(min(ac, bc), max(al, bl)))
        for c, d, channel in zip(a, b, channels):
            channel[:] = numpy.convolve(c, d, mode="same")
        return channels, sum(offsets) + (min(al, bl) - 1) // 2


class ValidConvolution(Convolution):
    """A helper class, that computes convolutions with :mod:`numpy`'s :func:`~numpy.convolve`
    function in ``valid`` mode.
    """

    @staticmethod
    def with_vector(matrix, vector, offsets):
        """
        :param matrix: a two dimensional :func:`numpy.array`
        :param vector: a one dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        mc, ml = matrix.shape
        vl = len(vector)
        channels = allocate_array(shape=(mc, abs(ml - vl) + 1))
        for c, channel in zip(matrix, channels):
            channel[:] = numpy.convolve(c, vector, mode="valid")
        return channels, sum(offsets) + (min(ml, vl) - 1)

    @staticmethod
    def with_matrix(a, b, offsets):
        """
        :param a: a two dimensional :func:`numpy.array`
        :param b: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        ac, al = a.shape
        bc, bl = b.shape
        channels = allocate_array(shape=(min(ac, bc), abs(al - bl) + 1))
        for c, d, channel in zip(a, b, channels):
            channel[:] = numpy.convolve(c, d, mode="valid")
        return channels, sum(offsets) + (min(al, bl) - 1)


class SpectrumConvolution(Convolution):
    """A helper class, that computes convolutions by transforming the data to the
    frequency domain and doing a multiplication there.
    """

    @staticmethod
    def with_vector(matrix, vector, offsets):
        """
        :param matrix: a two dimensional :func:`numpy.array`
        :param vector: a one dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        mc, ml = matrix.shape
        vl = len(vector)
        rl = max(ml, vl)                    # result length
        pl = rl if rl % 2 == 0 else rl + 1  # padded length
        # zero padding, so that matrix and vector have the same length
        if ml < pl:
            matrix = pad_matrix(matrix, ml, mc, pl)
        if vl < pl:
            vector = pad_vector(vector, vl, pl)
        # compute the convolution
        ms = numpy.fft.rfft(matrix)
        vs = numpy.fft.rfft(vector)
        channels = allocate_array(shape=(mc, rl))
        channels[:] = numpy.fft.irfft(ms * vs)[:, 0:rl]
        return channels, sum(offsets)

    @staticmethod
    def with_matrix(a, b, offsets):
        """
        :param a: a two dimensional :func:`numpy.array`
        :param b: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        ac, al = a.shape
        bc, bl = b.shape
        c = min(ac, bc)
        rl = max(al, bl)                    # result length
        pl = rl if rl % 2 == 0 else rl + 1  # padded length
        # zero padding, so that matrix and vector have the same length
        if al < pl:
            a = pad_matrix(a, al, c, pl)
        if bl < pl:
            b = pad_matrix(b, bl, c, pl)
        # compute the convolution
        as_ = numpy.fft.rfft(a[0:c])
        bs = numpy.fft.rfft(b[0:c])
        channels = allocate_array(shape=(c, rl))
        channels[:] = numpy.fft.irfft(as_ * bs)[:, 0:rl]
        return channels, sum(offsets)


class SpectrumPaddedConvolution(Convolution):
    """A helper class, that computes convolutions by transforming the data to the
    frequency domain and doing a multiplication there. Before transformation, this
    class's methods pad the data to avoid the effects of the circular convolution.
    """

    @staticmethod
    def with_vector(matrix, vector, offsets):
        """
        :param matrix: a two dimensional :func:`numpy.array`
        :param vector: a one dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken.
        """
        mc, ml = matrix.shape
        vl = len(vector)
        rl = ml + vl - 1                        # result length
        pl = rl + 1 if rl % 2 == 1 else rl + 2  # padded length
        # pad the arrays
        matrix = pad_matrix(matrix, ml, mc, pl)
        vector = pad_vector(vector, vl, pl)
        # compute the convolution
        ms = numpy.fft.rfft(matrix)
        vs = numpy.fft.rfft(vector)
        channels = allocate_array(shape=(mc, rl))
        channels[:] = numpy.fft.irfft(ms * vs)[:, 0:rl]
        return channels, sum(offsets)

    @staticmethod
    def with_matrix(a, b, offsets):
        """
        :param a: a two dimensional :func:`numpy.array`
        :param b: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        ac, al = a.shape
        bc, bl = b.shape
        c = min(ac, bc)
        rl = al + bl - 1                        # result length
        pl = rl + 1 if rl % 2 == 1 else rl + 2  # padded length
        # pad the arrays
        a = pad_matrix(a, al, c, pl)
        b = pad_matrix(b, bl, c, pl)
        # compute the convolution
        as_ = numpy.fft.rfft(a[0:c])
        bs = numpy.fft.rfft(b[0:c])
        channels = allocate_array(shape=(c, rl))
        channels[:] = numpy.fft.irfft(as_ * bs)[:, 0:rl]
        return channels, sum(offsets)


class FullCorrelation:
    """A helper class, that computes correlations with :mod:`numpy`'s :func:`~numpy.correlate`
    function in ``full`` mode.
    """

    @staticmethod
    def with_vector(matrix, vector, offsets):
        """
        :param matrix: a two dimensional :func:`numpy.array`
        :param vector: a one dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        mc, ml = matrix.shape
        channels = allocate_array(shape=(mc, ml + len(vector) - 1))
        for c, channel in zip(matrix, channels):
            channel[:] = numpy.correlate(c, vector, mode="full")[::-1]
        return channels, offsets[1] - offsets[0] - ml + 1

    @staticmethod
    def with_vector2(vector, matrix, offsets):
        """
        :param vector: a one dimensional :func:`numpy.array`
        :param matrix: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        mc, ml = matrix.shape
        vl = len(vector)
        channels = allocate_array(shape=(mc, ml + vl - 1))
        for c, channel in zip(matrix, channels):
            channel[:] = numpy.correlate(vector, c, mode="full")[::-1]
        return channels, offsets[1] - offsets[0] - vl + 1

    @staticmethod
    def with_matrix(a, b, offsets):
        """
        :param a: a two dimensional :func:`numpy.array`
        :param b: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        ac, al = a.shape
        bc, bl = b.shape
        channels = allocate_array(shape=(min(ac, bc), al + bl - 1))
        for c, d, channel in zip(a, b, channels):
            channel[:] = numpy.correlate(c, d, mode="full")[::-1]
        return channels, offsets[1] - offsets[0] - al + 1


class SameCorrelation:
    """A helper class, that computes correlations with :mod:`numpy`'s :func:`~numpy.convolve`
    function in ``same`` mode.
    """

    @staticmethod
    def with_vector(matrix, vector, offsets):
        """
        :param matrix: a two dimensional :func:`numpy.array`
        :param vector: a one dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        mc, ml = matrix.shape
        vl = len(vector)
        rl = max(ml, vl)
        channels = allocate_array(shape=(mc, rl))
        for c, channel in zip(matrix, channels):
            channel[:] = numpy.convolve(c[::-1], vector, mode="same")
        return channels, offsets[1] - offsets[0] + vl - rl - min(ml, vl) // 2

    @staticmethod
    def with_vector2(vector, matrix, offsets):
        """
        :param vector: a one dimensional :func:`numpy.array`
        :param matrix: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        vl = len(vector)
        mc, ml = matrix.shape
        rl = max(ml, vl)
        channels = allocate_array(shape=(mc, rl))
        vector = vector[::-1]
        for c, channel in zip(matrix, channels):
            channel[:] = numpy.convolve(vector, c, mode="same")
        return channels, offsets[1] - offsets[0] + ml - rl - min(vl, ml) // 2

    @staticmethod
    def with_matrix(a, b, offsets):
        """
        :param a: a two dimensional :func:`numpy.array`
        :param b: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        ac, al = a.shape
        bc, bl = b.shape
        rl = max(al, bl)
        channels = allocate_array(shape=(min(ac, bc), rl))
        for c, d, channel in zip(a, b, channels):
            channel[:] = numpy.convolve(c[::-1], d, mode="same")
        return channels, offsets[1] - offsets[0] + bl - rl - min(al, bl) // 2


class ValidCorrelation:
    """A helper class, that computes correlations with :mod:`numpy`'s :func:`~numpy.correlate`
    function in ``valid`` mode.
    """

    @staticmethod
    def with_vector(matrix, vector, offsets):
        """
        :param matrix: a two dimensional :func:`numpy.array`
        :param vector: a one dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        mc, ml = matrix.shape
        vl = len(vector)
        rl = abs(ml - vl) + 1
        channels = allocate_array(shape=(mc, rl))
        for c, channel in zip(matrix, channels):
            channel[:] = numpy.correlate(c, vector, mode="valid")[::-1]
        return channels, offsets[1] - offsets[0] - (ml - vl + rl) // 2

    @staticmethod
    def with_vector2(vector, matrix, offsets):
        """
        :param vector: a one dimensional :func:`numpy.array`
        :param matrix: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        vl = len(vector)
        mc, ml = matrix.shape
        rl = abs(vl - ml) + 1
        channels = allocate_array(shape=(mc, rl))
        for c, channel in zip(matrix, channels):
            channel[:] = numpy.correlate(vector, c, mode="valid")[::-1]
        return channels, offsets[1] - offsets[0] - (vl - ml + rl) // 2

    @staticmethod
    def with_matrix(a, b, offsets):
        """
        :param a: a two dimensional :func:`numpy.array`
        :param b: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        ac, al = a.shape
        bc, bl = b.shape
        rl = abs(al - bl) + 1
        channels = allocate_array(shape=(min(ac, bc), rl))
        for c, d, channel in zip(a, b, channels):
            channel[:] = numpy.correlate(c, d, mode="valid")[::-1]
        return channels, offsets[1] - offsets[0] - (al - bl + rl) // 2


class SpectrumCorrelation:
    """A helper class, that computes correlations by transforming the data to the
    frequency domain and doing a multiplication there.
    """

    @staticmethod
    def with_vector(matrix, vector, offsets):
        """
        :param matrix: a two dimensional :func:`numpy.array`
        :param vector: a one dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        mc, ml = matrix.shape
        vl = len(vector)
        rl = max(ml, vl)    # result length
        # zero padding, so that matrix and vector have the same length
        if rl % 2 == 1:
            pl = rl + 1
            matrix = shift_matrix(matrix, ml, mc, pl)
            vector = pad_vector(vector, vl, pl)
        elif ml < rl:
            matrix = shift_and_cycle_matrix(matrix, ml, mc, rl, 1)
        elif vl < rl:
            vector = pad_and_cycle_vector(vector, vl, rl, -1)
        else:
            vector = cycle_vector(vector, vl, -1)
        # compute the correlation
        ms = numpy.fft.rfft(matrix).conjugate()
        vs = numpy.fft.rfft(vector)
        channels = allocate_array(shape=(mc, rl))
        channels[:] = numpy.fft.irfft(ms * vs)[:, -rl:]
        return channels, offsets[1] - offsets[0] - ml + 1

    @staticmethod
    def with_vector2(vector, matrix, offsets):
        """
        :param vector: a one dimensional :func:`numpy.array`
        :param matrix: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        vl = len(vector)
        mc, ml = matrix.shape
        rl = max(ml, vl)    # result length
        # zero padding, so that matrix and vector have the same length
        if rl % 2 == 1:
            pl = rl + 1
            vector = shift_vector(vector, vl, pl)
            matrix = pad_matrix(matrix, ml, mc, pl)
        elif vl < rl:
            vector = shift_and_cycle_vector(vector, vl, rl, 1)
        elif ml < rl:
            matrix = pad_and_cycle_matrix(matrix, ml, mc, rl, -1)
        else:
            matrix = cycle_matrix(matrix, vl, mc, -1)
        # compute the correlation
        vs = numpy.fft.rfft(vector).conjugate()
        ms = numpy.fft.rfft(matrix)
        channels = allocate_array(shape=(mc, rl))
        channels[:] = numpy.fft.irfft(vs * ms)[:, -rl:]
        return channels, offsets[1] - offsets[0] - vl + 1

    @staticmethod
    def with_matrix(a, b, offsets):
        """
        :param a: a two dimensional :func:`numpy.array`
        :param b: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        ac, al = a.shape
        bc, bl = b.shape
        c = min(ac, bc)
        rl = max(al, bl)    # result length
        # pad the arrays
        if rl % 2 == 1:
            pl = rl + 1
            a = shift_matrix(a, al, c, pl)
            b = pad_matrix(b, bl, c, pl)
        elif al < rl:
            a = shift_and_cycle_matrix(a, al, c, rl, 1)
        elif bl < rl:
            b = pad_and_cycle_matrix(b, bl, c, rl, -1)
        else:
            b = cycle_matrix(b, bl, c, -1)
        # compute the correlation
        as_ = numpy.fft.rfft(a[0:c]).conjugate()
        bs = numpy.fft.rfft(b[0:c])
        channels = allocate_array(shape=(c, rl))
        channels[:] = numpy.fft.irfft(as_ * bs)[:, -rl:]
        return channels, offsets[1] - offsets[0] - al + 1


class SpectrumPaddedCorrelation:
    """A helper class, that computes correlation by transforming the data to the
    frequency domain and doing a multiplication there. Before transformation, this
    class's methods pad the data to avoid the effects of the circular correlation.
    """

    @staticmethod
    def with_vector(matrix, vector, offsets):
        """
        :param matrix: a two dimensional :func:`numpy.array`
        :param vector: a one dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken.
        """
        mc, ml = matrix.shape
        vl = len(vector)
        rl = ml + vl - 1    # result length
        # pad the arrays
        if rl % 2 == 1:
            pl = rl + 1
            matrix = pad_and_shift_matrix(matrix, ml, mc, pl, 1)
        else:
            pl = rl + 2
            matrix = pad_and_shift_matrix(matrix, ml, mc, pl, 2)
        vector = shift_vector(vector, vl, pl)
        # compute the correlation
        ms = numpy.fft.rfft(matrix).conjugate()
        vs = numpy.fft.rfft(vector)
        channels = allocate_array(shape=(mc, rl))
        channels[:] = numpy.fft.irfft(ms * vs)[:, 0:rl]
        return channels, offsets[1] - offsets[0] - ml + 1

    @staticmethod
    def with_vector2(vector, matrix, offsets):
        """
        :param vector: a one dimensional :func:`numpy.array`
        :param matrix: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        vl = len(vector)
        mc, ml = matrix.shape
        rl = ml + vl - 1    # result length
        # pad the arrays
        if rl % 2 == 1:
            pl = rl + 1
            vector = pad_and_shift_vector(vector, vl, pl, 1)
        else:
            pl = rl + 2
            vector = pad_and_shift_vector(vector, vl, pl, 2)
        matrix = shift_matrix(matrix, ml, mc, pl)
        # compute the correlation
        vs = numpy.fft.rfft(vector).conjugate()
        ms = numpy.fft.rfft(matrix)
        channels = allocate_array(shape=(mc, rl))
        channels[:] = numpy.fft.irfft(vs * ms)[:, 0:rl]
        return channels, offsets[1] - offsets[0] - vl + 1

    @staticmethod
    def with_matrix(a, b, offsets):
        """
        :param a: a two dimensional :func:`numpy.array`
        :param b: a two dimensional :func:`numpy.array`
        :param offsets: a tuple with the offsets of the signals, from which the given data is taken
        """
        ac, al = a.shape
        bc, bl = b.shape
        c = min(ac, bc)
        rl = al + bl - 1    # result length
        # pad the arrays
        if rl % 2 == 1:
            pl = rl + 1
            a = pad_and_shift_matrix(a, al, c, pl, 1)
        else:
            pl = rl + 2
            a = pad_and_shift_matrix(a, al, c, pl, 2)
        b = shift_matrix(b, bl, c, pl)
        # compute the correlation
        as_ = numpy.fft.rfft(a[0:c]).conjugate()
        bs = numpy.fft.rfft(b[0:c])
        channels = allocate_array(shape=(c, rl))
        channels[:] = numpy.fft.irfft(as_ * bs)[:, 0:rl]
        return channels, offsets[1] - offsets[0] - al + 1


convolution = {ConvolutionMode.FULL: FullConvolution,
               ConvolutionMode.SAME: SameConvolution,
               ConvolutionMode.VALID: ValidConvolution,
               ConvolutionMode.SPECTRUM: SpectrumConvolution,
               ConvolutionMode.SPECTRUM_PADDED: SpectrumPaddedConvolution}
correlation = {ConvolutionMode.FULL: FullCorrelation,
               ConvolutionMode.SAME: SameCorrelation,
               ConvolutionMode.VALID: ValidCorrelation,
               ConvolutionMode.SPECTRUM: SpectrumCorrelation,
               ConvolutionMode.SPECTRUM_PADDED: SpectrumPaddedCorrelation}


def pad_vector(vector, vector_length, padded_length):
    """A helper function for padding a one dimensional array with zeros."""
    result = numpy.empty(padded_length)
    result[0:vector_length] = vector
    result[vector_length:] = 0.0
    return result


def shift_vector(vector, vector_length, padded_length):
    """A helper function for padding a one dimensional array with zeros."""
    result = numpy.empty(padded_length)
    result[0:-vector_length] = 0.0
    result[-vector_length:] = vector
    return result


def pad_and_shift_vector(vector, vector_length, padded_length, shift):
    """A helper function for padding a one dimensional array with zeros."""
    vector_length1 = vector_length + shift
    result = numpy.empty(padded_length)
    result[0:shift] = 0.0
    result[shift:vector_length1] = vector
    result[vector_length1:] = 0.0
    return result


def cycle_vector(vector, vector_length, shift):
    """A helper function for cyclic shifting a one dimensional array."""
    result = numpy.empty(vector_length)
    result[0:shift] = vector[-shift:]
    result[shift:] = vector[0:-shift]
    return result


def pad_and_cycle_vector(vector, vector_length, padded_length, shift):
    """A helper function for padding and cyclic shifting a one dimensional array.
    This function must only be used for negative shifts. For correct handling of
    positive shifts, see the pad_and_shift_vector function.
    """
    result = numpy.empty(padded_length)
    if vector_length > shift:
        vector_length1 = vector_length + shift
        result[0:vector_length1] = vector[-shift:]
        result[vector_length1:shift] = 0.0
    else:
        result[0:shift] = 0.0
    result[shift:] = vector[0:-shift]
    return result


def shift_and_cycle_vector(vector, vector_length, padded_length, shift):
    """A helper function for padding and cyclic shifting a one dimensional array.
    This function must only be used for positive shifts. For correct handling of
    negative shifts, see the pad_and_shift_vector function.
    """
    result = numpy.empty(padded_length)
    result[0:shift] = vector[-shift:]
    if vector_length > shift:
        vector_length1 = vector_length - shift
        result[shift:-vector_length1] = 0.0
        result[-vector_length1:] = vector[0:-shift]
    else:
        result[shift:] = 0.0
    return result


def pad_matrix(matrix, matrix_length, rows, padded_length):
    """A helper function for padding a two dimensional array with zeros."""
    result = numpy.empty(shape=(rows, padded_length))
    result[:, 0:matrix_length] = matrix[0:rows]
    result[:, matrix_length:] = 0.0
    return result


def shift_matrix(matrix, matrix_length, rows, padded_length):
    """A helper function for padding a two dimensional array with zeros."""
    result = numpy.empty(shape=(rows, padded_length))
    result[:, 0:-matrix_length] = 0.0
    result[:, -matrix_length:] = matrix[0:rows]
    return result


def pad_and_shift_matrix(matrix, matrix_length, rows, padded_length, shift):
    """A helper function for padding a two dimensional array with zeros."""
    matrix_length1 = matrix_length + shift
    result = numpy.empty(shape=(rows, padded_length))
    result[:, 0:shift] = 0.0
    result[:, shift:matrix_length1] = matrix[0:rows]
    result[:, matrix_length1:] = 0.0
    return result


def cycle_matrix(matrix, matrix_length, rows, shift):
    """A helper function for cyclic shifting a two dimensional array."""
    result = numpy.empty(shape=(rows, matrix_length))
    result[:, 0:shift] = matrix[0:rows, -shift:]
    result[:, shift:] = matrix[0:rows, 0:-shift]
    return result


def pad_and_cycle_matrix(matrix, matrix_length, rows, padded_length, shift):
    """A helper function for padding and cyclic shifting a two dimensional array.
    This function must only be used for negative shifts. For correct handling of
    positive shifts, see the pad_and_shift_matrix function.
    """
    result = numpy.empty(shape=(rows, padded_length))
    if matrix_length > shift:
        matrix_length1 = matrix_length + shift
        result[:, 0:matrix_length1] = matrix[0:rows, -shift:]
        result[:, matrix_length1:shift] = 0.0
    else:
        result[:, 0:shift] = 0.0
    result[:, shift:] = matrix[0:rows, 0:-shift]
    return result


def shift_and_cycle_matrix(matrix, matrix_length, rows, padded_length, shift):
    """A helper function for padding and cyclic shifting a two dimensional array.
    This function must only be used for positive shifts. For correct handling of
    negative shifts, see the pad_and_shift_matrix function.
    """
    result = numpy.empty(shape=(rows, padded_length))
    result[:, 0:shift] = matrix[0:rows, -shift:]
    if matrix_length > shift:
        matrix_length1 = matrix_length - shift
        result[:, shift:-matrix_length1] = 0.0
        result[:, -matrix_length1:] = matrix[0:rows, 0:-shift]
    else:
        result[:, shift:] = 0.0
    return result
