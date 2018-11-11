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

import os
import re
import unittest
import sumpf


class TestAttributes(unittest.TestCase):
    """
    Tests if certain attributes of SuMPF or its classes are set correctly.
    """
    def test_licence_variable(self):
        """
        Tests if SuMPF has the license-attribute.
        """
        self.assertTrue(hasattr(sumpf, "license"))
        self.assertEqual(sumpf.license.split("\n")[0], "                   GNU GENERAL PUBLIC LICENSE")
        self.assertEqual(sumpf.license.split("\n")[1], "                       Version 3, 29 June 2007")
        self.assertEqual(len(sumpf.license), 35145)

    def test_class_documentation(self):
        """
        Tests if every class is sufficiently documented
        """
        def format_name(classpath, classname):
            return ".".join([m.__name__ for m in classpath] + [classname])
        fails = []
        short_is_enough = ["DelayFilterGenerator", "FilterGenerator",
                           "AverageSpectrums", "ConjugateSpectrum",
                           "RelabelSignal", "RelabelSpectrum",
                           "ClipSignal", "LogarithmSignal",
                           "SignalMean", "SpectrumMean",
                           "SignalVariance", "SpectrumVariance",
                           "SweepFunction"]
        undocumented = ["SpectrumAsSignal", "SignalMinimumChannel", "SpectrumMinimumChannel",
                        "SpectrumMaximumChannel", "SignalMaximumChannel"]
        for p, m, c, f, v in sumpf.helper.walk_module(sumpf):
            for cls in c:
                if cls.__doc__ is None:
                    if cls.__name__ not in undocumented:
                        fails.append(format_name(classpath=p, classname=cls.__name__))
                else:
                    doclines = len(cls.__doc__.strip().split("\n"))
                    if cls.__name__ in short_is_enough:
                        if doclines < 1:
                            fails.append(format_name(classpath=p, classname=cls.__name__))
                        elif doclines >= 3:
                            self.fail("The class " + cls.__name__ + " is properly documented and should not be in the short_is_enough list.")
                    elif cls.__name__ in undocumented:
                        pass
                    elif doclines < 3:
                        fails.append(format_name(classpath=p, classname=cls.__name__))
        if fails != []:
            self.fail("The following " + str(len(fails)) + " classes are not sufficiently documented: " + str(fails))

    def test_no_output_call_in_constructor(self):
        """
        Tests, that no methods, that have been decorates as OutputConnectors are
        called from within their class's constructor.
        This is just a simple test, that checks for direct calls of the connector
        in the constructor. It does not check, if the constructor calls a method,
        which calls the connector, which is of course also forbidden.
        """
        # precompile regular expressions
        re_indentation = re.compile("(\s*)")
        re_class = re.compile("(\s*)(class)\s+([a-zA-Z_]+\w*)")
        re_call = re.compile("(\s+self.)(\w+)(\()")
        re_constructor = re.compile("(\s*)(def\s+__init__)(\(\s*self)")
        re_method = re.compile("(\s+def\s+)(\w+)(\(\s*self)")
        re_output = re.compile("\s*\@sumpf.Output\(")
        # search for Output connectors, that are called from within a constructor
        for path in sumpf.config.get("source_dirs"):
            for root, dirs, files in os.walk(path):
                for filename in files:
                    if filename.endswith(".py"):
                        with open(os.path.join(root, filename)) as f:
                            in_constructor = False
                            is_output = False
                            constructor_indentation = 0
                            class_incm = [] # a list of tuples (indentation, class name, connector methods, methods that are called in the constructor)
                            for line in f:
                                indentation = len(re_indentation.match(line).groups()[0])
                                if indentation < constructor_indentation:
                                    in_constructor = False
                                while class_incm != [] and indentation < class_incm[-1][0]:
                                    class_incm.pop()
                                class_match = re_class.match(line)
                                if class_match:
                                    groups = class_match.groups()
                                    class_incm.append((len(groups[0]), groups[2], [], []))
                                if in_constructor:
                                    call_match = re_call.search(line)
                                    if call_match:
                                        method_name = call_match.groups()[1]
                                        if method_name in class_incm[-1][2]:
                                            self.fail("The OutputConnector method %s is called from the constructor of class %s" % (method_name, class_incm[-1][1]))
                                        else:
                                            class_incm[-1][3].append(method_name)
                                if class_incm != []:
                                    constructor_match = re_constructor.match(line)
                                    if constructor_match:
                                        constructor_indentation = len(constructor_match.groups()[0])
                                        in_constructor = True
                                    else:
                                        method_match = re_method.match(line)
                                        if method_match:
                                            if is_output:
                                                method_name = method_match.groups()[1]
                                                if method_name in class_incm[-1][3]:
                                                    self.fail("The OutputConnector method %s is called from the constructor of class %s" % (method_name, class_incm[-1][1]))
                                                else:
                                                    class_incm[-1][2].append(method_name)
                                            is_output = False
                                output_match = re_output.match(line)
                                if output_match:
                                    is_output = True

