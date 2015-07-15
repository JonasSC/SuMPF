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


class TestMean(unittest.TestCase):
    """
    A test case for the calculation of mean values of Signals and Spectrums.
    """
    def test_signal_mean(self):
        """
        Tests the SignalMean class.
        """
        signal1 = sumpf.Signal(channels=((-2.0, -4.8, -3.9, 7.4), (12.1, 0.1, -6.3, -3.5)))
        signal2 = sumpf.Signal(channels=((1, 2), (4, 5), (7, 8)))
        mean = sumpf.modules.SignalMean(signal=signal1)
        result = mean.GetMean()
        expected = (-0.825, 0.6)
        for i in range(max(len(result), len(expected))):
            self.assertAlmostEqual(result[i], expected[i])
        mean.SetSignal(signal2)
        self.assertEqual(mean.GetMean(), (1.5, 4.5, 7.5))

    def test_spectrum_mean(self):
        """
        Tests the SpectrumMean class.
        """
        spectrum1 = sumpf.Spectrum(channels=((-2.0 + 2.0j, -4.8 - 1.0j, -3.9 - 4.7j, 7.4 + 6.6j), (12.1 + 4j, 0.1 - 8.3j, -6.3 + 11.7j, -3.5 + 7.9j)))
        spectrum2 = sumpf.Spectrum(channels=((1, 2), (4, 5), (7, 8)))
        mean = sumpf.modules.SpectrumMean(spectrum=spectrum1)
        result = mean.GetMean()
        expected = (-0.825 + 0.725j, 0.6 + 3.825j)
        for i in range(max(len(result), len(expected))):
            self.assertAlmostEqual(result[i], expected[i])
        mean.SetSpectrum(spectrum2)
        self.assertEqual(mean.GetMean(), (1.5, 4.5, 7.5))

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        mean = sumpf.modules.SignalMean()
        self.assertEqual(mean.SetSignal.GetType(), sumpf.Signal)
        self.assertEqual(mean.GetMean.GetType(), tuple)
        common.test_connection_observers(testcase=self,
                                         inputs=[mean.SetSignal],
                                         noinputs=[],
                                         output=mean.GetMean)
        mean = sumpf.modules.SpectrumMean()
        self.assertEqual(mean.SetSpectrum.GetType(), sumpf.Spectrum)
        self.assertEqual(mean.GetMean.GetType(), tuple)
        common.test_connection_observers(testcase=self,
                                         inputs=[mean.SetSpectrum],
                                         noinputs=[],
                                         output=mean.GetMean)

