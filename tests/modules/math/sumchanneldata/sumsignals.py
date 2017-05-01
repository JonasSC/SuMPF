# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2017 Jonas Schulte-Coerne
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


class TestSumSignals(unittest.TestCase):
    """
    A test case for the SumSignals module
    """
    def setUp(self):
        self.signal1 = sumpf.Signal(channels=((11.1, 11.2, 11.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3)), samplingrate=42.0, labels=("1.1", "1.2", "1.3"))
        self.signal2 = sumpf.Signal(channels=((21.1, 21.2, 21.3), (22.1, 22.2, 22.3), (23.1, 23.2, 23.3)), samplingrate=42.0, labels=("2.1", "2.2", "2.3"))
        self.signal3 = sumpf.Signal(channels=((31.1, 31.2), (32.1, 32.2), (33.1, 33.2)), samplingrate=42.0)
        self.signal3_0 = sumpf.Signal(channels=((31.1, 31.2, 0.0), (32.1, 32.2, 0.0), (33.1, 33.2, 0.0)), samplingrate=42.0)
        self.signal4 = sumpf.Signal(channels=((41.1, 41.2, 41.3), (42.1, 42.2, 42.3), (43.1, 43.2, 43.3)), samplingrate=23.0)
        self.signal5 = sumpf.Signal(channels=((51.1, 51.2, 51.3), (52.1, 52.2, 52.3)), samplingrate=42.0)
        self.signal6 = sumpf.Signal(channels=((61.1, 61.2, 61.3),), samplingrate=42.0)

    def test_constructor_and_clear(self):
        """
        Tests if adding a list of Signals with the constructor works and if removing them with the Clear method works.
        """
        sumsignals = sumpf.modules.SumSignals(signals=[self.signal1, self.signal2])
        self.assertEqual(sumsignals.GetOutput(), self.signal1 + self.signal2)
        sumsignals.Clear()
        self.assertEqual(sumsignals.GetOutput(), sumpf.Signal())
        quicksummed = sumpf.modules.SumSignals([self.signal1, self.signal2]).GetOutput()
        self.assertEqual(quicksummed, self.signal1 + self.signal2)
        self.assertRaises(ValueError, sumpf.modules.SumSignals([self.signal1, self.signal2, self.signal3]).GetOutput)
        self.assertEqual(sumpf.modules.SumSignals([self.signal1, self.signal2, self.signal3], on_length_conflict=sumpf.modules.SumSignals.FILL_WITH_ZEROS).GetOutput(), self.signal1 + self.signal2 + self.signal3_0)

    def test_summation(self):
        """
        Tests if the summation works as expected
        """
        sumsignals = sumpf.modules.SumSignals()
        self.assertEqual(sumsignals.GetOutput(), sumpf.Signal())
        id1 = sumsignals.AddInput(self.signal1)
        self.assertEqual(sumsignals.GetOutput(), self.signal1)
        sumsignals.AddInput(self.signal2)
        self.assertEqual(sumsignals.GetOutput(), self.signal1 + self.signal2)
        sumsignals.RemoveInput(id1)
        self.assertEqual(sumsignals.GetOutput(), self.signal2)
        sumsignals.AddInput(self.signal3)
        sumsignals.SetLengthConflictStrategy(sumpf.modules.SumSignals.FILL_WITH_ZEROS)
        self.assertEqual(sumsignals.GetOutput(), self.signal2 + self.signal3_0)
        sumsignals.SetLengthConflictStrategy(sumpf.modules.SumSignals.CROP)
        self.assertEqual(sumsignals.GetOutput(), (self.signal2 + self.signal3_0)[0:len(self.signal3)])
        sumsignals.Clear()
        sumsignals.AddInput(self.signal4)
        self.assertEqual(sumsignals.GetOutput(), self.signal4)

    def test_errors(self):
        """
        Tests if errors are raised correctly
        """
        self.assertRaises(ValueError, sumpf.modules.SumSignals().RemoveInput, 3)
        self.assertRaises(ValueError, sumpf.modules.SumSignals([self.signal1, self.signal3]).GetOutput)
        self.assertRaises(ValueError, sumpf.modules.SumSignals([self.signal1, self.signal4]).GetOutput)
        self.assertRaises(ValueError, sumpf.modules.SumSignals([self.signal1, self.signal5]).GetOutput)
        self.assertRaises(ValueError, sumpf.modules.SumSignals([self.signal1, self.signal6]).GetOutput)
        self.assertRaises(ValueError, sumpf.modules.SumSignals([self.signal3, self.signal6], on_length_conflict=sumpf.modules.SumSignals.FILL_WITH_ZEROS).GetOutput)
        self.assertRaises(ValueError, sumpf.modules.SumSignals([self.signal3, self.signal6], on_length_conflict=sumpf.modules.SumSignals.CROP).GetOutput)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        sumsignals = sumpf.modules.SumSignals()
        self.assertEqual(sumsignals.AddInput.GetType(), sumpf.Signal)
        self.assertEqual(sumsignals.SetLengthConflictStrategy.GetType(), int)
        self.assertEqual(sumsignals.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[sumsignals.AddInput, sumsignals.SetLengthConflictStrategy, sumsignals.Clear],
                                         noinputs=[],
                                         output=sumsignals.GetOutput)

