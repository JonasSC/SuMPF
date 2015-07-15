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

import collections
import math
import unittest
import sumpf
import _common as common


class TestArbitrarySignalGenerator(unittest.TestCase):
    """
    A TestCase for the ArbitrarySignalGenerator.
    """
    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_defaults(self):
        """
        Tests the default values of the ArbitrarySignalGenerator.
        """
        gen = sumpf.modules.ArbitrarySignalGenerator()
        signal = gen.GetSignal()
        self.assertEqual(len(signal), sumpf.config.get("default_signal_length"))
        self.assertEqual(signal.GetSamplingRate(), sumpf.config.get("default_samplingrate"))
        self.assertEqual(signal.GetLabels(), ("Arbitrary",))

    def test_compare_with_other_generators(self):
        """
        Compares the output of an ArbitrarySignalGenerator with the output of
        other signal generator classes.
        """
        # impulse
        def impulse(t):
            if t == 0.0:
                return 1.0
            else:
                return 0.0
        aimpulse = sumpf.modules.ArbitrarySignalGenerator(function=impulse,
                                                        label="Impulse",
                                                        samplingrate=47,
                                                        length=11).GetSignal()
        gimpulse = sumpf.modules.ImpulseGenerator(delay=0.0,
                                                  frequency=0.0,
                                                  samplingrate=47,
                                                  length=11).GetSignal()
        self.assertEqual(aimpulse, gimpulse)
        # sine
        def sine(t):
            return math.sin(2.0 * math.pi * 1000.0 * t + 1.3)
        asine = sumpf.modules.ArbitrarySignalGenerator(function=sine,
                                                       label="Sine",
                                                       samplingrate=64.203,
                                                       length=13).GetSignal()
        gsine = sumpf.modules.SineWaveGenerator(frequency=1000.0,
                                                phase=1.3,
                                                samplingrate=64.203,
                                                length=13).GetSignal()
        self.assertEqual(asine, gsine)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.ArbitrarySignalGenerator()
        self.assertEqual(gen.SetFunction.GetType(), collections.Callable)
        self.assertEqual(gen.SetLabel.GetType(), str)
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetSamplingRate.GetType(), float)
        self.assertEqual(gen.GetSignal.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetFunction, gen.SetLabel, gen.SetLength, gen.SetSamplingRate],
                                         noinputs=[],
                                         output=gen.GetSignal)

