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


class TestAmplifySignal(unittest.TestCase):
    """
    A TestCase for the AmplifySignal module.
    """
    def test_get_set(self):
        """
        Tests if the getter and setter methods work as expected.
        """
        signal = sumpf.Signal(channels=((1.0, 2.0, 3.0),), samplingrate=17.0, labels=("label",))
        amp = sumpf.modules.AmplifySignal()
        self.assertIsNone(amp._input)                               # the object initialized without arguments should be empty
        amp.SetInput(signal)
        amp.SetAmplificationFactor(1.5)
        output = amp.GetOutput()
        self.assertEqual(output.GetSamplingRate(), 17)              # the sampling rate should have been taken from input Signal
        self.assertEqual(output.GetChannels(), ((1.5, 3.0, 4.5),))  # the amplified Signal should have been calculated correctly
        self.assertEqual(output.GetLabels(), ("label",))            # the amplified Signal should have the same label as the input Signal

    def test_constructor(self):
        """
        Tests if setting the data via the constructor works.
        """
        signal = sumpf.Signal(channels=((1.0, 2.0, 3.0),), samplingrate=9.0)
        amp = sumpf.modules.AmplifySignal(signal)
        amp.SetAmplificationFactor(2.5)
        output = amp.GetOutput()
        self.assertEqual(output.GetSamplingRate(), 9)               # the sampling rate should have been taken from input Signal
        self.assertEqual(output.GetChannels(), ((2.5, 5.0, 7.5),))  # the amplified Signal should have been calculated correctly

    def test_connections(self):
        """
        tests if calculating the amplified Signal through connections is possible.
        """
        con = ConnectionTester()
        amp = sumpf.modules.AmplifySignal()
        sumpf.connect(amp.GetOutput, con.Trigger)
        sumpf.connect(con.GetSignal, amp.SetInput)
        self.assertTrue(con.triggered)  # setting the input should have triggered the trigger
        con.triggered = False
        sumpf.connect(con.GetScalarFactor, amp.SetAmplificationFactor)
        self.assertTrue(con.triggered)  # setting the amplification should have triggered the trigger
        output = amp.GetOutput()
        self.assertEqual(output.GetSamplingRate(), 42)
        self.assertEqual(output.GetChannels(), ((2.0, 4.0, 6.0),))

    def test_vectorial_factor(self):
        """
        tests if a vectorial amplification factor works as expected.
        """
        con = ConnectionTester()
        amp = sumpf.modules.AmplifySignal()
        channels = len(con.GetVectorialFactor())
        cpy = sumpf.modules.CopySignalChannels(channelcount=channels)
        sumpf.connect(con.GetSignal, cpy.SetInput)
        sumpf.connect(cpy.GetOutput, amp.SetInput)
        sumpf.connect(con.GetVectorialFactor, amp.SetAmplificationFactor)
        self.assertEqual(amp.GetOutput().GetChannels(), ((1.0, 2.0, 3.0), (2.0, 4.0, 6.0), (3.0, 6.0, 9.0)))
        cpy.SetChannelCount(channels - 1)
        self.assertEqual(amp.GetOutput().GetChannels(), ((1.0, 2.0, 3.0), (2.0, 4.0, 6.0)))
        cpy.SetChannelCount(channels + 1)
        self.assertEqual(amp.GetOutput().GetChannels(), ((1.0, 2.0, 3.0), (1.0, 2.0, 3.0), (1.0, 2.0, 3.0), (1.0, 2.0, 3.0)))

