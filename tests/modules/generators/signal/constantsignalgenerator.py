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


class TestConstantSignalGenerator(unittest.TestCase):
    """
    A TestCase for the ConstantSignalGenerator.
    """
    def test_samples(self):
        """
        Tests if the length and sampling rate are set correctly and all samples
        have the given value.
        """
        gen = sumpf.modules.ConstantSignalGenerator(samplingrate=48000, length=10)
        output = gen.GetSignal()
        self.assertEqual(len(output), 10)
        self.assertEqual(output.GetSamplingRate(), 48000)
        self.assertEqual(output.GetLabels(), ("Constant",))
        self.assertEqual(output.GetChannels(), ((1.0,) * 10,))
        gen = sumpf.modules.ConstantSignalGenerator(value=12.0, samplingrate=48000, length=10)
        output = gen.GetSignal()
        self.assertEqual(output.GetChannels(), ((12.0,) * 10,))
        gen.SetValue(-4.6)
        output = gen.GetSignal()
        self.assertEqual(output.GetChannels(), ((-4.6,) * 10,))

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.ConstantSignalGenerator()
        self.assertEqual(gen.SetValue.GetType(), float)
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetSamplingRate.GetType(), float)
        self.assertEqual(gen.GetSignal.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetValue, gen.SetLength, gen.SetSamplingRate],
                                         noinputs=[],
                                         output=gen.GetSignal)

