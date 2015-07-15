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
from .connectiontester import ConnectionTester


class TestAverageSignals(unittest.TestCase):
    """
    A TestCase for the AverageSignals module.
    """
    def test_get_set(self):
        """
        Tests if the getter and setter methods work as expected.
        """
        signal1 = sumpf.Signal(channels=((1.0, 2.0, 3.0),), samplingrate=17.0)
        signal2 = sumpf.Signal(channels=((3.0, 1.0, 2.0),), samplingrate=17.0)
        signal3 = sumpf.Signal(channels=((2.0, 3.0, 1.0),), samplingrate=17.0)
        avg = sumpf.modules.AverageSignals()
        self.assertIsNone(avg._lastdataset)                         # an object initialized without arguments should be empty
        avg.AddInput(signal1)
        avg.AddInput(signal2)
        avg.AddInput(signal3)
        output = avg.GetOutput()
        self.assertEqual(output.GetSamplingRate(), 17.0)            # the sampling rate should be taken from input Signals
        self.assertEqual(output.GetChannels(), ((2.0, 2.0, 2.0),))  # the average should be calculated correctly
        self.assertEqual(output.GetLabels(), ("Average 1",))        # the label should be set correctly

    def test_constructor(self):
        """
        Tests if setting the data via the constructor works.
        """
        signal1 = sumpf.Signal(channels=((1.0, 2.0, 3.0),), samplingrate=9.0)
        signal2 = sumpf.Signal(channels=((3.0, 1.0, 2.0),), samplingrate=9.0)
        signal3 = sumpf.Signal(channels=((2.0, 3.0, 1.0),), samplingrate=9.0)
        avg = sumpf.modules.AverageSignals(signals=[signal1, signal2, signal3])
        output = avg.GetOutput()
        self.assertEqual(output.GetSamplingRate(), 9)
        self.assertEqual(output.GetChannels(), ((2.0, 2.0, 2.0),))

    def test_connections(self):
        """
        tests if calculating the average through connections is possible.
        """
        gen = ConnectionTester()
        avg = sumpf.modules.AverageSignals()
        sumpf.connect(gen.GetSignal, avg.AddInput)
        sumpf.connect(avg.TriggerDataCreation, gen.Start)
        avg.SetNumber(10)
        avg.Start()
        output = avg.GetOutput()
        self.assertEqual(output.GetSamplingRate(), 42)
        self.assertEqual(output.GetChannels(), ((4.5, 9.0, 13.5),))

    def test_errors(self):
        """
        Tests if errors are raised as expected.
        """
        signal1 = sumpf.Signal(channels=((1.0, 2.0, 3.0),), samplingrate=17.0)
        signal2 = sumpf.Signal(channels=((3.0, 1.0),), samplingrate=17.0)
        signal3 = sumpf.Signal(channels=((2.0, 3.0, 1.0), (2.0, 2.0, 2.0)), samplingrate=17.0)
        signal4 = sumpf.Signal(channels=((2.0, 3.0, 1.0),), samplingrate=9.0)
        avg = sumpf.modules.AverageSignals()
        avg.AddInput(signal1)
        self.assertRaises(ValueError, avg.AddInput, signal2)                # should fail because of length conflict
        self.assertRaises(ValueError, avg.AddInput, signal3)                # should fail because of channel count conflict
        self.assertRaises(ValueError, avg.AddInput, signal4)                # should fail because of sampling rate conflict
        self.assertRaises(ValueError, sumpf.modules.AverageSignals, [signal1, signal2]) # signals should also be checked in the constructor

