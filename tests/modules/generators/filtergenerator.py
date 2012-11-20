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
import _common as common


class TestFilterGenerator(unittest.TestCase):
	"""
	A TestCase for the FilterGenerator module.
	"""
	def test_gain(self):
		gen = sumpf.modules.FilterGenerator(frequency=100.0, resolution=200.0, length=100)
		self.assertEqual(gen.GetSpectrum().GetLabels(), ("Filter",))	# the label of the channel should be as expected
		coefficients = []
		coefficients.append(sumpf.modules.FilterGenerator.Butterworth(order=4))
		coefficients.append(sumpf.modules.FilterGenerator.Chebyshev(order=4, ripple=3.0))
		for c in coefficients:
			gen.SetCoefficients(c)
			gen.SetLowpassToHighpassTransform(False)
			channel = gen.GetSpectrum().GetMagnitude()[0]
			self.assertAlmostEqual(channel[0], 1.0)						# a lowpass should have a gain of 1 at low frequencies
			self.assertAlmostEqual(channel[-1], 0.0)					# a lowpass should have a gain of 0 at high frequencies
			gen.SetLowpassToHighpassTransform(True)
			channel = gen.GetSpectrum().GetMagnitude()[0]
			self.assertAlmostEqual(channel[0], 0.0)						# a highpass should have a gain of 0 at low frequencies
			self.assertAlmostEqual(channel[-1], 1.0, 3)					# a highpass should have a gain of 1 at high frequencies

	def test_passthrough(self):
		gen = sumpf.modules.FilterGenerator(frequency=100.0, resolution=20.0, length=10)
		expected_result = ((1.0,) * 10,)
		self.assertEqual(gen.GetSpectrum().GetResolution(), 20.0)			# resolution should have been copied correctly
		self.assertEqual(gen.GetSpectrum().GetChannels(), expected_result)	# all samples should be 1.0
		gen.SetFrequency(37.4)
		self.assertEqual(gen.GetSpectrum().GetResolution(), 20.0)			# resolution should have been copied correctly, even after frequency change
		self.assertEqual(gen.GetSpectrum().GetChannels(), expected_result)	# all samples should be 1.0, even after frequency change

	def test_bandpass(self):
		gen = sumpf.modules.FilterGenerator(frequency=500.0, resolution=10.0, length=100)
		gen.SetCoefficients(sumpf.modules.FilterGenerator.Bandpass(q_factor=5.0))
		channel = gen.GetSpectrum().GetMagnitude()[0]
		self.assertAlmostEqual(channel[50], 1.0)							# gain at resonant frequency should be 1
		self.assertAlmostEqual(channel[45], 1.0 / math.sqrt(2.0), 1)		# gain at lower cutoff frequency should be sqrt(2)
		self.assertAlmostEqual(channel[55], 1.0 / math.sqrt(2.0), 1)		# gain at upper cutoff frequency should be sqrt(2)

	def test_connectors(self):
		"""
		Tests if the connectors are properly decorated.
		"""
		gen = sumpf.modules.FilterGenerator()
		self.assertEqual(gen.SetLength.GetType(), int)
		self.assertEqual(gen.SetResolution.GetType(), float)
		self.assertEqual(gen.SetMaximumFrequency.GetType(), float)
		self.assertEqual(gen.SetCoefficients.GetType(), list)
		self.assertEqual(gen.SetFrequency.GetType(), float)
		self.assertEqual(gen.SetLowpassToHighpassTransform.GetType(), bool)
		self.assertEqual(gen.GetSpectrum.GetType(), sumpf.Spectrum)
		common.test_connection_observers(testcase=self,
		                                 inputs=[gen.SetLength, gen.SetResolution, gen.SetMaximumFrequency, gen.SetCoefficients, gen.SetFrequency, gen.SetLowpassToHighpassTransform],
		                                 noinputs=[],
		                                 output=gen.GetSpectrum)

