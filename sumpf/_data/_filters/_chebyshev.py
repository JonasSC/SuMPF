# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2020 Jonas Schulte-Coerne
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

"""Contains the classes for Chebyshev filters."""

import math
from ._base import frequency_scaling, RolloffFilter
from ._butterworth import butterworth

__all__ = ("Chebyshev1Filter",)


def chebyshev1(cutoff_frequency, ripple, order, highpass):
    """A helper function for creating the transfer function of a Chebyshev Type 1 filter.

    :param cutoff_frequency: the cutoff frequency of the filter in Hz
    :param ripple: the allowed passband ripple in dB
    :param order: the filter order as an integer
    :param highpass: True, if a lowpass-to-highpass-transformation shall be done, False otherwise
    """
    k = frequency_scaling(cutoff_frequency=cutoff_frequency, highpass=highpass)
    k2 = k ** 2
    factors = []
    # precompute coefficients
    g = math.asinh(1.0 / math.sqrt(10.0 ** (abs(ripple) / 10.0) - 1.0)) / order
    sinhg = math.sinh(g)
    cosh2g = math.cosh(g) ** 2
    # generate the transfer function
    if order % 2 == 0:
        pb2o = math.pi / (2 * order)
        for i in range(1, order // 2 + 1):
            b2 = 1.0 / (cosh2g - (math.cos((2 * i - 1) * pb2o) ** 2))
            b1 = 2.0 * b2 * sinhg * math.cos((2 * i - 1) * pb2o)
            factors.append(Chebyshev1Filter.Polynomial((b2 * k2, b1 * k, 1.0)))
    else:
        pbo = math.pi / order
        b1 = 1.0 / sinhg
        factors.append(Chebyshev1Filter.Polynomial((b1 * k, 1.0)))
        for i in range(2, (order + 1) // 2 + 1):
            b2 = 1.0 / (cosh2g - (math.cos((i - 1) * pbo) ** 2))
            b1 = 2.0 * b2 * sinhg * math.cos((i - 1) * pbo)
            factors.append(Chebyshev1Filter.Polynomial((b2 * k2, b1 * k, 1.0)))
    return ~Chebyshev1Filter.Product(factors=factors, transform=highpass)


class Chebyshev1Filter(RolloffFilter):
    """Implementation of a Chebyshev Type 1 filter.

    Be aware, that the definition of the cutoff frequency is different for Butterworth
    and Chebyshev filters. While with a Butterworth filter, the cutoff frequency
    is the frequency, where the magnitude of the filter's transfer function falls
    below -3dB, the transfer function of a Chebyshev falls below 1.0 (for even order
    filters) or below the passband ripple (for odd order filters).

    If the passband ripple is set to 0.0dB, a Butterworth filter will be generated.
    This might cause a jump in the cutoff frequency compared to a Chebyshev filter
    with a very small passband ripple, because of the difference in the definition
    of the cutoff frequency.
    """

    def __init__(self, cutoff_frequency=1000.0, ripple=3.0, order=1, highpass=False):
        """
        :param cutoff_frequency: the cutoff frequency of the filter in Hz
        :param ripple: the allowed passband ripple in dB
        :param order: the filter order as an integer
        :param highpass: True, if a lowpass-to-highpass-transformation shall be done, False otherwise
        """
        if ripple:
            transfer_function = chebyshev1(cutoff_frequency=cutoff_frequency,
                                           ripple=ripple,
                                           order=order,
                                           highpass=highpass)
        else:
            transfer_function = butterworth(cutoff_frequency=cutoff_frequency,
                                            order=order,
                                            highpass=highpass)
        RolloffFilter.__init__(self,
                               transfer_function=transfer_function,
                               label="Chebyshev 1",
                               cutoff_frequency=cutoff_frequency,
                               order=order,
                               highpass=highpass)
        self.__ripple = ripple

    def ripple(self):
        """Returns the passband ripple of the filter.

        :returns: a float
        """
        return self.__ripple
