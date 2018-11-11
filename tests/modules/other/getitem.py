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

import collections
import unittest
import sumpf
import _common as common


class TestGetItem(unittest.TestCase):
    """
    A TestCase for the GetItem module.
    """
    def test_function(self):
        """
        Tests standard functionality of the module.
        """
        # test the constructor defaults
        get = sumpf.modules.GetItem()
        self.assertIsNone(get.GetItem())
        # test a tuple a list and a string
        sequences = ([1, 2, 3, 4, 5], (6.0, 7.0, 8.0), "abcdefg")
        for s in sequences:
            get = sumpf.modules.GetItem()
            get.SetContainer(s)
            for i, r in enumerate(s):
                get.SetKey(i)
                self.assertEqual(get.GetItem(), r)
        # test a dict
        d = {"a": 1, 9: 4.0, 7.2: "b"}
        for k in d:
            self.assertEqual(sumpf.modules.GetItem(container=d, key=k).GetItem(), d[k])

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        get = sumpf.modules.GetItem()
        self.assertEqual(get.SetContainer.GetType(), (collections.Sequence, collections.Mapping))
        self.assertEqual(get.SetKey.GetType(), None)
        self.assertEqual(get.GetItem.GetType(), None)
        common.test_connection_observers(testcase=self,
                                         inputs=[get.SetKey, get.SetContainer],
                                         noinputs=[],
                                         output=get.GetItem)

