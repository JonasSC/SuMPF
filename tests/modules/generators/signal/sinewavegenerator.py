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
import math
import sumpf
import _common as common


class TestSineWaveGenerator(unittest.TestCase):
    def setUp(self):
        self.frequency = 480.0
        self.factor = 10
        self.samplingrate = self.frequency * self.factor
        self.gen = sumpf.modules.SineWaveGenerator(frequency=self.frequency,
                                                   phase=0.0,
                                                   samplingrate=self.samplingrate,
                                                   length=self.samplingrate)

    def test_frequency(self):
        """
        Tests if the frequency is set correctly by finding out the distance between the 0.0-samples
        """
        last = None
        signal = self.gen.GetSignal()
        samples = signal.GetChannels()[0]
        self.assertEqual(signal.GetLabels(), ("Sine",))     # the label of the channel should be as expected
        for i in range(len(samples)):
            if samples[i] == 0.0:
                if last is not None:
                    self.assertEqual(i - last, self.factor)
                last = i
        self.assertIsNotNone(last)                          # there should be a 0.0-sample in the Signal

    def test_phase(self):
        """
        Tests if setting the phase works correctly
        """
        samples = self.gen.GetSignal().GetChannels()[0]
        self.assertEqual(samples[0], 0.0)               # Check if the sine with phase of 0 starts with 0...
        self.assertGreater(samples[1], samples[0])      #  ... and raises from that point on
        self.gen.SetPhase(math.pi / 2)
        samples = self.gen.GetSignal().GetChannels()[0]
        self.assertAlmostEqual(samples[0], 1.0)         # Check if the sine with phase of pi/2 starts with 1...
        self.assertLess(samples[1], samples[0])         #  ... and falls from that point on
        self.gen.SetPhaseInDegrees(180.0)
        samples = self.gen.GetSignal().GetChannels()[0]
        self.assertAlmostEqual(samples[0], 0.0)         # Check if the sine with phase of 180 degrees starts with 0...
        self.assertLess(samples[1], samples[0])         #  ... and falls from that point on

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.SineWaveGenerator()
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetSamplingRate.GetType(), float)
        self.assertEqual(gen.SetFrequency.GetType(), float)
        self.assertEqual(gen.SetPhase.GetType(), float)
        self.assertEqual(gen.GetSignal.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetLength, gen.SetSamplingRate, gen.SetFrequency, gen.SetPhase],
                                         noinputs=[],
                                         output=gen.GetSignal)

