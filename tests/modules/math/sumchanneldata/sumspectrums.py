# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2018 Jonas Schulte-Coerne
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

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy



class TestSumSpectrums(unittest.TestCase):
    """
    A test case for the SumSpectrums module
    """
    def setUp(self):
        self.spectrum1 = sumpf.Spectrum(channels=((11.1, 11.2, 11.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3)), resolution=42.0, labels=("1.1", "1.2", "1.3"))
        self.spectrum2 = sumpf.Spectrum(channels=((21.1, 21.2, 21.3), (22.1, 22.2, 22.3), (23.1, 23.2, 23.3)), resolution=42.0, labels=("2.1", "2.2", "2.3"))
        self.spectrum3 = sumpf.Spectrum(channels=((31.1, 31.2), (32.1, 32.2), (33.1, 33.2)), resolution=42.0)
        self.spectrum3_0 = sumpf.Spectrum(channels=((31.1, 31.2, 0.0), (32.1, 32.2, 0.0), (33.1, 33.2, 0.0)), resolution=42.0)
        self.spectrum4 = sumpf.Spectrum(channels=((41.1, 41.2, 41.3), (42.1, 42.2, 42.3), (43.1, 43.2, 43.3)), resolution=23.0)
        self.spectrum5 = sumpf.Spectrum(channels=((51.1, 51.2, 51.3), (52.1, 52.2, 52.3)), resolution=42.0)
        self.spectrum6 = sumpf.Spectrum(channels=((61.1, 61.2, 61.3),), resolution=42.0)

    def test_constructor_and_clear(self):
        """
        Tests if adding a list of Spectrums with the constructor works and if removing them with the Clear method works.
        """
        sumspectrums = sumpf.modules.SumSpectrums(spectrums=[self.spectrum1, self.spectrum2])
        self.assertEqual(sumspectrums.GetOutput(), self.spectrum1 + self.spectrum2)
        sumspectrums.Clear()
        self.assertEqual(sumspectrums.GetOutput(), sumpf.Spectrum())
        quicksummed = sumpf.modules.SumSpectrums([self.spectrum1, self.spectrum2]).GetOutput()
        self.assertEqual(quicksummed, self.spectrum1 + self.spectrum2)
        self.assertRaises(ValueError, sumpf.modules.SumSpectrums([self.spectrum1, self.spectrum2, self.spectrum3]).GetOutput)
        self.assertEqual(sumpf.modules.SumSpectrums([self.spectrum1, self.spectrum2, self.spectrum3], on_length_conflict=sumpf.modules.SumSpectrums.FILL_WITH_ZEROS).GetOutput(), self.spectrum1 + self.spectrum2 + self.spectrum3_0)

    def test_summation(self):
        """
        Tests if the summation works as expected
        """
        sumspectrums = sumpf.modules.SumSpectrums()
        self.assertEqual(sumspectrums.GetOutput(), sumpf.Spectrum())
        id1 = sumspectrums.AddInput(self.spectrum1)
        self.assertEqual(sumspectrums.GetOutput(), self.spectrum1)
        sumspectrums.AddInput(self.spectrum2)
        self.assertEqual(sumspectrums.GetOutput(), self.spectrum1 + self.spectrum2)
        sumspectrums.RemoveInput(id1)
        self.assertEqual(sumspectrums.GetOutput(), self.spectrum2)
        sumspectrums.AddInput(self.spectrum3)
        sumspectrums.SetLengthConflictStrategy(sumpf.modules.SumSpectrums.FILL_WITH_ZEROS)
        self.assertEqual(sumspectrums.GetOutput(), self.spectrum2 + self.spectrum3_0)
        sumspectrums.SetLengthConflictStrategy(sumpf.modules.SumSpectrums.CROP)
        expected_channels = tuple(numpy.add(a, b)[0:len(self.spectrum3)] for a, b in zip(self.spectrum2.GetChannels(), self.spectrum3_0.GetChannels()))
        for c1, c2 in zip(sumspectrums.GetOutput().GetChannels(), expected_channels):
            for s1, s2 in zip(c1, c2):
                self.assertEqual(s1, s2)
        sumspectrums.Clear()
        sumspectrums.AddInput(self.spectrum4)
        self.assertEqual(sumspectrums.GetOutput(), self.spectrum4)

    def test_errors(self):
        """
        Tests if errors are raised correctly
        """
        self.assertRaises(ValueError, sumpf.modules.SumSpectrums().RemoveInput, 3)
        self.assertRaises(ValueError, sumpf.modules.SumSpectrums([self.spectrum1, self.spectrum3]).GetOutput)
        self.assertRaises(ValueError, sumpf.modules.SumSpectrums([self.spectrum1, self.spectrum4]).GetOutput)
        self.assertRaises(ValueError, sumpf.modules.SumSpectrums([self.spectrum1, self.spectrum5]).GetOutput)
        self.assertRaises(ValueError, sumpf.modules.SumSpectrums([self.spectrum1, self.spectrum6]).GetOutput)
        self.assertRaises(ValueError, sumpf.modules.SumSpectrums([self.spectrum3, self.spectrum6], on_length_conflict=sumpf.modules.SumSpectrums.FILL_WITH_ZEROS).GetOutput)
        self.assertRaises(ValueError, sumpf.modules.SumSpectrums([self.spectrum3, self.spectrum6], on_length_conflict=sumpf.modules.SumSpectrums.CROP).GetOutput)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        sumspectrums = sumpf.modules.SumSpectrums()
        self.assertEqual(sumspectrums.AddInput.GetType(), sumpf.Spectrum)
        self.assertEqual(sumspectrums.SetLengthConflictStrategy.GetType(), int)
        self.assertEqual(sumspectrums.GetOutput.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[sumspectrums.AddInput, sumspectrums.SetLengthConflictStrategy, sumspectrums.Clear],
                                         noinputs=[],
                                         output=sumspectrums.GetOutput)

