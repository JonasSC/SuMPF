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


########################
# the filter functions #
########################


class FilterFunction(object):
    """
    An abstract base class for filter functions that are defined by the coefficients
    of their Laplace transfer function.
    Derived classes of this must implement the GetCoefficients method, which returns
    the coefficients as a list of tuples (a, b), where a is a list of polynomial
    coefficients for the numerator and b is a list of coefficients for the denominator.
    Both a and b start with the coefficient for s**0.
    """
    def GetCoefficients(self):
        """
        This virtual method shall be overridden to generate the coefficients for
        the filter.
        @retval : a list of tuples (a, b) where a and b are lists of coefficients
        """
        raise NotImplementedError("This method should have been overridden in a derived class")



class Butterworth(FilterFunction):
    """
    A class that generates the coefficients for a Butterworth filter.
    """
    def __init__(self, order=1):
        """
        @param order: the order of the filter as an integer
        """
        self.__order = order

    def GetCoefficients(self):
        """
        Calculates the coefficients for the filter.
        @retval : a list of tuples (a, b) where a and b are lists of coefficients
        """
        coefficients = []
        n = float(self.__order)
        if self.__order % 2 == 0:
            for i in range(1, self.__order // 2 + 1):
                b1 = 2.0 * math.cos((2 * i - 1) * math.pi / (2 * n))
                coefficients.append(([1.0], [1.0, b1, 1.0]))
        else:
            coefficients.append(([1.0], [1.0, 1.0]))
            for i in range(2, (self.__order + 1) // 2 + 1):
                b1 = 2.0 * math.cos((i - 1) * math.pi / n)
                coefficients.append(([1.0], [1.0, b1, 1.0]))
        return coefficients



class Bessel(FilterFunction):
    """
    A class that generates the coefficients for a Bessel filter.
    """
    def __init__(self, order=1):
        """
        @param order: the order of the filter as an integer
        """
        self.__order = order

    def GetCoefficients(self):
        """
        Calculates the coefficients for the filter.
        @retval : a list of tuples (a, b) where a and b are lists of coefficients
        """
        coefficients = []
        for k in range(self.__order + 1):
            numerator = math.factorial(2.0 * self.__order - k)
            denominator = (2.0 ** (self.__order - k)) * math.factorial(k) * math.factorial(self.__order - k)
            coefficients.append(numerator / denominator)
        return [([coefficients[0]], coefficients)]



class Chebychev1(FilterFunction):
    """
    A class that generates the coefficients for a Chebychev filter of the first
    type. The ripple of the filter will occur in the stop band.
    """
    def __init__(self, order=1, ripple=3.0):
        """
        @param order: the order of the filter as an integer
        @param ripple: the float value of the maximum ripple in dB
        """
        self.__order = order
        self.__ripple = ripple

    def GetCoefficients(self):
        """
        Calculates the coefficients for the filter.
        @retval : a list of tuples (a, b) where a and b are lists of coefficients
        """
        coefficients = []
        n = float(self.__order)
        g = math.asinh(1.0 / (math.sqrt((10.0 ** (self.__ripple / 10.0)) - 1.0))) / n
        if self.__order % 2 == 0:
            for i in range(1, self.__order // 2 + 1):
                b2 = 1 / ((math.cosh(g) ** 2) - (math.cos((2 * i - 1) * math.pi / (2 * n)) ** 2))
                b1 = 2.0 * b2 * math.sinh(g) * math.cos((2 * i - 1) * math.pi / (2 * n))
                coefficients.append(([1.0], [1.0, b1, b2]))
        else:
            b1 = 1.0 / math.sinh(g)
            coefficients.append(([1.0], [1.0, b1]))
            for i in range(2, (self.__order + 1) // 2 + 1):
                b2 = 1 / ((math.cosh(g) ** 2) - (math.cos((i - 1) * math.pi / n) ** 2))
                b1 = 2.0 * b2 * math.sinh(g) * math.cos((i - 1) * math.pi / n)
                coefficients.append(([1.0], [1.0, b1, b2]))
        return coefficients



class Bandpass(FilterFunction):
    """
    A class that generates the coefficients for a second order band pass that is
    normalized to have a gain of one at the resonant frequency.
    """
    def __init__(self, q_factor=1.0):
        """
        @param q_factor: the Q-factor of the resonance
        """
        self.__q_factor = q_factor

    def GetCoefficients(self):
        """
        Calculates the coefficients for the filter.
        @retval : a list of tuples (a, b) where a and b are lists of coefficients
        """
        a0 = 0.0
        a1 = 1.0 / float(self.__q_factor)
        b0 = 1.0
        b1 = a1
        b2 = 1.0
        return [([a0, a1], [b0, b1, b2])]



class Bandstop(FilterFunction):
    """
    A class that generates the coefficients for a second order band stop or notch filter.
    """
    def __init__(self, q_factor=1.0):
        """
        @param q_factor: the Q-factor of the resonance
        """
        self.__q_factor = q_factor

    def GetCoefficients(self):
        """
        Calculates the coefficients for the filter.
        @retval : a list of tuples (a, b) where a and b are lists of coefficients
        """
        a0 = 1.0
        a1 = 0.0
        a2 = 1.0
        b0 = 1.0
        b1 = 1.0 / self.__q_factor
        b2 = 1.0
        return [([a0, a1, a2], [b0, b1, b2])]



class TransferFunction(FilterFunction):
    """
    Takes two sequences of coefficients, that define a transfer function as a
    fraction in the laplace domain.
    The resulting transfer function G(s) is computed as follows:
      a0, a1, a2, ..., an = numerator   # the numerator sequence as it is passed to the constructor
      b0, b1, b2, ..., bn = denominator # the denominator sequence as it is passed to the constructor
      G(s) = (a0 + a1*s + a2*s**2 + ... + an*s**n) / (b0 + b1*s + b2*s**2 + ... + bn*s**n)
    """
    def __init__(self, numerator=[1.0], denominator=[1.0]):
        """
        @param numerator: a sequence of coefficients for the numerator polynomial
        @param denominator: a sequence of coefficients for the denominator polynomial
        """
        self.__numerator = numerator
        self.__denominator = denominator

    def GetCoefficients(self):
        """
        Returns the coefficients for the filter.
        @retval : a list of tuples (a, b) where a and b are lists of coefficients
        """
        return [(self.__numerator, self.__denominator)]



#######################
# the generator class #
#######################


class FilterGenerator(FilterWithCoefficients):
    """
    Objects of this class generate spectrums of IIR filters.
    """
    BUTTERWORTH = Butterworth
    BESSEL = Bessel
    CHEBYCHEV1 = Chebychev1
    BANDPASS = Bandpass
    BANDSTOP = Bandstop
    TRANSFERFUNCTION = TransferFunction

    def __init__(self, filterfunction=None, frequency=1000.0, transform=False, resolution=None, length=None):
        """
        @param filterfunction: an instance of the class, that defines the filter (e.g. FilterGenerator.BUTTERWORTH(order=1))
        @param frequency: the corner or resonance frequency of the filter as a float in Hz
        @param transform: True, if a lowpass-to-highpass transformation shall be performed. False otherwise
        @param resolution: the resolution of the created spectrum in Hz
        @param length: the number of samples of the spectrum
        """
        FilterWithCoefficients.__init__(self, frequency=frequency, transform=transform, resolution=resolution, length=length)
        if filterfunction is None:
            self.__filterfunction = Butterworth(order=1)
        else:
            self.__filterfunction = filterfunction

    @sumpf.Input(FilterFunction, "GetSpectrum")
    def SetFilterFunction(self, function):
        """
        Specifies the function, that defines the filter.
        @param filterfunction: an instance of the class, that defines the filter (e.g. FilterGenerator.BUTTERWORTH(order=1))
        """
        self.__filterfunction = function

    @sumpf.Input(float, "GetSpectrum")
    def SetFrequency(self, frequency):
        """
        Sets the corner or resonance frequency of the filter.
        @param frequency: a frequency as a float in Hz
        """
        self._frequency = frequency

    @sumpf.Input(bool, "GetSpectrum")
    def SetTransform(self, transform):
        """
        Specifies, if a lowpass-to-highpass transformation shall be performed.
        @param transform: True, if the transformation shall be performed, False otherwise
        """
        self._transform = transform

    def _GetCoefficients(self):
        """
        Calculates the coefficients for the filter function.
        @retval : a list of tuples (a, b) where a and b are lists of coefficients
        """
        return self.__filterfunction.GetCoefficients()

    def _GetLabel(self):
        """
        Returns the label for the generated channel.
        @retval : the string label
        """
        return self.__filterfunction.__class__.__name__

