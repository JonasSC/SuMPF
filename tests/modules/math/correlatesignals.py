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
import _common as common


@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestCorrelateSignals(unittest.TestCase):
	"""
	A test case for the CorrelateSignals module.
	"""
	def setUp(self):
		self.signal1 = sumpf.Signal(channels=((1.0, 0.0),), samplingrate=48000)
		self.signal2 = sumpf.Signal(channels=((0.0, 0.5, 0.0),), samplingrate=48000)

	def test_correlation(self):
		"""
		Tests if the correlation is calculated correctly.
		"""
		cor = sumpf.modules.CorrelateSignals()
		self.assertEqual(cor.GetOutput().GetChannels(), ((0.0, 0.0, 0.0,),))		# the constructor defaults should define a cross correlation of two empty Signals
		cor = sumpf.modules.CorrelateSignals(signal1=self.signal1, signal2=self.signal2, mode=sumpf.modules.CorrelateSignals.FULL)
		self.assertEqual(cor.GetOutput().GetLabels(), ("Cross Correlation 1",))		# check if the label has been set as expected
		self.assertEqual(cor.GetOutput().GetChannels(), ((0.0, 0.5, 0.0, 0.0),))	# check correlation result for mode CorrelateSignals.FULL
		cor.SetCorrelationMode(sumpf.modules.CorrelateSignals.SAME)
		self.assertEqual(cor.GetOutput().GetChannels(), ((0.5, 0.0, 0.0),))			# check correlation result for mode CorrelateSignals.SAME
		cor.SetCorrelationMode(sumpf.modules.CorrelateSignals.VALID)
		self.assertEqual(cor.GetOutput().GetChannels(), ((0.5, 0.0),))				# check correlation result for mode CorrelateSignals.VALID
		cor.SetInput1(self.signal1)
		cor.SetInput2(self.signal1)
		self.assertEqual(cor.GetOutput().GetChannels(), ((1.0, 0.0),))					# check if setting the Signals works
		self.assertEqual(cor.GetOutput().GetLabels(), ("Auto Correlation 1",))		# check if the label has been set to "Auto Correlation", when both input signals are the same

	def test_convolution(self):
		"""
		Tests if the convolution with a reversed Signal is the same as a correlation.
		"""
		reversed_signal1 = sumpf.modules.ReverseSignal(signal=self.signal1).GetOutput()
		for mode in (sumpf.modules.CorrelateSignals.FULL, sumpf.modules.CorrelateSignals.SAME, sumpf.modules.CorrelateSignals.VALID):
			cnv = sumpf.modules.ConvolveSignals(signal1=self.signal2, signal2=reversed_signal1, mode=mode).GetOutput()
			cor = sumpf.modules.CorrelateSignals(signal1=self.signal2, signal2=self.signal1, mode=mode).GetOutput()
			self.assertEqual(cor.GetChannels(), cnv.GetChannels())

	def test_errors(self):
		"""
		Tests if the correlation module raises errors correctly.
		"""
		cor = sumpf.modules.CorrelateSignals(signal1=self.signal2, mode=sumpf.modules.CorrelateSignals.SAME)
		self.assertRaises(ValueError, cor.SetCorrelationMode, "Invalid")						# shall fail if mode is not supported by numpy
		cor.SetInput2(sumpf.Signal(channels=((0.0, 0.0),), samplingrate=44100))
		self.assertRaises(ValueError, cor.GetOutput)											# shall fail because input Signals do not have the same sampling rate
		cor.SetInput2(sumpf.Signal(channels=((1.0, 0.0), (5.0, 5.0)), samplingrate=48000))		# adding a Signal with different channel count or different length shall not fail
		self.assertEqual(cor.GetOutput().GetChannels(), ((0.0, 0.0, 0.5),))

	def test_connectors(self):
		"""
		Tests if the connectors are properly decorated.
		"""
		cnv = sumpf.modules.CorrelateSignals()
		self.assertEqual(cnv.SetInput1.GetType(), sumpf.Signal)
		self.assertEqual(cnv.SetInput2.GetType(), sumpf.Signal)
		self.assertEqual(cnv.SetCorrelationMode.GetType(), type(sumpf.modules.CorrelateSignals.VALID))
		self.assertEqual(cnv.GetOutput.GetType(), sumpf.Signal)
		common.test_connection_observers(testcase=self,
		                                 inputs=[cnv.SetInput1, cnv.SetInput2, cnv.SetCorrelationMode],
		                                 noinputs=[],
		                                 output=cnv.GetOutput)

