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


class TestSquareWaveGenerator(unittest.TestCase):
    def setUp(self):
        self.frequency = 50.0
        self.factor = 11
        self.samplingrate = self.frequency * self.factor
        self.gen = sumpf.modules.SquareWaveGenerator(dutycycle=0.5,
                                                     frequency=self.frequency,
                                                     phase=0.0,
                                                     samplingrate=self.samplingrate,
                                                     length=self.samplingrate)

    def test_frequency(self):
        """
        Tests if the frequency is set correctly by finding out the distance
        between the Signal's edges.
        """
        for dc in [0.3, 0.5, 0.7]:
            self.gen.SetDutyCycle(dc)
            signal = self.gen.GetSignal()
            samples = signal.GetChannels()[0]
            self.assertSetEqual(set(samples), set([-1.0, 1.0])) # all samples should either be 1.0 or -1.0
            self.assertEqual(signal.GetLabels(), ("Square",))   # the label of the channel should be as expected
            last = None
            avg = sumpf.helper.average.SortedSum()
            for i in range(1, len(samples)):
                if samples[i] > samples[i - 1]:
                    if last is not None:
                        avg.Add(i - last)
                    last = i
            self.assertEqual(avg.GetAverage(), self.factor)
            self.assertIsNotNone(last)                          # there should be an edge in the Signal

    def test_phase(self):
        """
        Tests if setting the phase works correctly.
        """
        samples = self.gen.GetSignal().GetChannels()[0]
        self.assertEqual(samples[0], 1.0)                                               # Check if the square wave with phase of 0 starts with 1.0
        self.assertGreater(samples[self.factor // 2], samples[self.factor // 2 + 1])    #  ... and falls after half a period
        self.gen.SetPhase(math.pi / 2)
        samples = self.gen.GetSignal().GetChannels()[0]
        self.assertEqual(samples[0], 1.0)                                               # Check if the square wave with phase of pi/2 starts with 1.0...
        self.assertGreater(samples[self.factor // 4], samples[self.factor // 4 + 1])    #  ... and falls after a quarter of a period
        self.gen.SetPhaseInDegrees(180.0)
        samples = self.gen.GetSignal().GetChannels()[0]
        self.assertEqual(samples[0], -1.0)                                              # Check if the square wave with phase of 180 degrees starts with -1.0...
        self.assertLess(samples[self.factor // 2], samples[self.factor // 2 + 1])       #  ... and raises after half a period

    def test_duty_cycle(self):
        """
        Tests the duty cycle of the square wave generator.
        """
        self.assertRaises(ValueError, self.gen.SetDutyCycle, -0.1)
        self.assertRaises(ValueError, self.gen.SetDutyCycle, 1.1)
        self.gen.SetLength(100)         # Create a period length for which the
        self.gen.SetSamplingRate(100.0) # square wave has the exact right duty
        self.gen.SetFrequency(1.0)      # cycle for each of the tested duty cycles
        for i in range(11):
            duty_cycle = i / 10.0
            self.gen.SetDutyCycle(duty_cycle)
            average = sumpf.helper.average.SortedSum(values=self.gen.GetSignal().GetChannels()[0]).GetAverage()
            self.assertAlmostEqual(average, -1.0 + 2.0 * duty_cycle)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.SquareWaveGenerator()
        self.assertEqual(gen.SetDutyCycle.GetType(), float)
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetSamplingRate.GetType(), float)
        self.assertEqual(gen.SetFrequency.GetType(), float)
        self.assertEqual(gen.SetPhase.GetType(), float)
        self.assertEqual(gen.GetSignal.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetDutyCycle, gen.SetLength, gen.SetSamplingRate, gen.SetFrequency, gen.SetPhase],
                                         noinputs=[],
                                         output=gen.GetSignal)

