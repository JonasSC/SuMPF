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


class TestSlopeSpectrumGenerator(unittest.TestCase):
    """
    A TestCase for the SlopeSpectrumGenerator module.
    """
    def test_function(self):
        """
        Tests the generator's output.
        """
        res = 20
        # pink slope (1/f)
        gen = sumpf.modules.SlopeSpectrumGenerator(exponent=1.0, start_frequency=5.0 * res, resolution=res, length=int(20000 / res) + 1)
        channel = gen.GetSpectrum().GetChannels()[0]
        self.assertEqual(channel[0:5], (1.0,) * 5)
        integral1 = 0.0
        for i in range(200 // res, 2000 // res + 1):
            integral1 += channel[i]
        integral2 = 0.0
        for i in range(2000 // res, 20000 // res + 1):
            integral2 += channel[i]
        self.assertLess(abs((integral1 - integral2) / integral2), 0.03)
        # red slope (1/f**2))
        gen.SetExponent(2.0)
        channel = gen.GetSpectrum().GetChannels()[0]
        self.assertEqual(channel[0:5], (1.0,) * 5)
        integral1 = 0.0
        self.assertAlmostEqual(channel[200 // res] / channel[400 // res], 4.0)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.SlopeSpectrumGenerator()
        self.assertEqual(gen.SetExponent.GetType(), float)
        self.assertEqual(gen.SetStartFrequency.GetType(), float)
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetResolution.GetType(), float)
        self.assertEqual(gen.SetMaximumFrequency.GetType(), float)
        self.assertEqual(gen.GetSpectrum.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetExponent, gen.SetStartFrequency, gen.SetLength, gen.SetResolution, gen.SetMaximumFrequency],
                                         noinputs=[],
                                         output=gen.GetSpectrum)

