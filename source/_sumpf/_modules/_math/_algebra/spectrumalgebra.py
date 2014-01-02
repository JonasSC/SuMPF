# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2014 Jonas Schulte-Coerne
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

from . import algebra
from . import spectrumalgebrabase


class AddSpectrums(spectrumalgebrabase.SpectrumAlgebra, algebra.Add):
	"""
	A module for adding two Spectrums.

	The input Spectrums must have the same length and resolution.
	If one Spectrum has more channels than the other, the surplus channels will be
	left out of the resulting Spectrum.

	The two input Spectrums will be added channel per channel and sample per sample:
		spectrum1 = sumpf.Spectrum(channels = ((1, 2), (3, 4)))
		spectrum2 = sumpf.Spectrum(channels = ((5, 6), (7, 8)))
		spectrum1 + spectrum2 == sumpf.Spectrum(channels=((1+5, 2+6), (3+7, 4+8)))
	"""
	pass



class SubtractSpectrums(spectrumalgebrabase.SpectrumAlgebra, algebra.Subtract):
	"""
	A module for subtracting two Spectrums.
	The second Spectrum will be subtracted from the first one.

	The input Spectrums must have the same length and resolution.
	If one Spectrum has more channels than the other, the surplus channels will be
	left out of the resulting Spectrum.

	The two input Spectrums will be subtracted channel per channel and sample per sample:
		spectrum1 = sumpf.Spectrum(channels = ((1, 2), (3, 4)))
		spectrum2 = sumpf.Spectrum(channels = ((5, 6), (7, 8)))
		spectrum1 - spectrum2 == sumpf.Spectrum(channels=((1-5, 2-6), (3-7, 4-8)))
	"""
	pass



class MultiplySpectrums(spectrumalgebrabase.SpectrumAlgebra, algebra.Multiply):
	"""
	A module for multiplying two Spectrums.

	The input Spectrums must have the same length and resolution.
	If one Spectrum has more channels than the other, the surplus channels will be
	left out of the resulting Spectrum.

	The two input Spectrums will be multiplied channel per channel and sample per sample:
		spectrum1 = sumpf.Spectrum(channels = ((1, 2), (3, 4)))
		spectrum2 = sumpf.Spectrum(channels = ((5, 6), (7, 8)))
		spectrum1 * spectrum2 == sumpf.Spectrum(channels=((1*5, 2*6), (3*7, 4*8)))
	"""
	pass



class DivideSpectrums(spectrumalgebrabase.SpectrumAlgebra, algebra.Divide):
	"""
	A module for dividing two Spectrums.
	The first Spectrum will be divided by the first one.

	The input Spectrums must have the same length and resolution.
	If one Spectrum has more channels than the other, the surplus channels will be
	left out of the resulting Spectrum.

	A ZeroDivisionError is raised only, if a non zero channel (not all samples
	are 0.0) is divided by a zero channel.
	If a zero channel is divided by another zero channel, the resulting channel
	will be a channel of which all samples are 1.0. This avoids ZeroDivisionErrors
	with empty Spectrums, which cannot always be avoided during the initialization
	of a processing chain.

	The two input Spectrums will be divided channel per channel and sample per sample:
		spectrum1 = sumpf.Spectrum(channels = ((1, 2), (3, 4)))
		spectrum2 = sumpf.Spectrum(channels = ((5, 6), (7, 8)))
		spectrum1 / spectrum2 == sumpf.Spectrum(channels=((1/5, 2/6), (3/7, 4/8)))
	"""
	pass

