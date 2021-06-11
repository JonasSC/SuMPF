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

"""Contains the class for a Butterworth filter."""

import math
from ._base import frequency_scaling, RolloffFilter

__all__ = ("ButterworthFilter",)


def butterworth(cutoff_frequency, order, highpass):
    """A helper function for creating the transfer function of a Butterworth filter.

    :param cutoff_frequency: the cutoff frequency of the filter in Hz
    :param order: the filter order as an integer
    :param highpass: True, if a lowpass-to-highpass-transformation shall be done, False otherwise
    """
    k = frequency_scaling(cutoff_frequency=cutoff_frequency, highpass=highpass)
    k2 = k ** 2
    factors = []
    if order % 2 == 0:
        for i in range(1, order // 2 + 1):
            b1 = 2.0 * math.cos((2 * i - 1) * math.pi / (2 * order))
            factors.append(ButterworthFilter.Polynomial((k2, b1 * k, 1.0)))
    else:
        factors.append(ButterworthFilter.Polynomial((k, 1.0)))
        for i in range(2, (order + 1) // 2 + 1):
            b1 = 2.0 * math.cos((i - 1) * math.pi / order)
            factors.append(ButterworthFilter.Polynomial((k2, b1 * k, 1.0)))
    return ~ButterworthFilter.Product(factors=factors, transform=highpass)


class ButterworthFilter(RolloffFilter):
    """Implementation of a Butterworth filter.
    Butterworth filters are optimized for a fast transition between the pass band
    and the stop band, while maintaining a monotonic magnitude response.
    """

    def __init__(self, cutoff_frequency=1000.0, order=1, highpass=False):
        """
        :param cutoff_frequency: the cutoff frequency (-3dB threshold) of the filter in Hz
        :param order: the filter order as an integer
        :param highpass: True, if a lowpass-to-highpass-transformation shall be done, False otherwise
        """
        RolloffFilter.__init__(self,
                               transfer_function=butterworth(cutoff_frequency=cutoff_frequency,
                                                             order=order,
                                                             highpass=highpass),
                               label="Butterworth",
                               cutoff_frequency=cutoff_frequency,
                               order=order,
                               highpass=highpass)
