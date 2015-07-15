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
from .signalgenerator import SignalGenerator


class LaguerreFunctionGenerator(SignalGenerator):
    """
    This class is for creating Laguerre function Signals.
    The generated Signals can be either ordinary Laguerre functions or generalized
    Laguerre functions with an integer order of generalization.
    This is an implementation of the formula given in the IEEE-paper "Optimal
    parametrization of truncated generalized Laguerre series" by Harm Belt and
    Albertus den Brinker. The formula in the paper uses the gamma function in one
    term to allow arbitrary orders of generalization. To speed up the generation
    of the Laguerre functions, this implementation has replaced the gamma function
    with a simple factorial, which is why this implementation only accepts integer
    orders of generalization.
    Furthermore, the scaling factor in this implementation is the same as the
    factor "p" in the book "The Volterra and Wiener theory of nonlinear systems"
    by Martin Schetzen. This differs from the scaling factor "sigma" in the paper
    by a factor of two:
        scaling_factor = p = sigma / 2
    This decision has been made, so that the scaling factor in this class and
    the one for the generation of the Laguerre functions in the frequency domain
    are equivalent.
    """
    def __init__(self, order=0, scaling_factor=1.0, generalization_order=0, samplingrate=None, length=None):
        """
        @param order: the order of the generated Laguerre function as an integer
        @param scaling_factor: the scaling factor for the Laguerre function as a float
        @param generalization_order: the order of generalization for the generated Laguerre function as an integer
        @param samplingrate: the sampling rate in Hz
        @param length: the number of samples of the signal
        """
        SignalGenerator.__init__(self, samplingrate=samplingrate, length=length)
        self.__order = order
        self.__scaling_factor = float(scaling_factor)
        self.__generalization_order = generalization_order

    def _GetSamples(self):
        """
        Generates the samples of the Laguerre function and returns them as a tuple.
        @retval : a tuple of samples
        """
        m = self.__order
        sigma = self.__scaling_factor * 2.0
        alpha = self.__generalization_order
        # precalculate time independent term
        factor1 = (-1.0) ** m * (sigma * math.factorial(m) / math.factorial(m + alpha)) ** 0.5
        precalculated = []
        for n in range(m + 1):
            a = (-1.0) ** n
            b = sumpf.helper.binomial_coefficient(m + alpha, m - n)
            c = math.factorial(n)
            precalculated.append(a * b / c)
        # calculate the actual samples
        samples = []
        for i in range(self._length):
            t = float(i) / float(self._samplingrate)
            summed = 0.0
            for n in range(m + 1):
                c = ((sigma * t) ** (n + alpha / 2.0))
                summed += precalculated[n] * c
            factor2 = math.exp(-0.5 * sigma * t)
            samples.append(factor1 * factor2 * summed)
        return tuple(samples)

    def _GetLabel(self):
        """
        Returns the label for the generated channel.
        @retval : the string label
        """
        return "%s order Laguerre" % sumpf.helper.counting_number(self.__order)

    @sumpf.Input(int, "GetSignal")
    def SetOrder(self, order):
        """
        Sets the order for the Laguerre function.
        The order is equal to the number of times, which the function crosses
        the x (or time) axis. With an order of 0, the Laguerre function will
        fall monotonously and converge to 0.0 for a raising x (or time) value.
        With an order of 1, the Laguerre function will start below zero, cross
        the x (or time) axis, raise to a positive maximum and converge to 0.0
        from there. A second order Laguerre function will cross the x (or time)
        axis twice, a third order one three times and so on.
        @param order: the order of the generated Laguerre function as an integer
        """
        self.__order = order

    @sumpf.Input(float, "GetSignal")
    def SetScalingFactor(self, scaling_factor):
        """
        Sets the scaling factor for the Laguerre function.
        A large scaling factor compresses the generated function in time, but
        increases the amplitude of the Laguerre function.
        This scaling factor is the same as the coefficient "p" in the works of
        Martin Schetzen. Harm Belt and Albertus den Brinker used a different
        coefficient, called "sigma", in their works. The two factors can be converted
        easily:
            scaling_factor = p = sigma / 2
        @param scaling_factor: the scaling factor for the Laguerre function as a float
        """
        self.__scaling_factor = float(scaling_factor)

    @sumpf.Input(int, "GetSignal")
    def SetGeneralizationOrder(self, order):
        """
        Sets the order of generalization for the Laguerre function
        If the order of generalization is zero, the produced Laguerre functions
        are the ordinary non-generalized Laguerre functions. With an increased
        order of generalization, the initial maximum of the Laguerre function is
        shifted to later points in time.
        In this implementation, the order of generalization has to be an integer.
        This has been done to avoid further computational effort in the already
        slow generation of the Laguerre functions.
        @param generalization_order: the order of generalization for the generated Laguerre function as an integer
        """
        self.__generalization_order = order

