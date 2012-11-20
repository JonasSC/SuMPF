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
class TestConvolveSignals(unittest.TestCase):
	"""
	A test case for the ConvolveSignals module.
	"""
	def setUp(self):
		self.signal1 = sumpf.Signal(channels=((1.0, 0.0),), samplingrate=48000)
		self.signal2 = sumpf.Signal(channels=((0.0, 0.5, 0.0),), samplingrate=48000)

	def test_convolution(self):
		"""
		Tests if the convolution is calculated correctly.
		"""
		cnv = sumpf.modules.ConvolveSignals()
		self.assertEqual(cnv.GetOutput().GetChannels(), ((0.0, 0.0, 0.0),))		# the constructor defaults should define a full convolution of two empty Signals
		cnv = sumpf.modules.ConvolveSignals(signal1=self.signal1, signal2=self.signal2, mode=sumpf.modules.ConvolveSignals.FULL)
		self.assertEqual(cnv.GetOutput().GetLabels(), ("Convolution 1",))			# check if the label has been set as expected
		self.assertEqual(cnv.GetOutput().GetChannels(), ((0.0, 0.5, 0.0, 0.0),))	# check convolution result for mode ConvolveSignals.FULL
		cnv.SetConvolutionMode(sumpf.modules.ConvolveSignals.SAME)
		self.assertEqual(cnv.GetOutput().GetChannels(), ((0.0, 0.5, 0.0),))		# check convolution result for mode ConvolveSignals.SAME
		cnv.SetConvolutionMode(sumpf.modules.ConvolveSignals.VALID)
		self.assertEqual(cnv.GetOutput().GetChannels(), ((0.5, 0.0),))			# check convolution result for mode ConvolveSignals.VALID
		cnv.SetInput1(self.signal2)
		cnv.SetInput2(self.signal1)
		self.assertEqual(cnv.GetOutput().GetChannels(), ((0.5, 0.0),))			# check if setting the Signals works

	def test_errors(self):
		"""
		Tests if the convolution module raises errors correctly.
		"""
		cnv = sumpf.modules.ConvolveSignals(signal1=self.signal2, mode=sumpf.modules.ConvolveSignals.SAME)
		self.assertRaises(ValueError, cnv.SetConvolutionMode, "Very Full")												# shall fail if mode is not supported by numpy
		cnv.SetInput2(sumpf.Signal(channels=((0.0, 0.0),), samplingrate=44100))
		self.assertRaises(ValueError, cnv.GetOutput)																# shall fail because input Signals do not have the same sampling rate
		cnv.SetInput2(sumpf.Signal(channels=((1.0, 0.0), (5.0, 5.0)), samplingrate=48000))						# adding a Signal with different channel count or different length shall not fail
		self.assertEqual(cnv.GetOutput().GetChannels(), ((0.0, 0.5, 0.0),))

	def test_connectors(self):
		"""
		Tests if the connectors are properly decorated.
		"""
		cnv = sumpf.modules.ConvolveSignals()
		self.assertEqual(cnv.SetInput1.GetType(), sumpf.Signal)
		self.assertEqual(cnv.SetInput2.GetType(), sumpf.Signal)
		self.assertEqual(cnv.SetConvolutionMode.GetType(), type(sumpf.modules.ConvolveSignals.FULL))
		self.assertEqual(cnv.GetOutput.GetType(), sumpf.Signal)
		common.test_connection_observers(testcase=self,
		                                 inputs=[cnv.SetInput1, cnv.SetInput2, cnv.SetConvolutionMode],
		                                 noinputs=[],
		                                 output=cnv.GetOutput)

