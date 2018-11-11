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


class TestRepeatSignal(unittest.TestCase):
    """
    A test case for the ShiftSignal module.
    """
    def test_function(self):
        """
        Tests the basic functionality of the RepeatSignal module.
        """
        # test signals
        signal = sumpf.Signal(channels=((1.0, 2.0, 3.0), (4.0, 5.0, 6.0)), samplingrate=12.0, labels=("1", None))
        signal2 = sumpf.Signal(channels=((1.0, 2.0, 3.0, 1.0, 2.0, 3.0), (4.0, 5.0, 6.0, 4.0, 5.0, 6.0)), samplingrate=12.0, labels=("1", None))
        signal3 = sumpf.Signal(channels=((1.0, 2.0, 3.0, 1.0, 2.0, 3.0, 1.0, 2.0, 3.0), (4.0, 5.0, 6.0, 4.0, 5.0, 6.0, 4.0, 5.0, 6.0)), samplingrate=12.0, labels=("1", None))
        # tests
        self.assertEqual(sumpf.modules.RepeatSignal(signal=signal).GetOutput(), signal)
        self.assertEqual(sumpf.modules.RepeatSignal(signal=signal, repetitions=2).GetOutput(), signal2)
        rep = sumpf.modules.RepeatSignal()
        rep.SetSignal(signal)
        rep.SetRepetitions(3)
        self.assertEqual(rep.GetOutput(), signal3)

    def test_uncommon_repetitions(self):
        """
        Tests uncommon values for the repetitions, that might provoke errors.
        """
        signal = sumpf.Signal(channels=((1.0, 2.0, 3.0), (4.0, 5.0, 6.0)), samplingrate=12.0, labels=("1", None))
        empty = sumpf.Signal(channels=((0.0, 0.0), (0.0, 0.0)), samplingrate=12.0, labels=("1", None))
        # setting a repetition of 0 shall return an empty Signal with the same number of channels, samplingrate and labels as the input signal
        self.assertEqual(sumpf.modules.RepeatSignal(signal=signal, repetitions=0).GetOutput(), empty)
        # setting a negative number of repetition shall raise a ValueError, when the output signal is computed
        rep = sumpf.modules.RepeatSignal(signal=signal)
        rep.SetRepetitions(-2)  # no error here
        self.assertRaises(ValueError, rep.GetOutput)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        rep = sumpf.modules.RepeatSignal()
        self.assertEqual(rep.SetSignal.GetType(), sumpf.Signal)
        self.assertEqual(rep.SetRepetitions.GetType(), int)
        self.assertEqual(rep.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[rep.SetSignal, rep.SetRepetitions],
                                         noinputs=[],
                                         output=rep.GetOutput)

