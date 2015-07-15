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


class TestLaguerreFilterGenerator(unittest.TestCase):
    """
    A TestCase for the LaguerreFilterGenerator module.
    """
    def test_function(self):
        """
        Tests the generator's output.
        """
        # create some Laguerre functions
        laguerre0 = sumpf.modules.LaguerreFilterGenerator(order=0, scaling_factor=1.0, resolution=0.1, length=100).GetSpectrum()
        laguerre1 = sumpf.modules.LaguerreFilterGenerator(order=1, scaling_factor=1.0, resolution=0.1, length=100).GetSpectrum()
        laguerre2 = sumpf.modules.LaguerreFilterGenerator(order=2, scaling_factor=1.0, resolution=0.1, length=100).GetSpectrum()
        m0 = laguerre0.GetMagnitude()[0]
        m1 = laguerre1.GetMagnitude()[0]
        m2 = laguerre2.GetMagnitude()[0]
        p0 = laguerre0.GetContinuousPhase()[0]
        p1 = laguerre1.GetContinuousPhase()[0]
        p2 = laguerre2.GetContinuousPhase()[0]
        # compare the generated functions
        self.assertAlmostEqual(m0[0], 2.0 ** 0.5)
        self.assertAlmostEqual(m1[0], 2.0 ** 0.5)
        self.assertAlmostEqual(m2[0], 2.0 ** 0.5)
        for i in range(1, len(m0)):
            self.assertAlmostEqual(m0[i], m1[i])
            self.assertAlmostEqual(m1[i], m2[i])
            self.assertGreater(p0[i], p1[i])
            self.assertGreater(p1[i], p2[i])

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.LaguerreFilterGenerator()
        self.assertEqual(gen.SetOrder.GetType(), int)
        self.assertEqual(gen.SetScalingFactor.GetType(), float)
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetResolution.GetType(), float)
        self.assertEqual(gen.SetMaximumFrequency.GetType(), float)
        self.assertEqual(gen.GetSpectrum.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetOrder, gen.SetScalingFactor, gen.SetLength, gen.SetResolution, gen.SetMaximumFrequency],
                                         noinputs=[],
                                         output=gen.GetSpectrum)

