#!/usr/bin/env python

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

"""
This is a small helper script to reduce the effort of updating the license headers,
when a new year has started.
There is a unit test that checks, if all files have a correct license header. This
unit test is not updated automatically by this test. The code that has to be updated
is found in the function "CheckLicense" in the file "tests/other/codingstyle/checks.py"
"""

import os

path = "../"

for root, dirs, files in os.walk(path):
    for filename in files:
        if filename.endswith(".py"):
            lines = None
            with open(os.path.join(root, filename), "r") as f:
                lines = list(f.readlines())
            for i in range(len(lines)):
                if lines[i] == "# Copyright (C) 2012-2014 Jonas Schulte-Coerne\n":  # this is the original content that shall be replaced (do not forget the \n at the line endings)
                    lines[i] = "# Copyright (C) 2012-2015 Jonas Schulte-Coerne\n"   # this is the new content (do not forget the \n at the line endings)
            with open(os.path.join(root, filename), "w") as f:
                f.write("".join(lines))

