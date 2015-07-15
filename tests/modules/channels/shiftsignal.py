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


class TestShiftSignal(unittest.TestCase):
    """
    A test case for the ShiftSignal module.
    """
    def test_function(self):
        """
        Tests the function of the CutSignal module.
        """
        signal = sumpf.Signal(channels=((1.0, 2.0, 3.0, 4.0, 5.0), (6.0, 7.0, 8.0, 9.0, 0.0)), samplingrate=12.0, labels=("1", None))
        shifted1 = sumpf.Signal(channels=((4.0, 5.0, 1.0, 2.0, 3.0), (9.0, 0.0, 6.0, 7.0, 8.0)), samplingrate=12.0, labels=("1", None))
        shifted2 = sumpf.Signal(channels=((2.0, 3.0, 4.0, 5.0, 1.0), (7.0, 8.0, 9.0, 0.0, 6.0)), samplingrate=12.0, labels=("1", None))
        shifted3 = sumpf.Signal(channels=((0.0, 0.0, 1.0, 2.0, 3.0), (0.0, 0.0, 6.0, 7.0, 8.0)), samplingrate=12.0, labels=("1", None))
        shifted4 = sumpf.Signal(channels=((2.0, 3.0, 4.0, 5.0, 0.0), (7.0, 8.0, 9.0, 0.0, 0.0)), samplingrate=12.0, labels=("1", None))
        shift = sumpf.modules.ShiftSignal()
        self.assertEqual(shift.GetOutput(), sumpf.Signal())
        shift.SetInput(signal)
        self.assertEqual(shift.GetOutput(), signal)
        shift.SetShift(2)
        self.assertEqual(shift.GetOutput(), shifted1)
        shift = sumpf.modules.ShiftSignal(signal=signal, shift=2, circular=False)
        self.assertEqual(shift.GetOutput(), shifted3)
        shift.SetShift(-1)
        self.assertEqual(shift.GetOutput(), shifted4)
        shift.SetCircular(True)
        self.assertEqual(shift.GetOutput(), shifted2)


    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        cut = sumpf.modules.ShiftSignal()
        self.assertEqual(cut.SetInput.GetType(), sumpf.Signal)
        self.assertEqual(cut.SetShift.GetType(), int)
        self.assertEqual(cut.SetCircular.GetType(), bool)
        self.assertEqual(cut.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[cut.SetInput, cut.SetShift, cut.SetCircular],
                                         noinputs=[],
                                         output=cut.GetOutput)

