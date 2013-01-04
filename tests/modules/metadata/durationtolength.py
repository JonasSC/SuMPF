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

import unittest
import sumpf
import _common as common

class TestDurationToLength(unittest.TestCase):
	"""
	A TestCase for the TestDurationToLength module.
	"""
	def test_duration(self):
		"""
		Tests if the duration is calculated correctly
		"""
		d2l = sumpf.modules.DurationToLength()
		self.assertEqual(d2l.GetLength(), sumpf.config.get("default_signal_length"))
		d2l = sumpf.modules.DurationToLength(duration=1, samplingrate=22050)
		self.assertEqual(d2l.GetLength(), 22050)
		d2l.SetDuration(2.0)
		self.assertEqual(d2l.GetLength(), 44100)
		d2l.SetSamplingRate(3.3)
		self.assertEqual(d2l.GetLength(), 7)

	def test_connectors(self):
		"""
		Tests if the connectors are properly decorated.
		"""
		d2l = sumpf.modules.DurationToLength()
		self.assertEqual(d2l.GetLength.GetType(), int)
		self.assertEqual(d2l.SetDuration.GetType(), float)
		self.assertEqual(d2l.SetSamplingRate.GetType(), float)
		common.test_connection_observers(testcase=self,
		                                 inputs=[d2l.SetDuration, d2l.SetSamplingRate],
		                                 noinputs=[],
		                                 output=d2l.GetLength)

