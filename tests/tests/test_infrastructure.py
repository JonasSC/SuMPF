# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2021 Jonas Schulte-Coerne
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

import collections.abc
import enum
import inspect
import os
import re
import pytest
import connectors
import sumpf
import tests


def test_license():
    """Tests if all source files have the correct license header"""
    header = ("# This file is a part of the \"SuMPF\" package\n",
              "# Copyright (C) 2018-2021 Jonas Schulte-Coerne\n",
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
                        for h in header:
                            if line != h:
                                pytest.fail(msg=f"{path} is missing the license header", pytrace=False)
                            line = f.readline()


def test_sphinx_documentation():    # noqa: C901; pylint: disable=too-many-locals,too-many-branches,too-many-statements; alright, this is complex...
    """Tests if all classes and their attributes are included in the *Sphinx* documentation."""
    # get all documented methods
    documentation = os.path.join("documentation", "reference")
    if not os.path.isdir(documentation):
        pytest.skip("The source code for the documentation cannot be found.")
    class_mask = re.compile(r"\s*\.\. autoclass:: *(sumpf\.(\w*\.)*\w*)")
    method_mask = re.compile(r"\s*\.\. automethod:: *(\w*)\(([\*\w, ]*)\)")
    attribute_mask = re.compile(r"\s*\.\. autoattribute:: *(\w*)")
    members_mask = re.compile(r"\s*:members:")
    documented_methods = {}
    documented_attributes = {}
    with_members = set()
    for directory, _, files in os.walk(documentation):
        for filename in files:
            if os.path.splitext(filename)[-1] == ".rst":
                with open(os.path.join(directory, filename)) as f:
                    current_class = None
                    for l in f:
                        class_match = class_mask.match(l)
                        if class_match:
                            current_class = class_match.group(1)
                            assert current_class not in documented_methods
                            documented_methods[current_class] = {}
                            assert current_class not in documented_attributes
                            documented_attributes[current_class] = set()
                        else:
                            members_match = members_mask.match(l)
                            if members_match:
                                if current_class is not None:
                                    with_members.add(current_class)
                            else:
                                method_match = method_mask.match(l)
                                if method_match:
                                    assert current_class is not None
                                    method = method_match.group(1)
                                    args = [a.strip().lstrip("*")
                                            for a in method_match.group(2).split(",") if a.strip() != ""]
                                    documented_methods[current_class][method] = args
                                else:
                                    attribute_match = attribute_mask.match(l)
                                    if attribute_match:
                                        assert current_class is not None
                                        documented_attributes[current_class].add(attribute_match.group(1))
    # get all implemented features
    implemented_methods = {}
    implemented_connectors = {}
    implemented_attributes = {}
    for e in dir(sumpf):    # pylint: disable=too-many-nested-blocks
        if not e.startswith("_"):
            current_class = f"sumpf.{e}"
            implemented_methods[current_class] = {}
            implemented_connectors[current_class] = set()
            implemented_attributes[current_class] = set()
            o = getattr(sumpf, e)
            for a in dir(o):
                if not a.startswith("_"):
                    m = getattr(o, a)
                    if inspect.isclass(m) and issubclass(m, enum.Enum):     # enumerations are callable, but shall not be considered as methods
                        implemented_attributes[current_class].add(a)
                    elif isinstance(m, collections.abc.Callable):
                        parameters = [p for p in inspect.signature(m).parameters if p != "self"]
                        if isinstance(m, connectors.connectors.MacroInputConnector):
                            implemented_methods[current_class][a] = parameters + ["*"]
                            implemented_connectors[current_class].add(a)
                        else:
                            implemented_methods[current_class][a] = parameters
                            if isinstance(m, (connectors.connectors.OutputConnector,
                                              connectors.connectors.OutputProxy,
                                              connectors.connectors.MultiOutputConnector,
                                              connectors.connectors.MultiOutputProxy,
                                              connectors.connectors.SingleInputConnector,
                                              connectors.connectors.SingleInputProxy,
                                              connectors.connectors.MultiInputConnector,
                                              connectors.connectors.MultiInputProxy,
                                              connectors.connectors.MultiInputAssociateProxy,
                                              connectors.connectors.MacroOutputConnector)):
                                implemented_connectors[current_class].add(a)
                    else:
                        implemented_attributes[current_class].add(a)
    # compare the implemented set of features to the documented one
    for current_class in implemented_methods:
        # test if the class is included in the documentation
        if current_class not in documented_methods or current_class not in documented_attributes:
            pytest.fail(f"The class {current_class} is not included in the Sphinx documentation", pytrace=False)
        # test if the class's documentation contains a :members:-field, which does not work with connectors
        if implemented_connectors[current_class] and current_class in with_members:
            pytest.fail(f"The class {current_class} has connectors, which do not work "
                        "with the auto-generated documentation from the :members: field.",
                        pytrace=False)
        # check if the class's attributes and methods are documented
        if current_class not in with_members:
            if implemented_attributes[current_class] != documented_attributes[current_class]:
                pytest.fail(f"The class {current_class}'s attributes are not properly"
                            f"documented: expected {implemented_attributes[current_class]}, "
                            f"found {documented_attributes[current_class]}",
                            pytrace=False)
            for method in implemented_methods[current_class]:
                if method not in documented_methods[current_class]:
                    pytest.fail(f"The method {current_class}.{method} is not included "
                                "in the Sphinx documentation",
                                pytrace=False)
                if "*" in implemented_methods[current_class][method]:
                    index = implemented_methods[current_class][method].index("*")
                    if implemented_methods[current_class][method][0:index] != documented_methods[current_class][method][0:index]:   # pylint: disable=line-too-long
                        pytest.fail(f"The parameters of method {current_class}.{method} "
                                    "are not included in the Sphinx documentation: "
                                    f"expected {implemented_methods[current_class][method]}, "
                                    f"found {documented_methods[current_class][method]}",
                                    pytrace=False)
                    if not documented_methods[current_class][method][index:]:
                        pytest.fail(f"Expected more parameters of the method "
                                    "{current_class}.{method} to be documented",
                                    pytrace=False)
                else:
                    if implemented_methods[current_class][method] != documented_methods[current_class][method]:
                        pytest.fail(f"The parameters of method {current_class}.{method} "
                                    "are not included in the Sphinx documentation: "
                                    f"expected {implemented_methods[current_class][method]}, "
                                    f"found {documented_methods[current_class][method]}",
                                    pytrace=False)
        # check if there are surplus methods or attributes in the documentation
        for method in documented_methods[current_class]:
            if method not in implemented_methods[current_class]:
                pytest.fail(f"The non-existent method {current_class}.{method} is "
                            "dispensable in the Sphinx documentation",
                            pytrace=False)
        for attribute in documented_attributes[current_class]:
            if attribute not in implemented_attributes[current_class]:
                pytest.fail(f"The non-existent attribute {current_class}.{attribute} "
                            "is dispensable in the Sphinx documentation",
                            pytrace=False)
