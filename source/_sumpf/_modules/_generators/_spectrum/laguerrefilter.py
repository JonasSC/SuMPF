# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2015 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import math
import sumpf
from .filterwithcoefficients import FilterWithCoefficients


class LaguerreFilterGenerator(FilterWithCoefficients):
    """
    A generator class that creates Laguerre functions in the frequency domain.
    Due to properties of the implementation of the fourier transform, which is
    used by SuMPF, the time domain data of the Laguerre functions, that are created
    by inverse transforming the output of this filter class, has to be scaled with
    the sampling rate of that time domain data to have the same magnitude as the
    Laguerre functions, which have been created in the time domain with the
    LaguerreFilterGenerator class.
    """
    def __init__(self, order=0, scaling_factor=1.0, resolution=None, length=None):
        """
        @param order: the order of the generated Laguerre function as an integer
        @param scaling_factor: the scaling factor for the Laguerre function as a float
        @param resolution: the resolution of the created spectrum in Hz
        @param length: the number of samples of the spectrum
        """
        FilterWithCoefficients.__init__(self, frequency=1.0 / (2.0 * math.pi), transform=False, resolution=resolution, length=length)
        self.__order = order
        self.__scaling_factor = scaling_factor

    @sumpf.Input(int, "GetSpectrum")
    def SetOrder(self, order):
        """
        Sets the order for the Laguerre function.
        The order is equal to the number of times, which the function crosses
        the x (or time) axis in the time domain. With an order of 0, the Laguerre
        function will fall monotonously and converge to 0.0 for a raising x (or
        time) value.
        With an order of 1, the Laguerre function will start below zero, cross
        the x (or time) axis, raise to a positive maximum and converge to 0.0
        from there. A second order Laguerre function will cross the x (or time)
        axis twice, a third order one three times and so on.
        @param order: the order of the generated Laguerre function as an integer
        """
        self.__order = order

    @sumpf.Input(float, "GetSpectrum")
    def SetScalingFactor(self, scaling_factor):
        """
        Sets the scaling factor for the Laguerre function.
        A large scaling factor compresses the generated function in time, but
        increases the amplitude of the Laguerre function.
        @param scaling_factor: the scaling factor for the Laguerre function as a float
        """
        self.__scaling_factor = float(scaling_factor)

    def _GetCoefficients(self):
        """
        Calculates the coefficients for the Laguerre function.
        @retval : a list of tuples (a, b) where a and b are lists of coefficients
        """
        p = self.__scaling_factor
        coefficients = []
        numerator = [(2.0 * p) ** 0.5]
        denominator = [p, 1.0]
        coefficients.append((numerator, denominator))
        numerator = [p, -1.0]
        for o in range(0, self.__order):
            coefficients.append((numerator, denominator))
        return coefficients

    def _GetLabel(self):
        """
        Returns the label for the generated channel.
        @retval : the string label
        """
        return "%s order Laguerre" % sumpf.helper.counting_number(self.__order)

