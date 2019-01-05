# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2019 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""Tests for infrastructure tasks such as licensing, documentation etc."""

import os
import re
import pytest
import sumpf
import tests


def test_license():
    """Tests if all source files have the correct license header"""
    header = ("# This file is a part of the \"SuMPF\" package\n",
              "# Copyright (C) 2018-2019 Jonas Schulte-Coerne\n",
              "#\n",
              "# This program is free software: you can redistribute it and/or modify it under\n",
              "# the terms of the GNU Lesser General Public License as published by the Free\n",
              "# Software Foundation, either version 3 of the License, or (at your option) any\n",
              "# later version.\n",
              "#\n",
              "# This program is distributed in the hope that it will be useful, but WITHOUT\n",
              "# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS\n",
              "# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more\n",
              "# details.\n",
              "#\n",
              "# You should have received a copy of the GNU Lesser General Public License along\n",
              "# with this program. If not, see <http://www.gnu.org/licenses/>.\n")
    for directory in (os.path.split(sumpf.__file__)[0],
                      os.path.split(tests.__file__)[0]):
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.lower().endswith(".py"):
                    path = os.path.join(dirpath, filename)
                    with open(path) as f:
                        line = f.readline()
                        if line == "":
                            continue    # an empty file does not need a license header
                        else:
                            for h in header:
                                if line != h:
                                    pytest.fail(msg=f"{path} is missing the license header", pytrace=False)
                                line = f.readline()


def test_api_documentation():
    """Tests if all classes, that are provided by *SuMPF*, are included in the
    *Sphinx* documentation.
    """
    # get all documented classes
    documentation = os.path.join("documentation", "reference")
    if not os.path.isdir(documentation):
        pytest.skip("The source code for the documentation cannot be found.")
    mask = re.compile(r"\s*\.\. autoclass:: *sumpf.(\w*)")
    documented = set()
    for directory, _, files in os.walk(documentation):
        for filename in files:
            if os.path.splitext(filename)[-1] == ".rst":
                with open(os.path.join(directory, filename)) as f:
                    for l in f:
                        match = mask.match(l)
                        if match:
                            documented.add(match.group(1))
    # get all provided classes
    classes = set(c for c in dir(sumpf) if not c.startswith("_"))
    # compare the provided and documented classes
    assert classes.issubset(documented)
