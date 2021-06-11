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

"""Contains the implementations of frequency weighting filters."""

import math
import numpy
from ._base import Filter, S, Constant, Polynomial, Product

__all__ = ("AWeighting", "BWeighting", "CWeighting", "DWeighting", "UWeighting")


def _a_factors(fr):
    """A generator, which is used internally to generate the filter terms, that
    are multiplied to form the A-weighting filter.

    :param fr: the reference frequency (1000Hz in IEC 61672-1)
    """
    fa = 10 ** 2.45  # f_A in IEC 61672-1:2013, Appendix E.3
    root5 = 5 ** 0.5 / 2
    f2 = (1.5 - root5) * fa  # f_2 in IEC 61672-1
    f3 = (1.5 + root5) * fa  # f_3 in IEC 61672-1
    s2 = 2 * math.pi * f2
    s3 = 2 * math.pi * f3
    yield Polynomial((1.0, 0.0)) / Polynomial((1.0, s2))
    yield Polynomial((1.0, 0.0)) / Polynomial((1.0, s3))
    yield from _c_factors(fr)


def _b_factors(fr):
    """A generator, which is used internally to generate the filter terms, that
    are multiplied to form the B-weighting filter.

    :param fr: the reference frequency (1000Hz in IEC 61672-1)
    """
    f5 = 158.5
    s5 = 2 * math.pi * f5
    yield Polynomial((1.0, 0.0)) / Polynomial((1.0, s5))
    yield from _c_factors(fr)


def _c_factors(fr):
    """A generator, which is used internally to generate the filter terms, that
    are multiplied to form the C-weighting filter.

    :param fr: the reference frequency (1000Hz in IEC 61672-1)
    """
    fl = 10 ** 1.5  # f_L in IEC 61672-1:2013, Appendix E.2
    fh = 10 ** 3.9  # f_H in IEC 61672-1
    d = 0.5 ** 0.5  # D in IEC 61672-1
    fr2 = fr ** 2
    fl2 = fl ** 2
    fh2 = fh ** 2
    c = fl2 * fh2  # c in IEC 61672-1
    b = (fr2 + c / fr2 - d * (fl2 + fh2)) / (1.0 - d)  # b in IEC 61672-1
    root = (b ** 2 - 4 * c) ** 0.5
    f1 = ((-b - root) / 2) ** 0.5  # f_1 in IEC 61672-1
    f4 = ((-b + root) / 2) ** 0.5  # f_2 in IEC 61672-1
    s1 = 2 * math.pi * f1
    s4 = 2 * math.pi * f4
    yield Polynomial((1.0, 0.0)) / Polynomial((1.0, s1))
    yield ~Polynomial((1.0, s1))
    yield Polynomial((1.0, 0.0)) / Polynomial((1.0, s4))
    yield ~Polynomial((1.0, s4))


def _d_factors(fr):  # pylint: disable=unused-argument; this argument is needed for compatibility with the other generators
    """A generator, which is used internally to generate the filter terms, that
    are multiplied to form the D-weighting filter.

    :param fr: an unused parameter, that is accepted, so this generator is compatible
               with the other generators
    """
    a = 1037918.48
    b = 1080768.16
    c = 9837328.0
    d = 11723776.0
    e = 79919.29
    f = 1345600.0
    u, v, w, x, y, z = numpy.multiply(2 * math.pi, numpy.sqrt((e, f, b, a, d, c)))
    yield Polynomial((1.0, 0.0)) / Polynomial((1.0, u))
    yield ~Polynomial((1.0, v))
    yield Polynomial((1.0, w, x ** 2)) / Polynomial((1.0, y, z ** 2))


def _u_factors(fr):  # pylint: disable=unused-argument; this argument is needed for compatibility with the other generators
    """A generator, which is used internally to generate the filter terms, that
    are multiplied to form the U-weighting filter.

    :param fr: an unused parameter, that is accepted, so this generator is compatible
               with the other generators
    """
    f1 = 12200
    f3 = 7850 - 8800j
    f4 = 7850 + 8800j
    f5 = 2900 - 12150j
    f6 = 2900 + 12150j
    s1, s3, s4, s5, s6 = numpy.multiply(2 * math.pi, (f1, f3, f4, f5, f6))
    yield ~Polynomial((1.0, s1))
    yield ~Polynomial((1.0, s1))
    yield ~Polynomial((1.0, s3))
    yield ~Polynomial((1.0, s4))
    yield ~Polynomial((1.0, s5))
    yield ~Polynomial((1.0, s6))


def _transfer_function(generator):
    """An internal helper function, that expects a generator and returns a transfer
    function for one channel of the weighting filter.

    This function generates the product of the filter terms, that are created with
    the generator and adds a normalization factor, so that the gain of the filter
    is 0dB at the reference frequency of 1000Hz.
    """
    fr = 1000.0
    sr = S(fr)
    transfer_functions = tuple(generator(fr))
    gain = numpy.prod([tf(sr) for tf in transfer_functions])
    normalization = Constant(1.0 / gain)
    return Product((normalization, *transfer_functions))


class AWeighting(Filter):
    """Implementation of a A-weighting filter like it is defined in IEC 61672-1."""

    def __init__(self):
        Filter.__init__(self, transfer_functions=(_transfer_function(_a_factors),), labels=("A-weighting",))


class BWeighting(Filter):
    """Implementation of a B-weighting filter similar to how it was defined in IEC 61672-1.

    The exact frequencies for the poles near 20.6Hz and 12.2kHz are computed with
    the formulas from IEC 61672-1. For the pole at 158.5Hz this rounded frequency
    value is used.
    """

    def __init__(self):
        Filter.__init__(self, transfer_functions=(_transfer_function(_b_factors),), labels=("B-weighting",))


class CWeighting(Filter):
    """Implementation of a C-weighting filter like it is defined in IEC 61672-1."""

    def __init__(self):
        Filter.__init__(self, transfer_functions=(_transfer_function(_c_factors),), labels=("C-weighting",))


class DWeighting(Filter):
    """Implementation of a D-weighting filter.

    This weighting was developed for measurements of aircraft noise, but it is
    rarely used nowadays.
    """

    def __init__(self):
        Filter.__init__(self, transfer_functions=(_transfer_function(_d_factors),), labels=("D-weighting",))


class UWeighting(Filter):
    """Implementation of a U-weighting filter like it is defined in IEC 61012.

    This filter is used in combination with other weighting filter in order to
    remove ultrasonic frequency content.
    """

    def __init__(self):
        Filter.__init__(self, transfer_functions=(_transfer_function(_u_factors),), labels=("U-weighting",))
