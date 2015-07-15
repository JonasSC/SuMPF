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


class TestConcatenateSignals(unittest.TestCase):
    """
    A test case for the ConcatenateSignals module.
    """
    def setUp(self):
        self.signal1 = sumpf.Signal(channels=((1.0, 0.0), (3.1, 4.7)), samplingrate=48000)
        self.signal2 = sumpf.Signal(channels=((0.0, 0.5, 0.0), (2.4, 6.2, 9.8)), samplingrate=48000)

    def test_concatenation(self):
        """
        Tests if the concatenation works as expected.
        """
        ccs = sumpf.modules.ConcatenateSignals()
        self.assertEqual(ccs.GetOutput(), sumpf.Signal())
        ccs = sumpf.modules.ConcatenateSignals(signal1=self.signal1)
        self.assertEqual(ccs.GetOutput(), self.signal1)
        ccs = sumpf.modules.ConcatenateSignals(signal2=self.signal2)
        self.assertEqual(ccs.GetOutput(), self.signal2)
        ccs = sumpf.modules.ConcatenateSignals(signal1=self.signal1, signal2=self.signal2)
        self.assertEqual(ccs.GetOutputLength(), 5)
        output = ccs.GetOutput()
        self.assertEqual(output.GetChannels(), ((1.0, 0.0, 0.0, 0.5, 0.0), (3.1, 4.7, 2.4, 6.2, 9.8)))
        self.assertEqual(output.GetSamplingRate(), 48000)
        self.assertEqual(output.GetLabels(), ("Concatenation 1", "Concatenation 2"))
        ccs.SetInput2(self.signal1)
        self.assertEqual(ccs.GetOutputLength(), 4)
        output = ccs.GetOutput()
        self.assertEqual(output.GetChannels(), ((1.0, 0.0, 1.0, 0.0), (3.1, 4.7, 3.1, 4.7)))
        self.assertEqual(output.GetSamplingRate(), 48000)
        self.assertEqual(output.GetLabels(), ("Concatenation 1", "Concatenation 2"))
        ccs.SetInput1(self.signal2)
        self.assertEqual(ccs.GetOutputLength(), 5)
        output = ccs.GetOutput()
        self.assertEqual(output.GetChannels(), ((0.0, 0.5, 0.0, 1.0, 0.0), (2.4, 6.2, 9.8, 3.1, 4.7)))
        self.assertEqual(output.GetSamplingRate(), 48000)
        self.assertEqual(output.GetLabels(), ("Concatenation 1", "Concatenation 2"))
        ccs.SetInput1(sumpf.Signal())
        self.assertEqual(ccs.GetOutput(), self.signal1)
        self.assertEqual(ccs.GetOutputLength(), 2)

    def test_errors(self):
        """
        Tests if the concatenation module raises errors correctly.
        """
        wrongsignal1 = sumpf.Signal(channels=self.signal2.GetChannels(), samplingrate=44100)
        wrongsignal2 = sumpf.Signal(channels=((1.0, 0.0),), samplingrate=48000)
        self.assertRaises(ValueError, sumpf.modules.ConcatenateSignals(signal1=self.signal1, signal2=wrongsignal1).GetOutput)   # shall fail if Signals do not have the same sampling rate
        self.assertRaises(ValueError, sumpf.modules.ConcatenateSignals(signal1=self.signal1, signal2=wrongsignal2).GetOutput)   # shall fail if Signals do not have the same channel count

    def test_connections(self):
        """
        Tests the connections of the concatenation module.
        """
        ccs = sumpf.modules.ConcatenateSignals()
        self.assertEqual(ccs.SetInput1.GetType(), sumpf.Signal)
        self.assertEqual(ccs.SetInput2.GetType(), sumpf.Signal)
        self.assertEqual(ccs.GetOutput.GetType(), sumpf.Signal)
        self.assertEqual(ccs.GetOutputLength.GetType(), int)
        common.test_connection_observers(testcase=self,
                                         inputs=[ccs.SetInput1, ccs.SetInput2],
                                         noinputs=[],
                                         output=ccs.GetOutput)
        common.test_connection_observers(testcase=self,
                                         inputs=[ccs.SetInput1, ccs.SetInput2],
                                         noinputs=[],
                                         output=ccs.GetOutputLength)

