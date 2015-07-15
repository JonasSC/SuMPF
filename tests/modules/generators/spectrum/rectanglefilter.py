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


class TestRectangleFilterGenerator(unittest.TestCase):
    """
    A TestCase for the RectangleFilterGenerator module.
    """
    def test_function(self):
        """
        Tests the generator's output.
        """
        spectrum = sumpf.modules.RectangleFilterGenerator(start_frequency=5.0, stop_frequency=7.0, invert=False, resolution=0.1, length=100).GetSpectrum()
        self.assertEqual(spectrum.GetChannels()[0][0:50], (0.0,) * 50)
        self.assertEqual(spectrum.GetChannels()[0][50:70], (1.0,) * 20)
        self.assertEqual(spectrum.GetChannels()[0][70:], (0.0,) * 30)
        spectrum = sumpf.modules.RectangleFilterGenerator(start_frequency=5.0, stop_frequency=7.0, invert=True, resolution=0.1, length=100).GetSpectrum()
        self.assertEqual(spectrum.GetChannels()[0][0:50], (1.0,) * 50)
        self.assertEqual(spectrum.GetChannels()[0][50:70], (0.0,) * 20)
        self.assertEqual(spectrum.GetChannels()[0][70:], (1.0,) * 30)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.RectangleFilterGenerator()
        self.assertEqual(gen.SetStartFrequency.GetType(), float)
        self.assertEqual(gen.SetStopFrequency.GetType(), float)
        self.assertEqual(gen.SetInvert.GetType(), bool)
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetResolution.GetType(), float)
        self.assertEqual(gen.SetMaximumFrequency.GetType(), float)
        self.assertEqual(gen.GetSpectrum.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetStartFrequency, gen.SetStopFrequency, gen.SetInvert, gen.SetLength, gen.SetResolution, gen.SetMaximumFrequency],
                                         noinputs=[],
                                         output=gen.GetSpectrum)

