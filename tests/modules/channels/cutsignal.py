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


class TestCutSignal(unittest.TestCase):
    """
    A test case for the CutSignal module.
    """
    def test_function(self):
        """
        Tests the function of the CutSignal module.
        """
        signal = sumpf.Signal(channels=((1.0, 2.0, 3.0, 4.0, 5.0), (6.0, 7.0, 8.0, 9.0, 0.0)), samplingrate=12.0, labels=("1", None))
        cut = sumpf.modules.CutSignal()
        self.assertEqual(cut.GetOutput(), sumpf.Signal())
        self.assertEqual(cut.GetOutputLength(), len(cut.GetOutput()))
        cut = sumpf.modules.CutSignal(signal=signal, start=2, stop=(-1))
        self.assertEqual(cut.GetOutput(), signal[2:-1])
        self.assertEqual(cut.GetOutputLength(), len(cut.GetOutput()))
        cut.SetStart(1)
        cut.SetStop(sumpf.modules.CutSignal.END)
        self.assertEqual(cut.GetOutput(), signal[1:])
        self.assertEqual(cut.GetOutputLength(), len(cut.GetOutput()))
        cut.SetStop(27)
        self.assertEqual(cut.GetOutput(), signal[1:27])
        self.assertEqual(cut.GetOutputLength(), len(cut.GetOutput()))

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        cut = sumpf.modules.CutSignal()
        self.assertEqual(cut.SetInput.GetType(), sumpf.Signal)
        self.assertEqual(cut.SetStart.GetType(), int)
        self.assertEqual(cut.SetStop.GetType(), int)
        self.assertEqual(cut.SetInterval.GetType(), tuple)
        self.assertEqual(cut.GetOutput.GetType(), sumpf.Signal)
        self.assertEqual(cut.GetOutputLength.GetType(), int)
        common.test_connection_observers(testcase=self,
                                         inputs=[cut.SetInput, cut.SetStart, cut.SetStop, cut.SetInterval],
                                         noinputs=[],
                                         output=cut.GetOutput)
        common.test_connection_observers(testcase=self,
                                         inputs=[cut.SetInput, cut.SetStart, cut.SetStop, cut.SetInterval],
                                         noinputs=[],
                                         output=cut.GetOutputLength)

