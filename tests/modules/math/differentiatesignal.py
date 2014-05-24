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
import unittest
import sumpf
import _common as common


class TestDifferentiateSignal(unittest.TestCase):
	"""
	A test case for the DifferentiateSignal module.
	"""
	def test_linear(self):
		"""
		Tests the derivative of a linearly raising Signal.
		"""
		length = 100
		samples = []
		for i in range(length):
			samples.append(float(i) / float(length))
		signal = sumpf.Signal(channels=(tuple(samples),), samplingrate=length / 2.0)
		drv = sumpf.modules.DifferentiateSignal(signal=signal)
		self.assertAlmostEqual(max(drv.GetOutput().GetChannels()[0]), 0.5)
		self.assertAlmostEqual(min(drv.GetOutput().GetChannels()[0]), 0.5)

	@unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
	def test_sine(self):
		"""
		Tests the derivative of a sine wave Signal.
		"""
		frequency = 1.9
		samplingrate = 48000
		length = 5 * samplingrate
		sin = sumpf.modules.SineWaveGenerator(frequency=frequency,
		                                      phase=0.0,
		                                      samplingrate=samplingrate,
		                                      length=length)
		cos = sumpf.modules.SineWaveGenerator(frequency=frequency,
		                                      phase=math.pi / 2.0,
		                                      samplingrate=samplingrate,
		                                      length=length)
		drv = sumpf.modules.DifferentiateSignal()
		places = 2
		self.assertEqual(drv.GetOutput(), sumpf.Signal())
		drv.SetInput(sin.GetSignal())
		common.compare_signals_almost_equal(self, drv.GetOutput(), cos.GetSignal() * (2.0 * math.pi * frequency), places)

	def test_connectors(self):
		"""
		Tests if the connectors are properly decorated.
		"""
		drv = sumpf.modules.DifferentiateSignal()
		self.assertEqual(drv.SetInput.GetType(), sumpf.Signal)
		self.assertEqual(drv.GetOutput.GetType(), sumpf.Signal)
		common.test_connection_observers(testcase=self,
		                                 inputs=[drv.SetInput],
		                                 noinputs=[],
		                                 output=drv.GetOutput)

