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


@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestRegularizedSpectrumInversion(unittest.TestCase):
    """
    A TestCase for the RegularizedSpectrumInversion module.
    """
    def test_epsilon(self):
        """
        Tests if the regularization parameter behaves as expected.
        """
        spk = sumpf.Spectrum(channels=((1.0,) * 100, (13.37 + 4.2j,) * 100), resolution=1.0)
        cnj = sumpf.modules.ConjugateSpectrum(spectrum=spk).GetOutput()
        reg = sumpf.modules.RegularizedSpectrumInversion(spectrum=spk,
                                                         start_frequency=30.0,
                                                         stop_frequency=70.0,
                                                         transition_length=10,
                                                         epsilon_max=1.0).GetOutput()
        eps = cnj / reg - cnj * spk
        c1 = eps.GetChannels()[0]
        c2 = eps.GetChannels()[1]
        for i in range(100):
            self.assertAlmostEqual(c1[i], c2[i])    # the epsilons should be equal for all channels
        for i in range(0, 20):
            self.assertEqual(c1[i], 1.0)
        for i in range(20, 30):
            self.assertGreater(c1[i], 0.0)
            self.assertLess(c1[i], c1[i - 1])
        for i in range(30, 71):
            self.assertEqual(c1[i], 0.0)
        for i in range(71, 81):
            self.assertLess(c1[i], 1.0)
            self.assertGreater(c1[i], c1[i - 1])
        for i in range(81, 100):
            self.assertEqual(c1[i], 1.0)

    def test_no_max_epsilon(self):
        """
        Tests what happens, if epsilon_max cannot be reached because of too long
        transition lengths or a too wide frequency interval.
        """
        spk = sumpf.Spectrum(channels=((2.3,) * 100,), resolution=0.1, labels=("Test",))
        reg = sumpf.modules.RegularizedSpectrumInversion()
        self.assertEqual(reg.GetOutput(), sumpf.Spectrum(channels=((1.0, 1.0),)))
        reg.SetSpectrum(spk)
        self.assertEqual(reg.GetOutput().GetLabels(), spk.GetLabels())
        reg.SetStartFrequency(0.0)
        reg.SetStopFrequency(10.0)
        for i in range(100):
            self.assertEqual(reg.GetOutput().GetChannels()[0][i], 1.0 / spk.GetChannels()[0][i])
        reg.SetStartFrequency(0.7)
        reg.SetStopFrequency(9.2)
        reg.SetTransitionLength(10)
        reg.SetEpsilonMax(1.0)
        self.assertEqual(reg.GetOutput().GetChannels()[0][0], 2.3 / (2.3 ** 2 + 0.75))
        self.assertEqual(reg.GetOutput().GetChannels()[0][-1], 2.3 / (2.3 ** 2 + 0.75))

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        reg = sumpf.modules.RegularizedSpectrumInversion()
        self.assertEqual(reg.GetOutput.GetType(), sumpf.Spectrum)
        self.assertEqual(reg.SetSpectrum.GetType(), sumpf.Spectrum)
        self.assertEqual(reg.SetStartFrequency.GetType(), float)
        self.assertEqual(reg.SetStopFrequency.GetType(), float)
        self.assertEqual(reg.SetTransitionLength.GetType(), int)
        self.assertEqual(reg.SetEpsilonMax.GetType(), float)
        common.test_connection_observers(testcase=self,
                                         inputs=[reg.SetSpectrum, reg.SetStartFrequency, reg.SetStopFrequency, reg.SetTransitionLength, reg.SetEpsilonMax],
                                         noinputs=[],
                                         output=reg.GetOutput)

