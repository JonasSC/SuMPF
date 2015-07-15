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


class TestSilenceGenerator(unittest.TestCase):
    """
    A TestCase for the SilenceGenerator.
    """
    def test_samples(self):
        """
        Tests if the length and sampling rate are set correctly and all samples are 0.0.
        """
        gen = sumpf.modules.SilenceGenerator(samplingrate=48000, length=10)
        output = gen.GetSignal()
        self.assertEqual(len(output), 10)
        self.assertEqual(output.GetSamplingRate(), 48000)
        self.assertEqual(output.GetLabels(), ("Silence",))
        self.assertEqual(output.GetChannels(), ((0.0,) * 10,))

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.SilenceGenerator()
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetSamplingRate.GetType(), float)
        self.assertEqual(gen.GetSignal.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetLength, gen.SetSamplingRate],
                                         noinputs=[],
                                         output=gen.GetSignal)

