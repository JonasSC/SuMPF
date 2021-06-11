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

"""Contains interpolation functions."""

import functools
import numpy
from ._enums import Interpolations

__all__ = ("get", "zero", "one", "linear", "logarithmic", "log_x", "log_y", "stairs_lin", "stairs_log")


def get(flag):
    """Returns the interpolation function, that is specified by the given flag
    from the :class:`~sumpf._internal.Interpolations` enumeration.

    :param flag: a flag from the :class:`~sumpf._internal.Interpolations` enumeration
    :returns: a function, that takes three parameters. The first is the x values
              as an array or a scalar number, for which interpolated values shall
              be calculated. The second is an array of x values, where the function
              has supporting points and the third is an equally long array of the
              function results at the supporting points. The function returns
              an array of interpolated values or a single result, depending on
              the first parameter being an array or a scalar.
    """
    # pylint: disable=too-many-return-statements
    if flag is Interpolations.ZERO:
        return zero
    elif flag is Interpolations.ONE:
        return one
    elif flag is Interpolations.LINEAR:
        return linear
    elif flag is Interpolations.LOGARITHMIC:
        return logarithmic
    elif flag is Interpolations.LOG_X:
        return log_x
    elif flag is Interpolations.LOG_Y:
        return log_y
    elif flag is Interpolations.STAIRS_LIN:
        return stairs_lin
    elif flag is Interpolations.STAIRS_LOG:
        return stairs_log
    else:
        raise ValueError(f"Unknown interpolation flag: {flag}. See sumpf.Bands.interpolations for available flags.")


def interpolation(func):
    """A decorator for the interpolation functions, that implements the boilerplate,
    that is common to all interpolation functions:

    * if the given x values are an empty array, the result is empty as well.
    * at the supporting points, the interpolation function returns the exact function values
    """

    @functools.wraps(func)
    def f(x, xs, ys):
        if isinstance(x, (float, int)):
            if x in xs:
                return ys[xs == x][0]
            else:
                return func(x, xs, ys, scalar=True)
        elif len(x) == 0:     # pylint: disable=len-as-condition; x might be a NumPy array, where __nonzero__ is not equivalent to len(.)
            return numpy.empty(0)
        else:
            result = func(x, xs, ys, scalar=False)
            for i, x_i in enumerate(x):
                if x_i in xs:
                    result[i] = ys[xs == x_i][0]
            return result

    return f


@interpolation
def zero(x, xs, ys, scalar):    # pylint: disable=unused-argument; all interpolation functions shall have the same interface
    """An interpolation, that fills the unknown values with zeros.

    :param x: an array or a scalar value, where the function shall be evaluated
    :param xs: an array of x values of the supporting points
    :param ys: an array of function values of the supporting points. This array
               must have the same length as the xs array.
    :returns: the interpolated or extrapolated function values as an array or a
              scalar, depending on x being an array or a number
    """
#   :param scalar: True if x is a scalar value, False if x is an array. This
#                  parameter is set by the "interpolation"-decorator and is not
#                  exposed to the user of the interpolation function.
    if scalar:
        return 0.0
    else:
        return numpy.zeros(len(x), dtype=ys.dtype)


@interpolation
def one(x, xs, ys, scalar):     # pylint: disable=unused-argument; all interpolation functions shall have the same interface
    """An interpolation, that fills the unknown values with ones.

    :param x: an array or a scalar value, where the function shall be evaluated
    :param xs: an array of x values of the supporting points
    :param ys: an array of function values of the supporting points. This array
               must have the same length as the xs array.
    :returns: the interpolated or extrapolated function values as an array or a
              scalar, depending on x being an array or a number
    """
#   :param scalar: True if x is a scalar value, False if x is an array. This
#                  parameter is set by the "interpolation"-decorator and is not
#                  exposed to the user of the interpolation function.
    if scalar:
        return 1.0
    else:
        return numpy.ones(len(x), dtype=ys.dtype)


def _linear(x, xs, ys, scalar):
    """A helper function, that implements the linear interpolation, so it can be
    used by other interpolation functions, too.
    """
    # pylint: disable=too-many-return-statements; there are many corner cases to be covered here
    if len(xs) == 1:
        if scalar:
            return ys[0]
        else:
            return numpy.full(len(x), fill_value=ys[0], dtype=ys.dtype)
    else:
        if scalar:
            if x < xs[0]:
                m = (ys[1] - ys[0]) / (xs[1] - xs[0])
                if numpy.isinf(m):
                    return numpy.nan
                n = ys[0] - m * xs[0]
                return m * x + n
            elif x > xs[-1]:
                m = (ys[-1] - ys[-2]) / (xs[-1] - xs[-2])
                if numpy.isinf(m):
                    return numpy.nan
                n = ys[-1] - m * xs[-1]
                return m * x + n
            else:
                return numpy.interp(x, xp=xs, fp=ys)
        else:
            result = numpy.interp(x, xp=xs, fp=ys)
            if x.min() < xs[0]:
                mask = x < xs[0]
                m = (ys[1] - ys[0]) / (xs[1] - xs[0])
                n = ys[0] - m * xs[0]
                result[mask] = m * x[mask] + n
            if x.max() > xs[-1]:
                mask = x > xs[-1]
                m = (ys[-1] - ys[-2]) / (xs[-1] - xs[-2])
                n = ys[-1] - m * xs[-1]
                result[mask] = m * x[mask] + n
            return result


@interpolation
def linear(x, xs, ys, scalar):
    """An interpolation, that interpolates linearly between two supporting points.

    :param x: an array or a scalar value, where the function shall be evaluated
    :param xs: an array of x values of the supporting points
    :param ys: an array of function values of the supporting points. This array
               must have the same length as the xs array.
    :returns: the interpolated or extrapolated function values as an array or a
              scalar, depending on x being an array or a number
    """
#   :param scalar: True if x is a scalar value, False if x is an array. This
#                  parameter is set by the "interpolation"-decorator and is not
#                  exposed to the user of the interpolation function.
    return _linear(x, xs, ys, scalar)


@interpolation
def logarithmic(x, xs, ys, scalar):
    """An interpolation, that hat interpolates logarithmically on both axes.

    :param x: an array or a scalar value, where the function shall be evaluated
    :param xs: an array of x values of the supporting points
    :param ys: an array of function values of the supporting points. This array
               must have the same length as the xs array.
    :returns: the interpolated or extrapolated function values as an array or a
              scalar, depending on x being an array or a number
    """
#   :param scalar: True if x is a scalar value, False if x is an array. This
#                  parameter is set by the "interpolation"-decorator and is not
#                  exposed to the user of the interpolation function.
    return numpy.exp2(_linear(numpy.log2(x), numpy.log2(xs), numpy.log2(ys), scalar))    # the actual base of the logarithm does not matter, but the log2 function proved to be twice as fast as log or log10, while exp was only slightly faster than exp2


@interpolation
def log_x(x, xs, ys, scalar):
    """An interpolation, that interpolates logarithmically on the x-axis and linearly
    on the y-axis.

    This interpolation might be useful for :class:`~sumpf.Bands` filters, where
    the filter values are in dB, so that they shall not be processed logarithmically,
    but the frequencies are plotted on a logarithmic x-axis. In such a case, this
    interpolation will produce straight lines between two supporting points.

    :param x: an array or a scalar value, where the function shall be evaluated
    :param xs: an array of x values of the supporting points
    :param ys: an array of function values of the supporting points. This array
               must have the same length as the xs array.
    :returns: the interpolated or extrapolated function values as an array or a
              scalar, depending on x being an array or a number
    """
#   :param scalar: True if x is a scalar value, False if x is an array. This
#                  parameter is set by the "interpolation"-decorator and is not
#                  exposed to the user of the interpolation function.
    return _linear(numpy.log2(x), numpy.log2(xs), ys, scalar)    # the actual base of the logarithm does not matter, but the log2 function proved to be twice as fast as log or log10


@interpolation
def log_y(x, xs, ys, scalar):
    """An interpolation, that hat interpolates linearly on the x-axis and logarithmically
    on the y-axis.

    :param x: an array or a scalar value, where the function shall be evaluated
    :param xs: an array of x values of the supporting points
    :param ys: an array of function values of the supporting points. This array
               must have the same length as the xs array.
    :returns: the interpolated or extrapolated function values as an array or a
              scalar, depending on x being an array or a number
    """
#   :param scalar: True if x is a scalar value, False if x is an array. This
#                  parameter is set by the "interpolation"-decorator and is not
#                  exposed to the user of the interpolation function.
    return numpy.exp2(_linear(x, xs, numpy.log2(ys), scalar))    # the actual base of the logarithm does not matter, but the log2 function proved to be twice as fast as log or log10, while exp was only slightly faster than exp2


def _stairs_lin(x, xs, ys):
    """A helper function, that implements the linear stairs interpolation, so it
    can be used by other interpolation functions, too.

    Other than in the other interpolation functions, this helper function expects
    x to be an array every time.
    """
    i = numpy.searchsorted(xs, x)
    i[i >= len(ys)] -= 1
    left = x - xs[numpy.maximum(i - 1, 0)]
    right = x - xs[i]
    mask = (numpy.fabs(left) < numpy.fabs(right))
    i[mask] -= 1
    return ys[i]


@interpolation
def stairs_lin(x, xs, ys, scalar):
    """An interpolation, that maintains a constant value around a supporting point.
    The x-value, where it switches from the function value of one supporting point
    to the other is the average x-value between the x-values of the surrounding
    supporting points.

    :param x: an array or a scalar value, where the function shall be evaluated
    :param xs: an array of x values of the supporting points
    :param ys: an array of function values of the supporting points. This array
               must have the same length as the xs array.
    :returns: the interpolated or extrapolated function values as an array or a
              scalar, depending on x being an array or a number
    """
#   :param scalar: True if x is a scalar value, False if x is an array. This
#                  parameter is set by the "interpolation"-decorator and is not
#                  exposed to the user of the interpolation function.
    if scalar:
        return _stairs_lin(numpy.array((x,)), xs, ys)[0]
    else:
        return _stairs_lin(x, xs, ys)


@interpolation
def stairs_log(x, xs, ys, scalar):
    """An interpolation, that maintains a constant value around a supporting point.
    The x-value, where it switches from the function value of one supporting point
    to the other is the middle value between the surrounding supporting points on
    a logarithmic x-axis.

    :param x: an array or a scalar value, where the function shall be evaluated
    :param xs: an array of x values of the supporting points
    :param ys: an array of function values of the supporting points. This array
               must have the same length as the xs array.
    :returns: the interpolated or extrapolated function values as an array or a
              scalar, depending on x being an array or a number
    """
#   :param scalar: True if x is a scalar value, False if x is an array. This
#                  parameter is set by the "interpolation"-decorator and is not
#                  exposed to the user of the interpolation function.
    minimum = xs.min()
    if scalar:
        if x < minimum:
            return ys[xs == minimum][0]
        else:
            maximum = xs.max()
            if x > maximum:
                return ys[xs == maximum][0]
            else:
                return _stairs_lin(numpy.log2(numpy.array((x,))), numpy.log2(xs), ys)[0]
    else:
        result = _stairs_lin(numpy.log2(x), numpy.log2(xs), ys)    # the actual base of the logarithm does not matter, but the log2 function proved to be twice as fast as log or log10
        mask = (x < minimum)
        result[mask] = ys[xs == minimum][0]
        maximum = xs.max()
        mask = (x > maximum)
        result[mask] = ys[xs == maximum][0]
        return result
