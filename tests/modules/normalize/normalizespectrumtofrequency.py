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


class TestNormalizeSpectrumToFrequency(unittest.TestCase):
    """
    A TestCase for the NormalizeSpectrumToFrequency module.
    """
    def test_functionality(self):
        """
        Tests the functionality of the NormalizeSpectrumToFrequency module.
        """
        # test data
        spectrum = sumpf.Spectrum(channels=((1.0, 2.0, 3.0), (4.0, 1.0, 0.0)), resolution=1000.0, labels=("one", "two"))
        norm1000 = sumpf.Spectrum(channels=((0.5, 1.0, 1.5), (4.0, 1.0, 0.0)), resolution=1000.0, labels=("one", "two"))
        norm500 = sumpf.Spectrum(channels=((2.0 / 3.0, 4.0 / 3.0, 2.0), (8.0 / 5.0, 2.0 / 5.0, 0.0)), resolution=1000.0, labels=("one", "two"))
        # the actual tests
        nrm = sumpf.modules.NormalizeSpectrumToFrequency()
        self.assertEqual(nrm.GetOutput(), sumpf.Spectrum())
        nrm = sumpf.modules.NormalizeSpectrumToFrequency(input=norm1000, frequency=500)
        self.assertEqual(nrm.GetOutput(), norm500)
        nrm = sumpf.modules.NormalizeSpectrumToFrequency(input=spectrum)
        nrm.SetInput(spectrum)
        self.assertEqual(nrm.GetOutput(), norm1000)
        nrm.SetFrequency(500)
        self.assertEqual(nrm.GetOutput(), norm500)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        nrm = sumpf.modules.NormalizeSpectrumToFrequency()
        self.assertEqual(nrm.SetInput.GetType(), sumpf.Spectrum)
        self.assertEqual(nrm.SetFrequency.GetType(), float)
        self.assertEqual(nrm.GetOutput.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[nrm.SetInput, nrm.SetFrequency],
                                         noinputs=[],
                                         output=nrm.GetOutput)

