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

import collections
import unittest
import sumpf
import _common as common


class TestFindSignalValues(unittest.TestCase):
    """
    A TestCase for the FindSignalValues module.
    """
    def test_exact(self):
        """
        Tests finding an exact value.
        """
        signal = sumpf.Signal(channels=((0.0, 1.0, -1.0), (-4.0, -1.0, 34.0)), samplingrate=9.0, labels=("Tom", "Hank"))
        fnd = sumpf.modules.FindSignalValues()
        self.assertEqual(fnd.GetSampleIndices(), (0,))
        fnd.SetSignal(signal)
        self.assertEqual(fnd.GetSampleIndices(), (0, None))
        fnd.SetValues(-1.0)
        self.assertEqual(fnd.GetSampleIndices(), (2, 1))
        fnd.SetValues((1.0, 34.0))
        self.assertEqual(fnd.GetSampleIndices(), (1, 2))
        fnd.SetInterval((2, 1.0))
        self.assertEqual(fnd.GetSampleIndices(), (None, 2))

    def test_above_threshold(self):
        """
        Tests finding the index, where the index exceeds a threshold.
        """
        signal = sumpf.Signal(channels=((0.0, 1.0, -1.0), (-4.0, -1.0, 34.0)), samplingrate=9.0, labels=("Tom", "Hank"))
        fnd = sumpf.modules.FindSignalValues(check=sumpf.modules.FindSignalValues.ABOVE_THRESHOLD)
        self.assertEqual(fnd.GetSampleIndices(), (None,))
        fnd.SetSignal(signal)
        self.assertEqual(fnd.GetSampleIndices(), (1, 2))
        fnd.SetValues(-1.0)
        self.assertEqual(fnd.GetSampleIndices(), (0, 2))
        fnd.SetValues((0.5, -3.0))
        self.assertEqual(fnd.GetSampleIndices(), (1, 1))
        fnd.SetInterval((2, 1.0))
        self.assertEqual(fnd.GetSampleIndices(), (None, 2))

    def test_below_threshold(self):
        """
        Tests finding the index, where the index exceeds a threshold.
        """
        signal = sumpf.Signal(channels=((0.0, 1.0, -1.0), (-4.0, -1.0, 34.0)), samplingrate=9.0, labels=("Tom", "Hank"))
        fnd = sumpf.modules.FindSignalValues(check=sumpf.modules.FindSignalValues.BELOW_THRESHOLD)
        self.assertEqual(fnd.GetSampleIndices(), (None,))
        fnd = sumpf.modules.FindSignalValues(signal=signal, check=sumpf.modules.FindSignalValues.BELOW_THRESHOLD)
        self.assertEqual(fnd.GetSampleIndices(), (2, 0))
        fnd = sumpf.modules.FindSignalValues(signal=signal, check=sumpf.modules.FindSignalValues.BELOW_THRESHOLD, values=-1.0)
        self.assertEqual(fnd.GetSampleIndices(), (None, 0))
        fnd.SetValues((0.5, -3.0))
        self.assertEqual(fnd.GetSampleIndices(), (0, 0))
        fnd = sumpf.modules.FindSignalValues(signal=signal, check=sumpf.modules.FindSignalValues.BELOW_THRESHOLD, values=-1.0, interval=(1, 1.0))
        self.assertEqual(fnd.GetSampleIndices(), (None, None))

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        fnd = sumpf.modules.FindSignalValues()
        self.assertEqual(fnd.SetSignal.GetType(), sumpf.Signal)
        self.assertEqual(fnd.SetCheck.GetType(), collections.Callable)
        self.assertEqual(fnd.SetValues.GetType(), (collections.Iterable, float, int))
        self.assertEqual(fnd.SetInterval.GetType(), sumpf.SampleInterval)
        self.assertEqual(fnd.GetSampleIndices.GetType(), tuple)
        common.test_connection_observers(testcase=self,
                                         inputs=[fnd.SetSignal, fnd.SetCheck, fnd.SetValues, fnd.SetInterval],
                                         noinputs=[],
                                         output=fnd.GetSampleIndices)

