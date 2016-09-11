# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2016 Jonas Schulte-Coerne
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

class TestLevel(unittest.TestCase):
    """
    A test case for the Level class.
    """
    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_multichannel_input(self):
        """
        Tests if signals with multiple channels are computed as expected.
        """
        constant = sumpf.modules.ConstantSignalGenerator(value=2.0)
        square = sumpf.modules.SquareWaveGenerator(frequency=6.0 / constant.GetSignal().GetDuration())
        merger = sumpf.modules.MergeSignals()
        sumpf.connect(constant.GetSignal, merger.AddInput)
        sumpf.connect(square.GetSignal, merger.AddInput)
        level = sumpf.modules.Level()
        self.assertEqual(level.GetLevel(), (0.0,))
        sumpf.connect(merger.GetOutput, level.SetSignal)
        for p in range(1, 4 + 1):
            level.SetPower(p)
            level.SetRoot(p)
            result = level.GetLevel()
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], 2.0)
            if p % 2 == 0:
                self.assertEqual(result[1], 1.0)
            else:
                self.assertEqual(result[1], 0.0)

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_sine(self):
        """
        Tests computing the RMS value of a sine wave.
        """
        sine = sumpf.modules.SineWaveGenerator().GetSignal()
        level = sumpf.modules.Level(signal=sine).GetLevel()[0]
        self.assertAlmostEqual(level, 0.5 ** 0.5, 4)

    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_sampling_rate(self):
        """
        Tests that the sampling rate does not affect the computed level.
        """
        signal1 = sumpf.modules.WindowGenerator(raise_interval=(0, 1000),
                                                fall_interval=(1000, 2000),
                                                function=sumpf.modules.WindowGenerator.VonHann(),
                                                samplingrate=1000.0,
                                                length=2000.0).GetSignal()
        signal2 = sumpf.modules.WindowGenerator(raise_interval=(0, 3000),
                                                fall_interval=(3000, 6000),
                                                function=sumpf.modules.WindowGenerator.VonHann(),
                                                samplingrate=3000.0,
                                                length=6000.0).GetSignal()
        self.assertAlmostEqual(sumpf.modules.Level(signal=signal1).GetLevel()[0],
                               sumpf.modules.Level(signal=signal2).GetLevel()[0],
                               3)

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_compare_with_mean(self):
        """
        Compares the results of the Level class with the results of the SignalMean class.
        """
        noise = sumpf.modules.NoiseGenerator(seed=1108).GetSignal()
        level = sumpf.modules.Level(signal=noise, power=1.0, root=1.0).GetLevel()
        mean = sumpf.modules.SignalMean(signal=noise).GetMean()
        self.assertEqual(level, mean)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        lvl = sumpf.modules.Level()
        self.assertEqual(lvl.SetSignal.GetType(), sumpf.Signal)
        self.assertEqual(lvl.SetPower.GetType(), float)
        self.assertEqual(lvl.SetRoot.GetType(), float)
        self.assertEqual(lvl.GetLevel.GetType(), tuple)
        common.test_connection_observers(testcase=self,
                                         inputs=[lvl.SetSignal, lvl.SetPower, lvl.SetRoot],
                                         noinputs=[],
                                         output=lvl.GetLevel)

