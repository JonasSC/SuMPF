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

import math
import sumpf
import numpy	# the ThieleSmallParameterAuralizationLinear class needs NumPy for the fourier transforms, so importing this file shall fail, when NumPy is not available
from .auralization_base import ThieleSmallParameterAuralization


class ThieleSmallParameterAuralizationLinear(ThieleSmallParameterAuralization):
	"""
	Synthesizes loudspeaker responses to a given input voltage signal.
	These responses can be the membrane excursion, the membrane velocity, the
	membrane acceleration, the input current and the generated sound pressure
	at a given distance.

	The simulation is implemented as an IIR-filter in the frequency domain.
	This implementation would allow to consider frequency dependencies of the
	loudspeaker's parameters, like a model of the suspension creep. This feature
	is not implemented (yet).
	"""
	def _Recalculate(self):
		"""
		Calculates the channels for the excursion, velocity and acceleration
		of the membrane and for the input current and the generated sound pressure.
		@retval the channel data excursion_channels, velocity_channels, acceleration_channels, current_channels, sound_pressure_channels
		"""
		# get the Thiele Small parameters
		R = self._thiele_small.GetVoiceCoilResistance()
		m = self._thiele_small.GetMembraneMass()
		L = self._thiele_small.GetVoiceCoilInductance()
		M = self._thiele_small.GetForceFactor()
		k = self._thiele_small.GetSuspensionStiffness()
		w = self._thiele_small.GetMechanicalDamping()
		S = self._thiele_small.GetMembraneArea()
		r = self._listener_distance
		rho = self._medium_density
		# set up filters
		spectrum = sumpf.modules.FourierTransform(signal=self._voltage).GetSpectrum()
		numerator = (M,)
		denominator = (R * k, L * k + R * w + M ** 2, L * w + R * m, L * m)
		excursion_filter = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.FILTER_WITH_COEFFICIENTS(frequency=1.0 / (2.0 * math.pi),
		                                                                                                                       coefficients=((numerator, denominator),),
		                                                                                                                       transform=False),
		                                                 resolution=spectrum.GetResolution(),
		                                                 length=len(spectrum)).GetSpectrum()
		derivative_filter = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.FILTER_WITH_COEFFICIENTS(frequency=1.0 / (2.0 * math.pi),
		                                                                                                                        coefficients=(((0.0, 1.0), (1.0,)),),
		                                                                                                                        transform=False),
		                                                  resolution=spectrum.GetResolution(),
		                                                  length=len(spectrum)).GetSpectrum()
		# calculate the output data for each channel
		excursion_channels = []
		velocity_channels = []
		acceleration_channels = []
		current_channels = []
		sound_pressure_channels = []
		for c in range(len(spectrum.GetChannels())):
			channel = sumpf.modules.SplitSpectrum(data=spectrum, channels=[c]).GetOutput()
			excursion_spectrum = channel * excursion_filter
			excursion_channels.append(sumpf.modules.InverseFourierTransform(spectrum=excursion_spectrum).GetSignal().GetChannels()[0])
			velocity_spectrum = excursion_spectrum * derivative_filter
			velocity_channels.append(sumpf.modules.InverseFourierTransform(spectrum=velocity_spectrum).GetSignal().GetChannels()[0])
			acceleration_spectrum = velocity_spectrum * derivative_filter
			acceleration_channels.append(sumpf.modules.InverseFourierTransform(spectrum=acceleration_spectrum).GetSignal().GetChannels()[0])
			current_spectrum = (k * excursion_spectrum + w * velocity_spectrum + m * acceleration_spectrum) / M
			current_channels.append(sumpf.modules.InverseFourierTransform(spectrum=current_spectrum).GetSignal().GetChannels()[0])
			sound_pressure_spectrum = acceleration_spectrum * rho * S / (4.0 * math.pi * r)
			sound_pressure_channels.append(sumpf.modules.InverseFourierTransform(spectrum=sound_pressure_spectrum).GetSignal().GetChannels()[0])
		return excursion_channels, velocity_channels, acceleration_channels, current_channels, sound_pressure_channels
