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

import os
import unittest
import sumpf


class TestNormalizePath(unittest.TestCase):
    """
    A TestCase for the helper function for normalizing paths.
    """
    def test_normalize_path(self):
        tests = {}
        if os.name in ["nt", "ce", "os2"]:
            # perform a slightly different test for operating systems that use device letters
            tests[os.path.join(os.sep, "a", "b", "c")] = os.path.join("C:", os.sep, "a", "b", "c")
            tests[os.path.join(os.sep, "a", "b", "c", "")] = os.path.join("C:", os.sep, "a", "b", "c")
        else:
            tests[os.path.join(os.sep, "a", "b", "c")] = os.path.join(os.sep, "a", "b", "c")
            tests[os.path.join(os.sep, "a", "b", "c", "")] = os.path.join(os.sep, "a", "b", "c")
        tests[os.path.join("a", "b", "c")] = os.path.join(os.getcwd(), "a", "b", "c")
        tests[os.path.join("    a", "b", "c ")] = os.path.join(os.getcwd(), "a", "b", "c")
        tests[os.path.join("~", "a", "b", "c")] = os.path.join(os.path.expanduser("~"), "a", "b", "c")
        for t in tests:
            self.assertEqual(sumpf.helper.normalize_path(t), tests[t])

