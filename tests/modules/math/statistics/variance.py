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


class TestVariance(unittest.TestCase):
    """
    A test case for the calculation of variance values of Signals and Spectrums.
    """
    def test_signal_variance(self):
        """
        Tests the SignalVariance class.
        """
        signal1 = sumpf.Signal(channels=((-2.0, -4.8, -3.9, 7.4), (12.1, 0.1, -6.3, -3.5)))
        signal2 = sumpf.Signal(channels=((1, 2), (4, 5), (7, 8)))
        variance = sumpf.modules.SignalVariance(signal=signal1)
        result = variance.GetVariance()
        mean1 = sumpf.modules.SignalMean(signal=signal1).GetMean()
        mean2 = sumpf.modules.SignalMean(signal=signal1 * signal1).GetMean()
        for i in range(max(len(result), len(mean1), len(mean2))):
            expected = mean2[i] - mean1[i] ** 2
            self.assertAlmostEqual(result[i], expected)
        variance.SetSignal(signal2)
        self.assertEqual(variance.GetVariance(), (0.25, 0.25, 0.25))

    @unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
    def test_spectrum_variance(self):
        """
        Tests the SpectrumVariance class.
        """
        spectrum1 = sumpf.Spectrum(channels=((-2.0 + 2.0j, -4.8 - 1.0j, -3.9 - 4.7j, 7.4 + 6.6j), (12.1 + 4j, 0.1 - 8.3j, -6.3 + 11.7j, -3.5 + 7.9j)))
        spectrum2 = sumpf.Spectrum(channels=((1, 2), (4, 5), (7, 8)))
        variance = sumpf.modules.SpectrumVariance(spectrum=spectrum1)
        result = variance.GetVariance()
        mean = sumpf.modules.SpectrumMean(spectrum=spectrum1).GetMean()
        for i in range(len(result)):
            expected = 0.0
            for s in spectrum1.GetChannels()[i]:
                expected += abs((s - mean[i]) ** 2)
            expected /= len(spectrum1)
            self.assertAlmostEqual(result[i], expected)
        variance.SetSpectrum(spectrum2)
        self.assertEqual(variance.GetVariance(), (0.25, 0.25, 0.25))

    def test_signal_variance_connectors(self):
        """
        Tests if the connectors of the SignalVariance class are properly decorated.
        """
        variance = sumpf.modules.SignalVariance()
        self.assertEqual(variance.SetSignal.GetType(), sumpf.Signal)
        self.assertEqual(variance.GetVariance.GetType(), tuple)
        common.test_connection_observers(testcase=self,
                                         inputs=[variance.SetSignal],
                                         noinputs=[],
                                         output=variance.GetVariance)

    @unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
    def test_spectrum_variance_connectors(self):
        """
        Tests if the connectors of the SpectrumVariance class are properly decorated.
        """
        variance = sumpf.modules.SpectrumVariance()
        self.assertEqual(variance.SetSpectrum.GetType(), sumpf.Spectrum)
        self.assertEqual(variance.GetVariance.GetType(), tuple)
        common.test_connection_observers(testcase=self,
                                         inputs=[variance.SetSpectrum],
                                         noinputs=[],
                                         output=variance.GetVariance)

