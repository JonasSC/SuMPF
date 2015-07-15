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


class TestStringFunctions(unittest.TestCase):
    """
    A TestCase for the helper functions in the stringfunctions.py file.
    """
    def test_counting_number(self):
        pairs = [(1, "1st"),
                 (2, "2nd"),
                 (3, "3rd"),
                 (4, "4th"),
                 (10, "10th"),
                 (11, "11th"),
                 (12, "12th"),
                 (13, "13th"),
                 (31, "31st"),
                 (43, "43rd"),
                 (101, "101st"),
                 (213, "213th"),
                 (323, "323rd")]
        for p in pairs:
            self.assertEqual(sumpf.helper.counting_number(p[0]), p[1])

    def test_leading_zeros(self):
        self.assertEqual(sumpf.helper.leading_zeros(number=5, maximum=1), "5")
        self.assertEqual(sumpf.helper.leading_zeros(number=3790, maximum=43e6), "00003790")
        self.assertEqual(sumpf.helper.leading_zeros(number=90, maximum=3), "90")

