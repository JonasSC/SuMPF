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


class TestSignalMinimum(unittest.TestCase):
    """
    A TestCase for the SignalMinimum module.
    """
    def test_find(self):
        """
        Tests the functionality of the SignalMaximum class.
        """
        signal = sumpf.Signal(channels=((0.0, 1.0, -1.0), (-4.0, -2.0, 34.0)), samplingrate=9.0, labels=("Tom", "Hank"))
        smn = sumpf.modules.SignalMinimum()
        # test the default parameters
        self.assertEqual(smn.GetMinima(), (0.0,))
        self.assertEqual(smn.GetGlobalMinimum(), 0.0)
        # test the finding of a maximum
        smn.SetSignal(signal)
        self.assertEqual(smn.GetMinima(), (-1.0, -4.0))
        self.assertEqual(smn.GetGlobalMinimum(), -4.0)
        # test passing a signal to the constructor
        self.assertEqual(sumpf.modules.SignalMinimum(signal).GetMinima(), smn.GetMinima())
        self.assertEqual(sumpf.modules.SignalMinimum(signal).GetGlobalMinimum(), smn.GetGlobalMinimum())

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        smn = sumpf.modules.SignalMinimum()
        self.assertEqual(smn.SetSignal.GetType(), sumpf.Signal)
        self.assertEqual(smn.GetMinima.GetType(), tuple)
        self.assertEqual(smn.GetGlobalMinimum.GetType(), float)
        common.test_connection_observers(testcase=self,
                                         inputs=[smn.SetSignal],
                                         noinputs=[],
                                         output=smn.GetMinima)
        common.test_connection_observers(testcase=self,
                                         inputs=[smn.SetSignal],
                                         noinputs=[],
                                         output=smn.GetGlobalMinimum)

