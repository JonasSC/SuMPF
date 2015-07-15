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


class TestTriangleWaveGenerator(unittest.TestCase):
    def setUp(self):
        self.frequency = 23.0
        self.factor = 20.0
        self.samplingrate = self.frequency * self.factor
        self.gen = sumpf.modules.TriangleWaveGenerator(frequency=self.frequency,
                                                       phase=0.0,
                                                       samplingrate=self.samplingrate,
                                                       length=self.samplingrate)

    def test_frequency(self):
        """
        Tests if the frequency is set correctly by finding out the distance
        between the edges of the Signal's derivative.
        """
        signal = self.gen.GetSignal()
        self.assertEqual(signal.GetLabels(), ("Triangle",))     # the label of the channel should be as expected
        diff = sumpf.modules.DifferentiateSignal(signal=signal).GetOutput()
        ddiff = sumpf.modules.AmplifySignal(input=diff, factor=1.0 / (4 * self.frequency)).GetOutput()
        dsamples = ddiff.GetChannels()[0]
        for i in range(len(dsamples)):
            r1 = float(i) * self.frequency / float(self.samplingrate)
            r2 = float(i + 1) * self.frequency / float(self.samplingrate)
            r1 -= int(r1)
            r2 -= int(r2)
            s = round(dsamples[i], 7)
            if r1 <= 0.25 < r2:
                self.assertIn(s, [0.0, 1.0])
            elif r1 <= 0.75 < r2:
                self.assertIn(s, [0.0, -1.0])
            elif r1 < 0.25 or 0.75 < r1:
                self.assertEqual(s, 1.0)
            else:
                self.assertEqual(s, -1.0)

    def test_raising(self):
        """
        Tests if the setting of the raising-ratio works.
        """
        self.assertRaises(ValueError, self.gen.SetRaising, -0.01)
        self.assertRaises(ValueError, self.gen.SetRaising, 1.01)
        self.gen.SetRaising(1.0)
        diff = sumpf.modules.DifferentiateSignal()
        sumpf.connect(self.gen.GetSignal, diff.SetInput)
        count = 0
        for s in diff.GetOutput().GetChannels()[0]:
            if round(s - 2.0 * self.frequency, 7) != 0.0:
                self.assertLess(s, 0.0)
                count += 1
        self.assertEqual(count, int(self.frequency))
        self.gen.SetRaising(0.0)
        self.gen.SetPhase(math.pi)
        count = 0
        for s in diff.GetOutput().GetChannels()[0]:
            if round(s + 2.0 * self.frequency, 7) != 0.0:
                self.assertGreater(s, 0.0)
                count += 1
        self.assertEqual(count, int(self.frequency))

    def test_phase(self):
        """
        Tests if setting the phase works correctly.
        """
        self.gen.SetPhase(math.pi / 2)
        samples = self.gen.GetSignal().GetChannels()[0]
        self.assertEqual(samples[0], 1.0)               # Check if the wave with phase of pi/2 starts with 1.0...
        self.assertGreater(samples[1], samples[2])      #  ... and falls from there on
        self.gen.SetPhaseInDegrees(180.0)
        samples = self.gen.GetSignal().GetChannels()[0]
        self.assertEqual(samples[0], 0.0)               # Check if the wave with phase of 180 degrees starts with 0.0...
        self.assertGreater(samples[1], samples[2])      #  ... and falls from there on

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.TriangleWaveGenerator()
        self.assertEqual(gen.SetRaising.GetType(), float)
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetSamplingRate.GetType(), float)
        self.assertEqual(gen.SetFrequency.GetType(), float)
        self.assertEqual(gen.SetPhase.GetType(), float)
        self.assertEqual(gen.GetSignal.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetRaising, gen.SetLength, gen.SetSamplingRate, gen.SetFrequency, gen.SetPhase],
                                         noinputs=[],
                                         output=gen.GetSignal)

