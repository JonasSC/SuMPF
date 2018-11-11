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


@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestCreateSampleInterval(unittest.TestCase):
    """
    A TestCase for the CreateSampleInterval module.
    """
    def test_intervals(self):
        """
        Tests if the intercals are generated as expected
        """
        # test the defaults
        ci = sumpf.modules.CreateSampleInterval()
        self.assertEqual(ci.GetInterval(), sumpf.SampleInterval(0, 1.0))
        # test the setter and getter
        ci.SetStop(12)
        self.assertEqual(ci.GetInterval(), sumpf.SampleInterval(0, 12))
        ci.SetNegativeStop(True)
        self.assertEqual(ci.GetInterval(), sumpf.SampleInterval(0, -12))
        ci.SetStop(1.0)
        self.assertEqual(ci.GetInterval(), sumpf.SampleInterval(0, -1.0))
        ci.SetStart(8)
        self.assertEqual(ci.GetInterval(), sumpf.SampleInterval(8, -1.0))
        # test the constructor arguments
        self.assertEqual(sumpf.modules.CreateSampleInterval(start=2.9, stop=-14.8, negative_stop=True).GetInterval(), sumpf.SampleInterval(2.9, 14.8))
        self.assertEqual(sumpf.modules.CreateSampleInterval(start=-5.7, stop=13, negative_start=True).GetInterval(), sumpf.SampleInterval(5.7, 13))

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        ci = sumpf.modules.CreateSampleInterval()
        self.assertEqual(ci.SetStart.GetType(), (int, float))
        self.assertEqual(ci.SetStop.GetType(), (int, float))
        self.assertEqual(ci.SetNegativeStart.GetType(), bool)
        self.assertEqual(ci.SetNegativeStop.GetType(), bool)
        self.assertEqual(ci.GetInterval.GetType(), sumpf.SampleInterval)
        common.test_connection_observers(testcase=self,
                                         inputs=[ci.SetStart, ci.SetStop, ci.SetNegativeStart, ci.SetNegativeStop],
                                         noinputs=[],
                                         output=ci.GetInterval)

