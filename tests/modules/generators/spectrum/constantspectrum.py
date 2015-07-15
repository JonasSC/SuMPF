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


class TestConstantSpectrumGenerator(unittest.TestCase):
    """
    A TestCase for the ConstantSpectrumGenerator module.
    """
    def test_function(self):
        """
        Tests the generator's output.
        """
        # test a floating point factor
        gen = sumpf.modules.ConstantSpectrumGenerator(value=0.7, resolution=0.5, length=10)
        result = sumpf.Spectrum(channels=((0.7,) * 10,), resolution=0.5, labels=("Constant",))
        self.assertEqual(gen.GetSpectrum(), result)
        # test an integer factor
        gen.SetValue(4)
        result = sumpf.Spectrum(channels=((4.0,) * 10,), resolution=0.5, labels=("Constant",))
        # test a complex factor
        gen.SetValue(3.4j)
        result = sumpf.Spectrum(channels=((3.4j,) * 10,), resolution=0.5, labels=("Constant",))

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.ConstantSpectrumGenerator()
        self.assertEqual(gen.SetValue.GetType(), float)
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetResolution.GetType(), float)
        self.assertEqual(gen.SetMaximumFrequency.GetType(), float)
        self.assertEqual(gen.GetSpectrum.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetValue, gen.SetLength, gen.SetResolution, gen.SetMaximumFrequency],
                                         noinputs=[],
                                         output=gen.GetSpectrum)

