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


class TestRectifySignal(unittest.TestCase):
    """
    A test case for the RectifySignal module.
    """
    def test_calculation(self):
        """
        Tests if the result is calculated correctly.
        """
        signal = sumpf.Signal(channels=((1.0, -4.0, 5.0), (-10.0, 100.0, -512.0)), samplingrate=42.0, labels=(None, "3"))
        result = sumpf.Signal(channels=((1.0, 4.0, 5.0), (10.0, 100.0, 512.0)), samplingrate=42.0, labels=(None, "3"))
        rec = sumpf.modules.RectifySignal()
        self.assertEqual(rec.GetOutput(), sumpf.Signal())
        rec.SetInput(signal)
        self.assertEqual(rec.GetOutput(), result)
        rec = sumpf.modules.RectifySignal(signal=signal)
        self.assertEqual(rec.GetOutput(), result)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        rec = sumpf.modules.RectifySignal()
        self.assertEqual(rec.SetInput.GetType(), sumpf.Signal)
        self.assertEqual(rec.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[rec.SetInput],
                                         noinputs=[],
                                         output=rec.GetOutput)

