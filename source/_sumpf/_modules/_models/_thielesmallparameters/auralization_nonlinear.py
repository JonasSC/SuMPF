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
from .auralization_base import ThieleSmallParameterAuralization


class ThieleSmallParameterAuralizationNonlinear(ThieleSmallParameterAuralization):
	"""
	Synthesizes loudspeaker responses to a given input voltage signal.
	These responses can be the membrane displacement, the membrane velocity, the
	membrane acceleration, the input current and the generated sound pressure
	at a given distance.

	This synthesis also simulates nonlinear effects, which are caused by loudspeaker
	parameters that change with the membrane displacement or the membrane velocity.
	Frequency or temperature dependencies of parameters are not considered in
	this simulation.

	The simulation is implemented as an IIR-filter in the z-domain, that updates
	the displacement and velocity dependent parameters for each sample with the
	displacement and velocity that has been calculated for the previous sample.

	The formula for the IIR-filter has been calculated by using the bilinear transform
	on the voltage-to-displacement transfer function in the Laplace domain. Due
	to the non-infinite sampling rate, this causes an error in the high frequencies
	of the output signals.
	"""
	def __init__(self, thiele_small_parameters=sumpf.ThieleSmallParameters(), voltage_signal=None, listener_distance=1.0, medium_density=1.2041):
		"""
		@param thiele_small_parameters: a ThieleSmallParameters instance
		@param voltage_signal: a signal for the input voltage of the loudspeaker
		@param listener_distance: a float value for the distance between the loudspeaker and the point where the radiated sound is received in meters
		@param medium_density: a float value for the density of the medium, in which the loudspeaker radiates sound (probably air) in kilograms per cubic meter
		"""
		ThieleSmallParameterAuralization.__init__(self, thiele_small_parameters=thiele_small_parameters, voltage_signal=voltage_signal, listener_distance=listener_distance, medium_density=medium_density)
		# parameters that are precalculated to speed up the calculation
		self.__length = None
		self.__fs = None
		self.__fs2 = None
		self.__fs3 = None
		self.__2fs = None
		self.__4fs2 = None
		self.__8fs2 = None
		self.__8fs3 = None
		self.__4fs3 = None
		self.__4pi = None
		self._Precalculate()

	def _Precalculate(self):
		"""
		Calculates some values to speed up the actual simulation step.
		"""
		self.__length = len(self._voltage.GetChannels()[0]) + 4
		self.__fs = self._voltage.GetSamplingRate()
		self.__fs2 = self.__fs ** 2
		self.__fs3 = self.__fs ** 3
		self.__2fs = 2.0 * self.__fs
		self.__4fs2 = 4.0 * self.__fs2
		self.__8fs2 = 8.0 * self.__fs2
		self.__4fs3 = 4.0 * self.__fs3
		self.__8fs3 = 8.0 * self.__fs3
		self.__4pi = 4.0 * math.pi

	def _Recalculate(self):
		"""
		Calculates the channels for the displacement, velocity and acceleration
		of the membrane and for the input current and the generated sound pressure.
		@retval the channel data displacement_channels, velocity_channels, acceleration_channels, current_channels, sound_pressure_channels
		"""
		# make class variables local
		__length = self.__length
		__fs = self.__fs
		__fs2 = self.__fs2
		__fs3 = self.__fs3
		__2fs = self.__2fs
		__4fs2 = self.__4fs2
		__8fs2 = self.__8fs2
		__4fs3 = self.__4fs3
		__8fs3 = self.__8fs3
		__4pi = self.__4pi
		_thiele_small = self._thiele_small
		r = self._listener_distance
		rho = self._medium_density
		# start the calculation
		displacement_channels = []
		velocity_channels = []
		acceleration_channels = []
		current_channels = []
		sound_pressure_channels = []
		for c in self._voltage.GetChannels():
			voltage = (0.0,) * 4 + c
			displacement = [0.0] * __length
			velocity = [0.0] * __length
			acceleration = [0.0] * __length
			current = [0.0] * __length
			sound_pressure = [0.0] * __length
			for i in range(4, len(voltage)):
				f = 0.0
				x = displacement[i - 1]
				v = velocity[i - 1]
				t = None
				# get the Thiele Small parameters
				R = _thiele_small.GetVoiceCoilResistance(f, x, v, t)
				L = _thiele_small.GetVoiceCoilInductance(f, x, v, t)
				M = _thiele_small.GetForceFactor(f, x, v, t)
				k = _thiele_small.GetSuspensionStiffness(f, x, v, t)
				w = _thiele_small.GetMechanicalDamping(f, x, v, t)
				m = _thiele_small.GetMembraneMass(f, x, v, t)
				S = _thiele_small.GetMembraneArea(f, x, v, t)
				# precalculate some values for the displacement calculation
				Lm = L * m
				Lw = L * w
				Lk = L * k
				Rm = R * m
				Rw = R * w
				Rk = R * k
				M2 = M * M
				LwRm = Lw + Rm
				LkM2Rw = Lk + M2 + Rw
				factor = 1.0 / (Rk + __8fs3 * Lm + __4fs2 * LwRm + __2fs * LkM2Rw)
				factor4 = 4.0 * factor
				# calculate the filter coefficients for the displacement calculation
				a0 = factor * M
				a1 = factor4 * M
				a2 = 6.0 * a0
				a3 = a1
				a4 = a0
				b1 = factor4 * (Rk - __4fs3 * Lm + __fs * LkM2Rw)
				b2 = factor * (6.0 * Rk - __8fs2 * LwRm)
				b3 = factor4 * (Rk + __4fs3 * Lm - __fs * LkM2Rw)
				b4 = factor * (Rk - __8fs3 * Lm + __4fs2 * LwRm - __2fs * LkM2Rw)
				displacement[i] = a0 * voltage[i] + a1 * voltage[i - 1] + a2 * voltage[i - 2] + a3 * voltage[i - 3] + a4 * voltage[i - 4] - b1 * displacement[i - 1] - b2 * displacement[i - 2] - b3 * displacement[i - 3] - b4 * displacement[i - 4]
				# calculate the velocity, the acceleration, the current and the sound pressure
				velocity[i] = __2fs * displacement[i] - __2fs * displacement[i - 1] - velocity[i - 1]
				acceleration[i] = __2fs * velocity[i] - __2fs * velocity[i - 1] - acceleration[i - 1]
				current[i] = (k * displacement[i] + w * velocity[i] + m * acceleration[i]) / M
				sound_pressure[i] = (rho * acceleration[i] * S) / (__4pi * r)
			# store the Signals
			displacement_channels.append(tuple(displacement[4:]))
			velocity_channels.append(tuple(velocity[4:]))
			acceleration_channels.append(tuple(acceleration[4:]))
			current_channels.append(tuple(current[4:]))
			sound_pressure_channels.append(tuple(sound_pressure[4:]))
		return displacement_channels, velocity_channels, acceleration_channels, current_channels, sound_pressure_channels

