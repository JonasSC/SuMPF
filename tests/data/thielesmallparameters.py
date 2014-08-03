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

import unittest
import sumpf


class TestThieleSmallParameters(unittest.TestCase):
	def test_data(self):
		"""
		Tests if all data can be set and retrieved as expected.
		"""
		names = {"voicecoil_resistance": "GetVoiceCoilResistance",
		         "voicecoil_inductance": "GetVoiceCoilInductance",
		         "force_factor": "GetForceFactor",
		         "suspension_stiffness": "GetSuspensionStiffness",
		         "mechanical_damping": "GetMechanicalDamping",
		         "membrane_mass": "GetMembraneMass",
		         "membrane_area": "GetMembraneArea"}
		for n in names:
			# test constant values
			kwargs = {n: 37.7056}
			ts = sumpf.ThieleSmallParameters(**kwargs)
			self.assertEqual(getattr(ts, names[n])(), kwargs[n])
			self.assertEqual(getattr(ts, names[n])(frequency=440.1, membrane_excursion=0.6, membrane_velocity=4.03, voicecoil_temperature=29.4), kwargs[n])
			# test values that depend on the loudspeaker's state
			kwargs = {n: lambda f, x, v, t: f + x + v + t}
			ts = sumpf.ThieleSmallParameters(**kwargs)
			self.assertEqual(getattr(ts, names[n])(), 20.0)
			self.assertEqual(getattr(ts, names[n])(frequency=440.1, membrane_excursion=0.6, membrane_velocity=4.03, voicecoil_temperature=29.4), 474.13)

