# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2018 Jonas Schulte-Coerne
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


@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestWindowGenerator(unittest.TestCase):
    """
    A test case for the WindowGenerator module.
    """
    def setUp(self):
        self.gen = sumpf.modules.WindowGenerator(fall_interval=(3, 7),
                                                 function=sumpf.modules.WindowGenerator.Hamming(),  # Choose a window that does not end with zero
                                                 samplingrate=42.0,
                                                 length=10)

    def test_single_edge(self):
        """
        Tests the generation of Signals with a single edge.
        """
        output = self.gen.GetSignal()
        self.assertEqual(output.GetLabels(), ("Window",))           # the label of the channel should be as expected
        self.assertEqual(len(output), 10)                           # the length should be as defined in the constructor
        self.assertEqual(output.GetSamplingRate(), 42)              # the sampling rate should be as defined in the constructor
        self.assertEqual(output.GetChannels()[0][0:3], (1.0,) * 3)  # all samples before the window should be 1.0
        self.assertEqual(output.GetChannels()[0][7:10], (0.0,) * 3) # all samples after the window should be 0.0
        for fall in ((0, 0), (1.0, 1.0)):
            self.gen.SetFallInterval(fall)
            self.gen.SetRiseInterval((3, 7))
            output = self.gen.GetSignal()
            self.assertEqual(output.GetChannels()[0][0:3], (0.0,) * 3)  # if the window is raising all samples before the window should be 0.0
            self.assertEqual(output.GetChannels()[0][7:10], (1.0,) * 3) # if the window is raising all samples after the window should be 1.0
            self.gen.SetRiseInterval((-6, -4))
            output = self.gen.GetSignal()
            self.assertEqual(output.GetChannels()[0][0:4], (0.0,) * 4)  # the start of the window should have been set correctly via SetInterval
            self.assertEqual(output.GetChannels()[0][6:10], (1.0,) * 4) # the end of the window should have been set correctly via SetInterval
            self.gen.SetRiseInterval((5, 12))
            output = self.gen.GetSignal()
            self.assertEqual(output.GetChannels()[0][0:5], (0.0,) * 5)  # setting an interval which is larger than the length of the generated Signal should be possible
            self.assertEqual(len(output), 10)                           # the length should not be changed by the large interval

    def test_rise_fall(self):
        """
        Tests the generation of Signals with both a rising and a falling edge.
        """
        # first rise, then fall
        rising = sumpf.modules.WindowGenerator(rise_interval=(1, 4), samplingrate=42.0, length=10).GetSignal()
        falling = sumpf.modules.WindowGenerator(fall_interval=(6, 9), samplingrate=42.0, length=10).GetSignal()
        both = sumpf.modules.WindowGenerator(rise_interval=(1, 4), fall_interval=(6, 9), samplingrate=42.0, length=10).GetSignal()
        self.assertEqual(both.GetChannels(), (rising * falling).GetChannels())
        # first fall, then rise
        rising = sumpf.modules.WindowGenerator(rise_interval=(6, 9), samplingrate=42.0, length=10).GetSignal()
        falling = sumpf.modules.WindowGenerator(fall_interval=(1, 4), samplingrate=42.0, length=10).GetSignal()
        both = sumpf.modules.WindowGenerator(rise_interval=(6, 9), fall_interval=(1, 4), samplingrate=42.0, length=10).GetSignal()
        self.assertEqual(both.GetChannels(), (rising + falling).GetChannels())
        # first fall, then rise
        rising = sumpf.modules.WindowGenerator(rise_interval=(1, 9), samplingrate=42.0, length=10).GetSignal()
        falling = sumpf.modules.WindowGenerator(fall_interval=(4, 6), samplingrate=42.0, length=10).GetSignal()
        both = sumpf.modules.WindowGenerator(rise_interval=(1, 9), fall_interval=(4, 6), samplingrate=42.0, length=10).GetSignal()
        self.assertEqual(both.GetChannels(), (rising * falling).GetChannels())

    def test_negative_intervals(self):
        """
        Tests negative integers and None for the interval borders
        """
        self.assertEqual(sumpf.modules.WindowGenerator(rise_interval=(0, -7), fall_interval=(-3, -1), samplingrate=42.0, length=10).GetSignal(),
                         sumpf.modules.WindowGenerator(rise_interval=(0, 3), fall_interval=(7, 9), samplingrate=42.0, length=10).GetSignal())
        self.assertEqual(sumpf.modules.WindowGenerator(rise_interval=(-3, 1.0), fall_interval=(-10, -7), samplingrate=42.0, length=10).GetSignal(),
                         sumpf.modules.WindowGenerator(rise_interval=(7, 10), fall_interval=(0, 3), samplingrate=42.0, length=10).GetSignal())

    def test_excessive_intervals(self):
        """
        Tests intervals for the edges, that are outside the signal's length
        """
        self.assertEqual(sumpf.modules.WindowGenerator(rise_interval=(-15, -12), fall_interval=(12, 18), samplingrate=42.0, length=10).GetSignal().GetChannels(),
                         sumpf.modules.ConstantSignalGenerator(value=1.0, samplingrate=42.0, length=10).GetSignal().GetChannels())
        self.assertEqual(sumpf.modules.WindowGenerator(rise_interval=(1.2, 1.4), fall_interval=(-1.2, -1.4), samplingrate=42.0, length=10).GetSignal().GetChannels(),
                         sumpf.modules.ConstantSignalGenerator(value=0.0, samplingrate=42.0, length=10).GetSignal().GetChannels())
        self.assertEqual(sumpf.modules.WindowGenerator(rise_interval=(-1.4, -1.2), fall_interval=(-1.4, -1.2), samplingrate=42.0, length=10).GetSignal().GetChannels(),
                         sumpf.modules.ConstantSignalGenerator(value=0.0, samplingrate=42.0, length=10).GetSignal().GetChannels())
        self.assertEqual(sumpf.modules.WindowGenerator(rise_interval=(1.2, 1.4), fall_interval=(1.2, 1.4), samplingrate=42.0, length=10).GetSignal().GetChannels(),
                         sumpf.modules.ConstantSignalGenerator(value=0.0, samplingrate=42.0, length=10).GetSignal().GetChannels())

    def test_float_intervals(self):
        """
        Tests floats for the intervals
        """
        self.assertEqual(sumpf.modules.WindowGenerator(rise_interval=0.3, fall_interval=-0.3, samplingrate=42.0, length=10).GetSignal(),
                         sumpf.modules.WindowGenerator(rise_interval=(0, 3), fall_interval=(7, 10), samplingrate=42.0, length=10).GetSignal())
        self.assertEqual(sumpf.modules.WindowGenerator(rise_interval=-0.3, fall_interval=0.3, samplingrate=42.0, length=10).GetSignal(),
                         sumpf.modules.WindowGenerator(rise_interval=(7, 10), fall_interval=(0, 3), samplingrate=42.0, length=10).GetSignal())

    def test_window_functions(self):
        """
        Tests the different window functions.
        """
        # test the rectangle function
        window = sumpf.modules.WindowGenerator(rise_interval=(1, 4), fall_interval=(6, 9), function=sumpf.modules.WindowGenerator.Rectangle(), samplingrate=14.39, length=10).GetSignal()
        reference = sumpf.Signal(channels=((0.0,) + (1.0,) * 8 + (0.0,),), samplingrate=14.39, labels=("Window",))
        self.assertEqual(window, reference)
        # test the functions, that actually do a fade
        functions = [(sumpf.modules.WindowGenerator.Bartlett(), -2),    # store a tuple (function, limit)
                     (sumpf.modules.WindowGenerator.Blackman(), -1),    # where function is the WindowFunction object
                     (sumpf.modules.WindowGenerator.Hamming(), -1),     # and limit is the last sample that is not 0.0
                     (sumpf.modules.WindowGenerator.VonHann(), -2),     # so if the window ends with 0.0 limit is the last but one sample: -2
                     (sumpf.modules.WindowGenerator.Kaiser(14), -1)]    # otherwise it's the last sample: -1
        for function, limit in functions:
            # test a falling window
            self.gen.SetFunction(function)
            self.gen.SetRiseInterval((0, 0))
            self.gen.SetFallInterval((0, 1.0))
            for i, s in enumerate(self.gen.GetSignal().GetChannels()[0][0:limit]):
                self.assertNotEqual(s, 1.0)                                         # the samples of the window must not be 1.0
                self.assertNotEqual(s, 0.0)                                         # neither can they be 0.0
            if limit == -2:
                self.assertEqual(self.gen.GetSignal().GetChannels()[0][-1], 0.0)    # if the window ends with 0.0 check that last sample
            # test a rising window
            self.gen.SetFallInterval((0, 0))
            self.gen.SetRiseInterval((0, 1.0))
            for s in self.gen.GetSignal().GetChannels()[0][-1 - limit:]:
                self.assertNotEqual(s, 1.0)                                         # the samples of the window must not be 1.0
                self.assertNotEqual(s, 0.0)                                         # neither can they be 0.0
            if limit == -2:
                self.assertEqual(self.gen.GetSignal().GetChannels()[0][0], 0.0)     # if the window starts with 0.0 check that first sample

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.WindowGenerator()
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetSamplingRate.GetType(), float)
        self.assertEqual(gen.SetRiseInterval.GetType(), sumpf.SampleInterval)
        self.assertEqual(gen.SetFallInterval.GetType(), sumpf.SampleInterval)
        self.assertEqual(gen.SetFunction.GetType(), sumpf.internal.WindowFunction)
        self.assertEqual(gen.GetSignal.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetLength, gen.SetSamplingRate, gen.SetRiseInterval, gen.SetFallInterval, gen.SetFunction],
                                         noinputs=[],
                                         output=gen.GetSignal)

