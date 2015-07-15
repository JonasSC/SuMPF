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


class TestReverseSignal(unittest.TestCase):
    """
    A test case for the ReverseSignal module.
    """
    def test_reversal(self):
        """
        Tests if the reversal of a Signal works as expected.
        """
        channels = ((1.0, 2.0, 3.0, 4.0, 5.0), (6.0, 7.0, 8.0, 9.0, 10.0))
        reversed_channels = ((5.0, 4.0, 3.0, 2.0, 1.0), (10.0, 9.0, 8.0, 7.0, 6.0))
        samplingrate = 77.3
        labels = ("Radio One", "BBC 2")
        signal = sumpf.Signal(channels=channels, samplingrate=samplingrate, labels=labels)
        reversed_signal = sumpf.Signal(channels=reversed_channels, samplingrate=samplingrate, labels=labels)
        rev = sumpf.modules.ReverseSignal(signal=signal)
        output1 = rev.GetOutput()
        self.assertEqual(output1, reversed_signal)
        rev.SetInput(output1)
        output2 = rev.GetOutput()
        self.assertEqual(output2, signal)

    def test_mutable_input(self):
        """
        Tests if the reversal of a Signal modifies the input signal, even if the
        input signal's channels are stored in mutable containers like lists.
        """
        immutable_channels = ((1.0, 2.0, 3.0, 4.0, 5.0), (6.0, 7.0, 8.0, 9.0, 10.0))
        mutable_channels = [[1.0, 2.0, 3.0, 4.0, 5.0], [6.0, 7.0, 8.0, 9.0, 10.0]]
        samplingrate = 77.3
        labels = ("Radio One", "BBC 2")
        immutable_signal = sumpf.Signal(channels=immutable_channels, samplingrate=samplingrate, labels=labels)
        mutable_signal = sumpf.Signal(channels=mutable_channels, samplingrate=samplingrate, labels=labels)
        rev = sumpf.modules.ReverseSignal(signal=mutable_signal)
        rev.GetOutput()
        rev.SetInput(mutable_signal)
        rev.GetOutput()
        self.assertEqual(mutable_signal, immutable_signal)

    def test_connections(self):
        """
        Tests the connections of the concatenation module.
        """
        ccs = sumpf.modules.ReverseSignal()
        self.assertEqual(ccs.SetInput.GetType(), sumpf.Signal)
        self.assertEqual(ccs.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[ccs.SetInput],
                                         noinputs=[],
                                         output=ccs.GetOutput)

