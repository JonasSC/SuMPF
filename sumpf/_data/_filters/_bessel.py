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

"""Contains the class for a Bessel filter."""

import math
from ._base import frequency_scaling, RolloffFilter

__all__ = ("BesselFilter",)


def bessel(cutoff_frequency, order, highpass):
    """A helper function for creating the transfer function of a Bessel filter.

    :param cutoff_frequency: the cutoff frequency of the filter in Hz
    :param order: the filter order as an integer
    :param highpass: True, if a lowpass-to-highpass-transformation shall be done, False otherwise
    """
    k = frequency_scaling(cutoff_frequency=cutoff_frequency, highpass=highpass)
    coefficients = []
    c0 = math.factorial(2 * order) // (2 ** order * math.factorial(order))
    for i in range(order, 0, -1):
        oi = order - i
        c = math.factorial(order + oi) // (2 ** oi * math.factorial(i) * math.factorial(oi))
        coefficients.append(c / c0 * k ** i)
    coefficients.append(1.0)
    return BesselFilter.Constant(1.0) / BesselFilter.Polynomial(coefficients, transform=highpass)


class BesselFilter(RolloffFilter):
    """Implementation of a Bessel filter.
    Bessel filters are optimized for a flat frequency response and a constant group
    delay in the pass band.

    Be aware, that the definition of the cutoff frequency is different for Butterworth
    and Bessel filters. While with a Butterworth filter, the cutoff frequency
    refers to the magnitude of the filter's transfer function, the cutoff frequency
    of a Bessel filter specifies the region, in which the filter has a relatively
    constant group delay. This usually makes it necessary to specify a considerably
    lower cutoff frequency for Bessel lowpass filters than for the other IIR filters
    (for highpass filters, it is the other way around).

    This filter does not decompose its transfer function into a sequence of
    second order filters, so it might be inaccurate for high filter orders and
    high frequencies due to numerical instabilities.
    """

    def __init__(self, cutoff_frequency=1000.0, order=1, highpass=False):
        """
        :param cutoff_frequency: the cutoff frequency (-3dB threshold) of the filter in Hz
        :param order: the filter order as an integer
        :param highpass: True, if a lowpass-to-highpass-transformation shall be done, False otherwise
        """
        RolloffFilter.__init__(self,
                               transfer_function=bessel(cutoff_frequency=cutoff_frequency,
                                                        order=order,
                                                        highpass=highpass),
                               label="Bessel",
                               cutoff_frequency=cutoff_frequency,
                               order=order,
                               highpass=highpass)
