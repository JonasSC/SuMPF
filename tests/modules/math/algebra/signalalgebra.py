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


class TestSignalAlgebra(unittest.TestCase):
    """
    A test case for the algebra modules for Signals.
    """
    def setUp(self):
        self.signal1 = sumpf.Signal(channels=((4.0, 6.0, 9.34), (3.0, 5.0, 8.4)), samplingrate=62.33)
        self.signal2 = sumpf.Signal(channels=((2.0, 1.0, 14.2), (3.0, 7.0, 2.1)), samplingrate=62.33)
        self.wrongsamplingrate = 59.78

    def test_results(self):
        """
        Tests if the calculations yield the expected results.
        """
        self.assertEqual(sumpf.modules.AddSignals(signal1=self.signal1, signal2=self.signal2).GetOutput(), self.signal1 + self.signal2)
        self.assertEqual(sumpf.modules.SubtractSignals(signal1=self.signal1, signal2=self.signal2).GetOutput(), self.signal1 - self.signal2)
        self.assertEqual(sumpf.modules.MultiplySignals(signal1=self.signal1, signal2=self.signal2).GetOutput(), self.signal1 * self.signal2)
        self.assertEqual(sumpf.modules.DivideSignals(signal1=self.signal1, signal2=self.signal2).GetOutput(), self.signal1 / self.signal2)

    def test_compare(self):
        """
        Tests the comparison of Signals.
        """
        comparator = sumpf.modules.CompareSignals()
        comparator.SetInput1(self.signal1)
        comparator.SetInput2(self.signal2)
        result = comparator.GetOutput()
        self.assertEqual(result.GetChannels(), ((1.0, 1.0, -1.0), (0.0, -1.0, 1.0)))
        self.assertEqual(result.GetSamplingRate(), 62.33)
        self.assertEqual(result.GetLabels(), ("Comparison 1", "Comparison 2"))

    def test_empty_signals(self):
        """
        Tests the algebra modules in case at least one of the input Signals is empty.
        """
        wrong_samplingrate = sumpf.Signal(channels=((0.0, 0.0), (0.0, 0.0)), samplingrate=self.wrongsamplingrate)
        wrong_channelcount = sumpf.Signal(samplingrate=self.signal1.GetSamplingRate())
        wrong_length = sumpf.Signal(channels=((0.0, 0.0), (0.0, 0.0)), samplingrate=self.signal1.GetSamplingRate(), labels=("These should", "not be copied"))
        for m in [sumpf.modules.AddSignals(),
                  sumpf.modules.SubtractSignals(),
                  sumpf.modules.MultiplySignals(),
                  sumpf.modules.DivideSignals(),
                  sumpf.modules.CompareSignals()]:
            m.SetInput1(self.signal1)
            m.SetInput2(wrong_samplingrate)
            self.assertEqual(m.GetOutput(), sumpf.Signal())
            m.SetInput1(wrong_channelcount)
            m.SetInput2(self.signal1)
            self.assertEqual(m.GetOutput(), sumpf.Signal(samplingrate=self.signal1.GetSamplingRate()))
            m.SetInput1(wrong_length)
            self.assertEqual(m.GetOutput(), sumpf.Signal(channels=wrong_length.GetChannels(), samplingrate=self.signal1.GetSamplingRate()))
        self.assertEqual(sumpf.modules.DivideSignals(signal1=wrong_length, signal2=wrong_length).GetOutput(),
                         sumpf.Signal(channels=wrong_length.GetChannels(), samplingrate=self.signal1.GetSamplingRate()))

    def test_errors(self):
        """
        Tests if the algebra modules raise errors correctly.
        """
        wrong_samplingrate = sumpf.Signal(channels=self.signal2.GetChannels(), samplingrate=self.wrongsamplingrate)
        wrong_channelcount = sumpf.Signal(channels=(self.signal2.GetChannels()[0],), samplingrate=self.signal1.GetSamplingRate())
        wrong_length = self.signal2[0:2]
        for cls in [sumpf.modules.AddSignals,
                    sumpf.modules.SubtractSignals,
                    sumpf.modules.MultiplySignals,
                    sumpf.modules.DivideSignals,
                    sumpf.modules.CompareSignals]:
            for wrong_signal in [wrong_samplingrate, wrong_channelcount, wrong_length]:
                self.assertRaises(ValueError, cls(signal1=self.signal1, signal2=wrong_signal).GetOutput)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        for m in [sumpf.modules.AddSignals(),
                  sumpf.modules.SubtractSignals(),
                  sumpf.modules.MultiplySignals(),
                  sumpf.modules.DivideSignals(),
                  sumpf.modules.CompareSignals()]:
            self.assertEqual(m.SetInput1.GetType(), sumpf.Signal)
            self.assertEqual(m.SetInput2.GetType(), sumpf.Signal)
            self.assertEqual(m.GetOutput.GetType(), sumpf.Signal)
            common.test_connection_observers(testcase=self,
                                             inputs=[m.SetInput1, m.SetInput2],
                                             noinputs=[],
                                             output=m.GetOutput)

