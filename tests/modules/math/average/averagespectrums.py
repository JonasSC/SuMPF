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
from .connectiontester import ConnectionTester


class TestAverageSpectrums(unittest.TestCase):
    """
    A TestCase for the AverageSpectrums module.
    """
    def test_get_set(self):
        """
        Tests if the getter and setter methods work as expected.
        """
        spectrum1 = sumpf.Spectrum(channels=((1.0, 2.0, 3.0 + 3.0j),), resolution=17.0)
        spectrum2 = sumpf.Spectrum(channels=((3.0, 1.0 + 6.0j, 2.0),), resolution=17.0)
        spectrum3 = sumpf.Spectrum(channels=((2.0 + 9.0j, 3.0, 1.0),), resolution=17.0)
        avg = sumpf.modules.AverageSpectrums()
        self.assertIsNone(avg._lastdataset)                                             # an object initialized without arguments should be empty
        avg.AddInput(spectrum1)
        avg.AddInput(spectrum2)
        avg.AddInput(spectrum3)
        output = avg.GetOutput()
        self.assertEqual(output.GetResolution(), 17.0)                                  # the resolution should be taken from input Spectrums
        self.assertEqual(output.GetChannels(), ((2.0 + 3.0j, 2.0 + 2.0j, 2.0 + 1.0j),)) # the average should be calculated correctly
        self.assertEqual(output.GetLabels(), ("Average 1",))                            # the label should be set correctly

    def test_constructor(self):
        """
        Tests if setting the data via the constructor works.
        """
        spectrum1 = sumpf.Spectrum(channels=((1.0, 2.0, 3.0 + 3.0j),), resolution=9.0)
        spectrum2 = sumpf.Spectrum(channels=((3.0, 1.0 + 6.0j, 2.0),), resolution=9.0)
        spectrum3 = sumpf.Spectrum(channels=((2.0 + 9.0j, 3.0, 1.0),), resolution=9.0)
        avg = sumpf.modules.AverageSpectrums(spectrums=[spectrum1, spectrum2, spectrum3])
        output = avg.GetOutput()
        self.assertEqual(output.GetResolution(), 9.0)
        self.assertEqual(output.GetChannels(), ((2.0 + 3.0j, 2.0 + 2.0j, 2.0 + 1.0j),))

    def test_connections(self):
        """
        tests if calculating the average through connections is possible.
        """
        gen = ConnectionTester()
        avg = sumpf.modules.AverageSpectrums()
        sumpf.connect(gen.GetSpectrum, avg.AddInput)
        sumpf.connect(avg.TriggerDataCreation, gen.Start)
        avg.SetNumber(10)
        avg.Start()
        output = avg.GetOutput()
        self.assertEqual(output.GetResolution(), 42.0)
        self.assertEqual(output.GetChannels(), ((4.5, 9.0, 13.5),))

    def test_errors(self):
        """
        Tests if errors are raised as expected.
        """
        spectrum1 = sumpf.Spectrum(channels=((1.0, 2.0, 3.0),), resolution=17.0)
        spectrum2 = sumpf.Spectrum(channels=((3.0, 1.0),), resolution=17.0)
        spectrum3 = sumpf.Spectrum(channels=((2.0, 3.0, 1.0), (2.0, 2.0, 2.0)), resolution=17.0)
        spectrum4 = sumpf.Spectrum(channels=((2.0, 3.0, 1.0),), resolution=9.0)
        avg = sumpf.modules.AverageSpectrums()
        avg.AddInput(spectrum1)
        self.assertRaises(ValueError, avg.AddInput, spectrum2)                                  # should fail because of length conflict
        self.assertRaises(ValueError, avg.AddInput, spectrum3)                                  # should fail because of channel count conflict
        self.assertRaises(ValueError, avg.AddInput, spectrum4)                                  # should fail because of resolution conflict
        self.assertRaises(ValueError, sumpf.modules.AverageSpectrums, [spectrum1, spectrum2])   # spectrums should also be checked in the constructor

