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
import sumpf
import _common as common


@unittest.skipIf(sumpf.config.get("unload_numpy"), "Testing modules that require the full featured numpy are skipped")
class TestWindowGenerator(unittest.TestCase):
	"""
	A test case for the WindowGenerator module.
	"""
	def setUp(self):
		self.gen = sumpf.modules.WindowGenerator(interval=(3, 7),
		                                         raising=False,
		                                         function=sumpf.modules.WindowGenerator.Hamming(), 	# Choose a window that does not end with zero
		                                         samplingrate=42.0,
		                                         length=10)

	def test_general(self):
		"""
		Tests general methods of the WindowGenerator like SetRaising and SetInterval.
		"""
		output = self.gen.GetSignal()
		self.assertEqual(output.GetLabels(), ("Window",))			# the label of the channel should be as expected
		self.assertEqual(len(output), 10)							# the length should be as defined in the constructor
		self.assertEqual(output.GetSamplingRate(), 42)				# the sampling rate should be as defined in the constructor
		self.assertEqual(output.GetChannels()[0][0:3], (1.0,) * 3)	# all samples before the window should be 1.0
		self.assertEqual(output.GetChannels()[0][7:10], (0.0,) * 3)	# all samples after the window should be 0.0
		self.gen.SetRaising(True)
		output = self.gen.GetSignal()
		self.assertEqual(output.GetChannels()[0][0:3], (0.0,) * 3)	# if the window is raising all samples before the window should be 0.0
		self.assertEqual(output.GetChannels()[0][7:10], (1.0,) * 3)	# if the window is raising all samples after the window should be 1.0
		self.gen.SetInterval((4, 6))
		output = self.gen.GetSignal()
		self.assertEqual(output.GetChannels()[0][0:4], (0.0,) * 4)	# the start of the window should have been set correctly via SetInterval
		self.assertEqual(output.GetChannels()[0][6:10], (1.0,) * 4)	# the end of the window should have been set correctly via SetInterval
		self.gen.SetInterval((5, 12))
		output = self.gen.GetSignal()
		self.assertEqual(output.GetChannels()[0][0:5], (0.0,) * 5)	# setting an interval which is larger than the length of the generated Signal should be possible
		self.assertEqual(len(output), 10)							# the length should not be changed by the large interval

	def test_window_functions(self):
		"""
		Tests the different window functions.
		"""
		functions = []
		functions.append((sumpf.modules.WindowGenerator.Bartlett(), -2))	# store a tuple (function, limit)
		functions.append((sumpf.modules.WindowGenerator.Blackman(), -1))	# where function is the WindowFunction object
		functions.append((sumpf.modules.WindowGenerator.Hamming(), -1))		# and limit is the last sample that is not 0.0
		functions.append((sumpf.modules.WindowGenerator.Hanning(), -2))		# so if the window ends with 0.0 limit is the last but one sample: -2
		functions.append((sumpf.modules.WindowGenerator.Kaiser(14), -1))	# otherwise it's the last sample: -1
		self.gen.SetInterval((0, 10))
		for function, limit in functions:
			self.gen.SetFunction(function)
			self.gen.SetRaising(False)
			for s in self.gen.GetSignal().GetChannels()[0][0:limit]:
				self.assertNotEqual(s, 1.0)											# the samples of the window must not be 1.0
				self.assertNotEqual(s, 0.0)											# neither can they be 0.0
			if limit == -2:
				self.assertEqual(self.gen.GetSignal().GetChannels()[0][-1], 0.0)	# if the window ends with 0.0 check that last sample
			self.gen.SetRaising(True)
			for s in self.gen.GetSignal().GetChannels()[0][-1 - limit:]:
				self.assertNotEqual(s, 1.0)											# the samples of the window must not be 1.0
				self.assertNotEqual(s, 0.0)											# neither can they be 0.0
			if limit == -2:
				self.assertEqual(self.gen.GetSignal().GetChannels()[0][0], 0.0)		# if the window starts with 0.0 check that first sample

	def test_connectors(self):
		"""
		Tests if the connectors are properly decorated.
		"""
		gen = sumpf.modules.WindowGenerator()
		self.assertEqual(gen.SetLength.GetType(), int)
		self.assertEqual(gen.SetSamplingRate.GetType(), float)
		self.assertEqual(gen.SetInterval.GetType(), tuple)
		self.assertEqual(gen.SetRaising.GetType(), bool)
		self.assertEqual(gen.SetFunction.GetType(), sumpf.internal.WindowFunction)
		self.assertEqual(gen.GetSignal.GetType(), sumpf.Signal)
		common.test_connection_observers(testcase=self,
		                                 inputs=[gen.SetLength, gen.SetSamplingRate, gen.SetInterval, gen.SetRaising, gen.SetFunction],
		                                 noinputs=[],
		                                 output=gen.GetSignal)

