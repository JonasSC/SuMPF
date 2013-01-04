# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2013 Jonas Schulte-Coerne
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
from .wavegenerator import WaveGenerator


class SquareWaveGenerator(WaveGenerator):
	"""
	A class whose instances generate square waves.
	The square waves can be modified with the same parameters as a sine wave.
	These parameters are the frequency and the phase, where the phase can be
	given either in radian or in degrees.
	When T is the period length (1.0/frequency), t is the current time index and
	the phase is 0.0, then the square wave is 1.0 in the interval 0.0 <= t < 0.5*T
	and -1.0 in the interval 0.5*T <= t < T. For t >= T this behavior is continued
	periodically.
	Unlike to a square wave definition by the sign of a sine wave, there are no
	undecided cases where a sample would be 0.0. The samples are always either 1.0
	or -1.0.
	The amplitude of the square wave will always be 1.0. It can be changed by
	sending the resulting Signal through a sumpf.AmplifySignal module.
	The resulting Signal will have one channel.
	"""
	def _GetSample(self, t):
		"""
		Calculates and returns the value of the sample at time t.
		This is sample is either 1.0 or -1.0.
		@param t: the time from the beginning of the signal in seconds
		@retval : the value of the square wave function at the given time
		"""
		x = t * self._frequency + self._phase / (2.0 * math.pi)
		if x - int(x) < 0.5:
			return 1.0
		else:
			return -1.0

	def _GetLabel(self):
		"""
		Returns the label for the generated channel.
		@retval : the string label
		"""
		return "Square"

