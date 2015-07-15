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

import collections
import math
import sumpf
from .spectrumgenerator import SpectrumGenerator


class WeightingFilterGenerator(SpectrumGenerator):
    """
    Objects of this class generate a filter according to a given weighting function.
    Currently, the A- and the C-Weighting functions are implemented, but other
    weighting functions can be passed to the SetWeighting method.
    The weighting function is normalized to have a magnitude of one at 1000Hz
    """
    def __init__(self, weighting=None, resolution=None, length=None):
        """
        @param weighting: the weighting function, e.g. WeightingFilterGenerator.A or WeightingFilterGenerator.C (defaults to A-Weighting)
        @param resolution: the resolution of the created spectrum in Hz
        @param length: the number of samples of the spectrum
        """
        SpectrumGenerator.__init__(self, resolution=resolution, length=length)
        if weighting is None:
            self.__weighting = WeightingFilterGenerator.A
        else:
            self.__weighting = weighting
        self.__factor = 1.0

    @staticmethod
    def A(f):
        """
        The filter function for the A-Weighting. This can be passed to the
        SetWeighting method.
        This function's results are not normalized to be one at 1000Hz.
        @param f: the frequency as a float in Hz for which the factor shall be returned
        @retval : the weighting factor as a float for the given frequency
        """
        s = 2.0j * math.pi * f
        omega1 = -20.6 * 2.0 * math.pi
        omega2 = -107.7 * 2.0 * math.pi
        omega3 = -737.9 * 2.0 * math.pi
        omega4 = -12200.0 * 2.0 * math.pi
        pole1 = (s - omega1) ** 2
        pole2 = s - omega2
        pole3 = s - omega3
        pole4 = (s - omega4) ** 2
        return s ** 4 / (pole1 * pole2 * pole3 * pole4)

    @staticmethod
    def C(f):
        """
        The filter function for the C-Weighting. This can be passed to the
        SetWeighting method.
        This function's results are not normalized to be one at 1000Hz.
        @param f: the frequency as a float in Hz for which the factor shall be returned
        @retval : the weighting factor as a float for the given frequency
        """
        s = 2.0j * math.pi * f
        omega1 = -20.6 * 2.0 * math.pi
        omega2 = -12200 * 2.0 * math.pi
        pole1 = (s - omega1) ** 2
        pole2 = (s - omega2) ** 2
        return s ** 2 / (pole1 * pole2)

    @sumpf.Input(collections.Callable, "GetSpectrum")
    def SetWeighting(self, weighting):
        """
        Specifies the weighting function
        @param weighting: a weighting function, e.g. WeightingFilterGenerator.A or WeightingFilterGenerator.C
        """
        self.__weighting = weighting

    def _GetSamples(self):
        """
        Override of the SpectrumGenerator._GetSamples method in order to calculate
        the weighting factor before computing the actual samples.
        @retval : a tuple of samples
        """
        self.__factor = 1.0 / self.__weighting(1000.0)
        return SpectrumGenerator._GetSamples(self)

    def _GetSample(self, f):
        """
        Defines the value for each sample
        @param f: the frequency of the sample in Hz
        @retval : the value of the generator function at the given frequency
        """
        return self.__factor * self.__weighting(f)

    def _GetLabel(self):
        """
        Defines the label.
        @retval : a string label
        """
        return "Weighting"

