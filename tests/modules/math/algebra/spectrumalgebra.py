# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2015 Jonas Schulte-Coerne
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
        self.spectrum1 = sumpf.Spectrum(channels=((4.0, 6.0j, 4.78), (3.0, 5.0, 9.9j)), resolution=99.34)
        self.spectrum2 = sumpf.Spectrum(channels=((2.0, 1.0, 15.3j), (3.0, 7.0j, 4.0)), resolution=99.34)
        self.wrongresolution = 33.6

    def test_results(self):
        """
        Tests if the calculations yield the expected results.
        """
        self.assertEqual(sumpf.modules.AddSpectrums(spectrum1=self.spectrum1, spectrum2=self.spectrum2).GetOutput(), self.spectrum1 + self.spectrum2)
        self.assertEqual(sumpf.modules.SubtractSpectrums(spectrum1=self.spectrum1, spectrum2=self.spectrum2).GetOutput(), self.spectrum1 - self.spectrum2)
        self.assertEqual(sumpf.modules.MultiplySpectrums(spectrum1=self.spectrum1, spectrum2=self.spectrum2).GetOutput(), self.spectrum1 * self.spectrum2)
        self.assertEqual(sumpf.modules.DivideSpectrums(spectrum1=self.spectrum1, spectrum2=self.spectrum2).GetOutput(), self.spectrum1 / self.spectrum2)

    def test_empty_spectrums(self):
        """
        Tests the algebra modules in case at least one of the input Spectrums is empty.
        """
        wrong_resolution = sumpf.Spectrum(channels=((0.0, 0.0), (0.0, 0.0)), resolution=self.wrongresolution)
        wrong_channelcount = sumpf.Spectrum(resolution=self.spectrum1.GetResolution())
        wrong_length = sumpf.Spectrum(channels=((0.0, 0.0), (0.0, 0.0)), resolution=self.spectrum1.GetResolution(), labels=("These should", "not be copied"))
        for m in [sumpf.modules.AddSpectrums(),
                  sumpf.modules.SubtractSpectrums(),
                  sumpf.modules.MultiplySpectrums(),
                  sumpf.modules.DivideSpectrums()]:
            m.SetInput1(self.spectrum1)
            m.SetInput2(wrong_resolution)
            self.assertEqual(m.GetOutput(), sumpf.Spectrum())
            m.SetInput1(wrong_channelcount)
            m.SetInput2(self.spectrum1)
            self.assertEqual(m.GetOutput(), sumpf.Spectrum(resolution=self.spectrum1.GetResolution()))
            m.SetInput1(wrong_length)
            self.assertEqual(m.GetOutput(), sumpf.Spectrum(channels=wrong_length.GetChannels(), resolution=self.spectrum1.GetResolution()))
        self.assertEqual(sumpf.modules.DivideSpectrums(spectrum1=wrong_length, spectrum2=wrong_length).GetOutput(),
                         sumpf.Spectrum(channels=wrong_length.GetChannels(), resolution=self.spectrum1.GetResolution()))

    def test_errors(self):
        """
        Tests if the algebra modules raise errors correctly.
        """
        wrong_resolution = sumpf.Spectrum(channels=self.spectrum2.GetChannels(), resolution=self.wrongresolution)
        wrong_channelcount = sumpf.Spectrum(channels=(self.spectrum2.GetChannels()[0],), resolution=self.spectrum1.GetResolution())
        wrong_length = sumpf.Spectrum(channels=((2.0, 1.0), (3.0, 7.0j)), resolution=self.spectrum1.GetResolution())
        for cls in [sumpf.modules.AddSpectrums,
                    sumpf.modules.SubtractSpectrums,
                    sumpf.modules.MultiplySpectrums,
                    sumpf.modules.DivideSpectrums]:
            for wrong_spectrum in [wrong_resolution, wrong_channelcount, wrong_length]:
                self.assertRaises(ValueError, cls(spectrum1=self.spectrum1, spectrum2=wrong_spectrum).GetOutput)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        for m in [sumpf.modules.AddSpectrums(),
                  sumpf.modules.SubtractSpectrums(),
                  sumpf.modules.MultiplySpectrums(),
                  sumpf.modules.DivideSpectrums()]:
            self.assertEqual(m.SetInput1.GetType(), sumpf.Spectrum)
            self.assertEqual(m.SetInput2.GetType(), sumpf.Spectrum)
            self.assertEqual(m.GetOutput.GetType(), sumpf.Spectrum)
            common.test_connection_observers(testcase=self,
                                             inputs=[m.SetInput1, m.SetInput2],
                                             noinputs=[],
                                             output=m.GetOutput)

