# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2016 Jonas Schulte-Coerne
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

import sys
import unittest
import sumpf
import _common as common

if sys.version_info.major == 2:
    import types
    NoneType = types.NoneType
else:
    NoneType = type(None)


@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestCreateInterval(unittest.TestCase):
    """
    A TestCase for the CreateInterval module.
    """
    def test_intervals(self):
        """
        Tests if the intercals are generated as expected
        """
        # test the defaults
        ci = sumpf.modules.CreateInterval()
        self.assertEqual(ci.GetInterval(), (0, -1))
        # test the setter and getter
        ci.SetStop(12)
        self.assertEqual(ci.GetInterval(), (0, 12))
        ci.SetNegativeStop(True)
        self.assertEqual(ci.GetInterval(), (0, -12))
        ci.SetStop(None)
        self.assertEqual(ci.GetInterval(), (0, None))
        ci.SetStart(9.1)
        self.assertEqual(ci.GetInterval(), (9.1, None))
        ci.SetNegativeStart(True)
        self.assertEqual(ci.GetInterval(), (-9.1, None))
        ci.SetStop(3.4)
        self.assertEqual(ci.GetInterval(), (-9.1, -3.4))
        # test the constructor arguments
        self.assertEqual(sumpf.modules.CreateInterval(start=2.9, stop=-14.8, negative_stop=True).GetInterval(), (2.9, 14.8))
        self.assertEqual(sumpf.modules.CreateInterval(start=-5.7, stop=13, negative_start=True).GetInterval(), (5.7, 13))

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        ci = sumpf.modules.CreateInterval()
        self.assertEqual(ci.SetStart.GetType(), (int, float))
        self.assertEqual(ci.SetStop.GetType(), (int, float, NoneType))
        self.assertEqual(ci.SetNegativeStart.GetType(), bool)
        self.assertEqual(ci.SetNegativeStop.GetType(), bool)
        self.assertEqual(ci.GetInterval.GetType(), tuple)
        common.test_connection_observers(testcase=self,
                                         inputs=[ci.SetStart, ci.SetStop, ci.SetNegativeStart, ci.SetNegativeStop],
                                         noinputs=[],
                                         output=ci.GetInterval)

