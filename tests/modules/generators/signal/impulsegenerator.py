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


class TestImpulseGenerator(unittest.TestCase):
    """
    A TestCase for the ImpulseGenerator module.
    """
    def setUp(self):
        self.len = 100
        self.smr = 100.0
        self.gen = sumpf.modules.ImpulseGenerator(delay=0.0,
                                                  frequency=0.0,
                                                  samplingrate=self.smr,
                                                  length=self.len)

    def test_no_repeats(self):
        """
        Tests if there is only one 1.0 sample at the correct position in the output signal
        """
        signal = self.gen.GetSignal()
        self.assertEqual(signal.GetLabels(), ("Impulse",))  # the label of the channel should be as expected
        samples = signal.GetChannels()[0]
        self.assertEqual(samples[0], 1.0)                   # first sample has to be 1.0
        for i in range(1, len(samples)):
            self.assertEqual(samples[i], 0.0)               # the other samples have to be 0.0
        self.gen.SetDelay(0.5)
        samples = self.gen.GetSignal().GetChannels()[0]
        for i in range(0, 50):
            self.assertEqual(samples[i], 0.0)               # the first samples have to be 0.0
        self.assertEqual(samples[50], 1.0)                  # after the delay, the sample has to be 1.0
        for i in range(51, len(samples)):
            self.assertEqual(samples[i], 0.0)               # the other samples have to be 0.0

    def test_with_repeats(self):
        """
        Tests if the repetition of impulses works correctly
        """
        self.gen.SetFrequency(self.len)
        signal = self.gen.GetSignal()
        samples = signal.GetChannels()[0]
        self.assertEqual(signal.GetLabels(), ("Impulse Sequence",))         # the label of the channel should be as expected
        for s in samples:
            self.assertEqual(s, 1.0)                                        # test a frequency that by which the sampling rate can be divided cleanly
        divisor = 8.2
        self.gen.SetFrequency(self.len / divisor)
        samples = self.gen.GetSignal().GetChannels()[0]
        for a in range(0, int(round(self.len / divisor)) + 1):
            self.assertEqual(samples[a * int(round(divisor))], 1.0)         # test a frequency that has to be rounded down
            for b in range(min(len(samples), a * int(round(divisor)) + 1),
                           min(len(samples), (a + 1) * int(round(divisor)))):
                self.assertEqual(samples[b], 0.0)                           # test a frequency that has to be rounded down
        divisor = 7.6
        self.gen.SetFrequency(self.len / divisor)
        samples = self.gen.GetSignal().GetChannels()[0]
        for a in range(0, int(round(self.len / divisor))):
            self.assertEqual(samples[a * int(round(divisor))], 1.0)         # test a frequency that has to be rounded up
            for b in range(min(len(samples), a * int(round(divisor)) + 1),
                           min(len(samples), (a + 1) * int(round(divisor)))):
                self.assertEqual(samples[b], 0.0)                           # test a frequency that has to be rounded up

    def test_errors(self):
        """
        Tests if errors are raised correctly
        """
        self.gen.SetDelay((self.len / self.smr) + 1)
        self.assertRaises(ValueError, self.gen.GetSignal)       # generating a Signal with a greater initial delay than the length of the Signal shall raise an error

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.ImpulseGenerator()
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetSamplingRate.GetType(), float)
        self.assertEqual(gen.SetDelay.GetType(), float)
        self.assertEqual(gen.SetFrequency.GetType(), float)
        self.assertEqual(gen.GetSignal.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetLength, gen.SetSamplingRate, gen.SetDelay, gen.SetFrequency],
                                         noinputs=[],
                                         output=gen.GetSignal)

