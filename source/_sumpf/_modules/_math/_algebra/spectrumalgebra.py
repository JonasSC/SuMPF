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

import sumpf
from . import spectrumalgebrabase


class AddSpectrums(spectrumalgebrabase.SpectrumAlgebra):
    """
    A module for adding two Spectrums.
    The input Spectrums must have the same length, resolution and channel count.

    The two input Spectrums will be added channel per channel and sample per sample:
        spectrum1 = sumpf.Spectrum(channels = ((1, 2), (3, 4)))
        spectrum2 = sumpf.Spectrum(channels = ((5, 6), (7, 8)))
        spectrum1 + spectrum2 == sumpf.Spectrum(channels=((1+5, 2+6), (3+7, 4+8)))
    """
    def _Calculate(self, spectrum1, spectrum2):
        """
        Does the actual calculation.
        @param spectrum1: the first Spectrum for the calculation
        @param spectrum2: the second Spectrum for the calculation
        """
        return spectrum1 + spectrum2



class SubtractSpectrums(spectrumalgebrabase.SpectrumAlgebra):
    """
    A module for subtracting two Spectrums.
    The second Spectrum will be subtracted from the first one.
    The input Spectrums must have the same length, resolution and channel count.

    The two input Spectrums will be subtracted channel per channel and sample per sample:
        spectrum1 = sumpf.Spectrum(channels = ((1, 2), (3, 4)))
        spectrum2 = sumpf.Spectrum(channels = ((5, 6), (7, 8)))
        spectrum1 - spectrum2 == sumpf.Spectrum(channels=((1-5, 2-6), (3-7, 4-8)))
    """
    def _Calculate(self, spectrum1, spectrum2):
        """
        Does the actual calculation.
        @param spectrum1: the first Spectrum for the calculation
        @param spectrum2: the second Spectrum for the calculation
        """
        return spectrum1 - spectrum2



class MultiplySpectrums(spectrumalgebrabase.SpectrumAlgebra):
    """
    A module for multiplying two Spectrums.
    The input Spectrums must have the same length, resolution and channel count.

    The two input Spectrums will be multiplied channel per channel and sample per sample:
        spectrum1 = sumpf.Spectrum(channels = ((1, 2), (3, 4)))
        spectrum2 = sumpf.Spectrum(channels = ((5, 6), (7, 8)))
        spectrum1 * spectrum2 == sumpf.Spectrum(channels=((1*5, 2*6), (3*7, 4*8)))
    """
    def _Calculate(self, spectrum1, spectrum2):
        """
        Does the actual calculation.
        @param spectrum1: the first Spectrum for the calculation
        @param spectrum2: the second Spectrum for the calculation
        """
        return spectrum1 * spectrum2



class DivideSpectrums(spectrumalgebrabase.SpectrumAlgebra):
    """
    A module for dividing two Spectrums.
    The first Spectrum will be divided by the first one.
    The input Spectrums must have the same length, resolution and channel count.
    If both Spectrums are empty, an empty Spectrum is returned instead of raising
    an error.

    The two input Spectrums will be divided channel per channel and sample per sample:
        spectrum1 = sumpf.Spectrum(channels = ((1, 2), (3, 4)))
        spectrum2 = sumpf.Spectrum(channels = ((5, 6), (7, 8)))
        spectrum1 / spectrum2 == sumpf.Spectrum(channels=((1/5, 2/6), (3/7, 4/8)))
    """
    def _Calculate(self, spectrum1, spectrum2):
        """
        Does the actual calculation.
        @param spectrum1: the first Spectrum for the calculation
        @param spectrum2: the second Spectrum for the calculation
        """
        if spectrum1.IsEmpty() and spectrum2.IsEmpty():
            return sumpf.Spectrum(channels=((0.0, 0.0),) * len(spectrum1.GetChannels()), resolution=spectrum1.GetResolution())
        else:
            return spectrum1 / spectrum2

