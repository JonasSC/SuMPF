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


class TestSignalMaximum(unittest.TestCase):
    """
    A TestCase for the SignalMaximum class.
    """
    def test_find(self):
        """
        Tests the functionality of the SignalMaximum class.
        """
        signal = sumpf.Signal(channels=((0.0, 1.0, -1.0), (-4.0, -2.0, 34.0)), samplingrate=9.0, labels=("Tom", "Hank"))
        smx = sumpf.modules.SignalMaximum()
        # test the default parameters
        self.assertEqual(smx.GetMaxima(), (0.0,))
        self.assertEqual(smx.GetGlobalMaximum(), 0.0)
        # test the finding of a maximum
        smx.SetSignal(signal)
        self.assertEqual(smx.GetMaxima(), (1.0, 34.0))
        self.assertEqual(smx.GetGlobalMaximum(), 34.0)
        # test passing a signal to the constructor
        self.assertEqual(sumpf.modules.SignalMaximum(signal).GetMaxima(), smx.GetMaxima())
        self.assertEqual(sumpf.modules.SignalMaximum(signal).GetGlobalMaximum(), smx.GetGlobalMaximum())

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        smx = sumpf.modules.SignalMaximum()
        self.assertEqual(smx.SetSignal.GetType(), sumpf.Signal)
        self.assertEqual(smx.GetMaxima.GetType(), tuple)
        self.assertEqual(smx.GetGlobalMaximum.GetType(), float)
        common.test_connection_observers(testcase=self,
                                         inputs=[smx.SetSignal],
                                         noinputs=[],
                                         output=smx.GetMaxima)
        common.test_connection_observers(testcase=self,
                                         inputs=[smx.SetSignal],
                                         noinputs=[],
                                         output=smx.GetGlobalMaximum)

