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

from .spectrumgenerator import SpectrumGenerator


class FilterWithCoefficients(SpectrumGenerator):
    """
    An abstract base class for filter classes that generate the complex weighting
    factor for a given frequency, from a set of laplace coefficients.
    The coefficients shall be a list of tuples (a, b) where a is the list of
    coefficients for the numerator and b is the list of coefficients for the
    denominator.
    As many filter polynomials give their coefficients in product form, this
    method takes a list of tuples. The polynomials created from these tuples
    will be multiplied.

    In pseudo Python and even more pseudo Mathematics:
    n := len(coefficients)
    G(s) := the transfer function of the complete filter
    wc := the cutoff frequency in radians (2*pi*self.__frequency)
    then is:
    G(s) = G0(s) * G1(s) * G2(s) * ... Gi(s) ... * Gn(s)
    with:
    a = coefficients[i][0]
    b = coefficients[i][1]
    Gi(s) = (a[0] + (s/wc)*a[1] + ((s/wc)**2)*a[2] + ...) / (b[0] + (s/wc)*b[1] + ((s/wc)**2)*b[2] + ...)
    or with lowpass-to-highpass-transformation:
    Gi(s) = (a[0] + (wc/s)*a[1] + ((wc/s)**2)*a[2] + ...) / (b[0] + (wc/s)*b[1] + ((wc/s)**2)*b[2] + ...)
    """
    def __init__(self, frequency, transform, resolution, length):
        """
        @param frequency: the corner or resonant frequency of the filter
        @param transform: True, if a lowpass-to-highpass transformation shall be made. False otherwise
        @param resolution: the resolution of the created spectrum in Hz
        @param length: the number of samples of the spectrum
        """
        SpectrumGenerator.__init__(self, resolution=resolution, length=length)
        self._frequency = frequency
        self.__coefficients = ()
        self._transform = transform

    def _GetCoefficients(self):
        """
        A virtual method, that is called prior to the generation of the samples,
        in order to generate the coefficients for the filter.
        This method must be overridden in derived classes.
        @retval : a list of tuples (a, b) where a and b are lists of coefficients
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def _GetSamples(self):
        """
        Override of the SpectrumGenerator._GetSamples method in order to calculate
        the filter coefficients before computing the actual samples.
        @retval : a tuple of samples
        """
        self.__coefficients = self._GetCoefficients()
        return SpectrumGenerator._GetSamples(self)

    def _GetSample(self, f):
        """
        This calculates the complex factor by which the frequency shall be scaled
        and phase shifted.
        @param frequency: the frequency for which the factor shall be calculated
        @param resolution: the resolution of the calculated spectrum
        @param length: the length of the calculated spectrum
        @retval : the value of the filter's transfer function at the given frequency
        """
        s = 1.0j * f / self._frequency
        sample = 1.0
        if self._transform:
            if f == 0.0:
                return 0.0
            else:
                s = 1.0 / s
        for c in self.__coefficients:
            numerator = 0.0
            for i in range(len(c[0])):
                numerator += c[0][i] * (s ** i)
            denominator = 0.0
            for i in range(len(c[1])):
                denominator += c[1][i] * (s ** i)
            sample *= numerator / denominator
        return sample

