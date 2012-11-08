# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012 Jonas Schulte-Coerne
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
import math
import sumpf


class TestSweepGenerator(unittest.TestCase):
	def setUp(self):
		self.f0 = 20.0
		self.sr = 48000
		self.gen = sumpf.modules.SweepGenerator(start_frequency=self.f0,
		                                        stop_frequency=25.0,
		                                        function=sumpf.modules.SweepGenerator.Exponential,
		                                        samplingrate=self.sr,
		                                        length=100)

	def test_initialization(self):
		signal = self.gen.GetSignal()
		self.assertEqual(len(signal), 100)					# the length should be as set in the constructor
		self.assertEqual(signal.GetSamplingRate(), self.sr)	# the sampling rate should be as set in the constructor
		self.assertEqual(signal.GetLabels(), ("Sweep",))	# the label of the channel should be as expected

	@unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
	def test_start_frequency(self):
		"""
		Tests if the start frequency is being calculated correctly.
		This is done by comparing the difference of the first two samples with
		the derivative of a sine with the start frequency.
		"""
		self.gen.SetStopFrequency(4000.0)
		self.gen.SetLength(2 ** 18)
		signal = self.gen.GetSignal()
		s1 = signal.GetChannels()[0][0]
		self.assertEqual(s1, 0.0)					# the first sample should be 0.0
		s2 = signal.GetChannels()[0][1]
		d1 = 2 * math.pi * self.f0
		d2 = math.cos(2 * math.pi * self.f0 / self.sr) * 2 * math.pi * self.f0
		d = (d1 + d2) / 2.0
		self.assertAlmostEqual(s2 * self.sr, d, 2)	# compare the start frequency when frequency increases exponentially
		self.gen.SetSweepFunction(sumpf.modules.SweepGenerator.Linear)
		s2 = self.gen.GetSignal().GetChannels()[0][1]
		self.assertAlmostEqual(s2 * self.sr, d, 1)	# compare the start frequency when frequency increases linearly

	@unittest.skipUnless(sumpf.config.get("run_incomplete_tests"), "Incomplete tests are skipped")
	def test_frequencies(self):
		"""
		Tests if the start and stop frequencies are correct.
		"""
		fT = 1000.0
		self.gen.SetStopFrequency(fT)
		self.gen.SetLength(2 ** 18)
		signal = self.gen.GetSignal()
		s1 = signal.GetChannels()[0][-2]
		s2 = signal.GetChannels()[0][-1]
		s = s2 - s1
		d1 = math.cos(math.asin(s1)) * 2 * math.pi * fT
		d2 = math.cos(math.asin(s2)) * 2 * math.pi * fT
		d = (d1 + d2) / (2 * self.sr)
		self.assertAlmostEqual(s, d, 7)				# compare the stop frequency when frequency increases exponentially
#		self.gen.SetSweepFunction(sumpf.SweepGenerator.Linear)
#		signal = self.gen.GetSignal()
#		s1 = signal.GetChannels()[0][-2]
#		s2 = signal.GetChannels()[0][-1]
#		s = s2 - s1
#		d1 = math.cos(math.asin(s1) * 2 * math.pi * fT) * 2 * math.pi * fT
#		d2 = math.cos(math.asin(s2) * 2 * math.pi * fT) * 2 * math.pi * fT
#		d = (d1 + d2) / (2 * self.sr)
#		self.assertAlmostEqual(s, d, 1)				# compare the stop frequency when frequency increases linearly

