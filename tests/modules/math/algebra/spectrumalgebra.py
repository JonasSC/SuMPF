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


class TestSpectrumAlgebra(unittest.TestCase):
	"""
	A test case for the algebra modules for Spectrums.
	"""
	def setUp(self):
		self.spectrum1 = sumpf.Spectrum(channels=((4.0, 6.0), (3.0, 5.0)), resolution=24000.0)
		self.spectrum2 = sumpf.Spectrum(channels=((2.0, 1.0), (3.0, 7.0)), resolution=24000.0)

	def test_add(self):
		"""
		Tests the addition of Spectrums.
		"""
		alg = sumpf.modules.AddSpectrums(spectrum1=self.spectrum1, spectrum2=self.spectrum2)
		res = alg.GetOutput()
		self.assertEqual(res.GetChannels(), ((6.0, 7.0), (6.0, 12.0)))
		self.assertEqual(res.GetLabels(), ("Sum 1", "Sum 2"))

	def test_subtract(self):
		"""
		Tests the subtraction of Spectrums.
		"""
		alg = sumpf.modules.SubtractSpectrums(spectrum1=self.spectrum1, spectrum2=self.spectrum2)
		res = alg.GetOutput()
		self.assertEqual(res.GetChannels(), ((2.0, 5.0), (0.0, -2.0)))
		self.assertEqual(res.GetLabels(), ("Difference 1", "Difference 2"))

	def test_multiply(self):
		"""
		Tests the multiplication of Spectrums.
		"""
		alg = sumpf.modules.MultiplySpectrums(spectrum1=self.spectrum1, spectrum2=self.spectrum2)
		res = alg.GetOutput()
		self.assertEqual(res.GetChannels(), ((8.0, 6.0), (9.0, 35.0)))
		self.assertEqual(res.GetLabels(), ("Product 1", "Product 2"))

	def test_divide(self):
		"""
		Tests the division of Spectrums.
		"""
		alg = sumpf.modules.DivideSpectrums(spectrum1=self.spectrum1, spectrum2=self.spectrum2)
		res = alg.GetOutput()
		self.assertEqual(res.GetChannels(), ((2.0, 6.0), (1.0, (5.0 / 7.0))))
		self.assertEqual(res.GetLabels(), ("Quotient 1", "Quotient 2"))

	def test_emptyspectrum(self):
		"""
		Tests if empty Spectrums are processed as expected.
		"""
		spectrum = sumpf.Spectrum(channels=((1.0, 2.0, 3.0), (4.0, 5.0, 6.0)), resolution=42.0)
		nullspectrum = sumpf.Spectrum(channels=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), resolution=42.0)
		invspectrum = sumpf.modules.AmplifySpectrum(input=spectrum, factor= -1.0).GetOutput()
		aspectrum = sumpf.modules.RelabelSpectrum(input=spectrum, labels=("Sum 1", "Sum 2")).GetOutput()
		sspectrum = sumpf.modules.RelabelSpectrum(input=spectrum, labels=("Difference 1", "Difference 2")).GetOutput()
		sinvspectrum = sumpf.modules.RelabelSpectrum(input=invspectrum, labels=("Difference 1", "Difference 2")).GetOutput()
		mnullspectrum = sumpf.modules.RelabelSpectrum(input=nullspectrum, labels=("Product 1", "Product 2")).GetOutput()
		dnullspectrum = sumpf.modules.RelabelSpectrum(input=nullspectrum, labels=("Quotient 1", "Quotient 2")).GetOutput()
		donespectrum = sumpf.Spectrum(channels=((1.0, 1.0),), labels=("Quotient 1",))
		self.assertEqual(sumpf.modules.AddSpectrums(spectrum, sumpf.Spectrum()).GetOutput(), aspectrum)
		self.assertEqual(sumpf.modules.AddSpectrums(sumpf.Spectrum(), spectrum).GetOutput(), aspectrum)
		self.assertEqual(sumpf.modules.SubtractSpectrums(spectrum, sumpf.Spectrum()).GetOutput(), sspectrum)
		self.assertEqual(sumpf.modules.SubtractSpectrums(sumpf.Spectrum(), spectrum).GetOutput(), sinvspectrum)
		self.assertEqual(sumpf.modules.MultiplySpectrums(spectrum, sumpf.Spectrum()).GetOutput(), mnullspectrum)
		self.assertEqual(sumpf.modules.MultiplySpectrums(sumpf.Spectrum(), spectrum).GetOutput(), mnullspectrum)
		self.assertRaises(ZeroDivisionError, sumpf.modules.DivideSpectrums(spectrum, sumpf.Spectrum()).GetOutput)
		self.assertEqual(sumpf.modules.DivideSpectrums(sumpf.Spectrum(), spectrum).GetOutput(), dnullspectrum)
		self.assertEqual(sumpf.modules.DivideSpectrums(sumpf.Spectrum(), sumpf.Spectrum()).GetOutput(), donespectrum)

	def test_errors(self):
		"""
		Tests if the algebra modules raise errors correctly.
		"""
		alg = sumpf.modules.AddSpectrums(spectrum1=self.spectrum1)
		alg.SetInput2(sumpf.Spectrum(channels=((0.0, 1.0, 0.0),), resolution=24000.0))
		self.assertRaises(ValueError, alg.GetOutput)									# shall fail if Spectrums do not have the same length
		alg.SetInput2(sumpf.Spectrum(channels=((0.0, 1.0),), resolution=22050.0))
		self.assertRaises(ValueError, alg.GetOutput)									# shall fail if Spectrums do not have the same resolution
		alg.SetInput2(sumpf.Spectrum(channels=((6.0, 4.0),), resolution=24000.0))		# adding a Spectrum with different channel count shall not fail. Surplus channels shall be cropped
		self.assertEqual(alg.GetOutput().GetChannels(), ((10.0, 10.0),))

	def test_connectors(self):
		"""
		Tests if the connectors are properly decorated.
		"""
		for m in [sumpf.modules.AddSpectrums(), sumpf.modules.SubtractSpectrums(), sumpf.modules.MultiplySpectrums(), sumpf.modules.DivideSpectrums()]:
			self.assertEqual(m.SetInput1.GetType(), sumpf.Spectrum)
			self.assertEqual(m.SetInput2.GetType(), sumpf.Spectrum)
			self.assertEqual(m.GetOutput.GetType(), sumpf.Spectrum)
			common.test_connection_observers(testcase=self,
			                                 inputs=[m.SetInput1, m.SetInput2],
			                                 noinputs=[],
			                                 output=m.GetOutput)

