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

import re
import os


class RegEx(object):
    Class = re.compile("class\s*\w*\s*\(*\s*[\w\s,]*\s*\)*\s*:")
    Decorator = re.compile("@\w*")
    Pass = re.compile("\s+pass\W+")

    Import = re.compile("import")
    FromImport = re.compile("from[.\s\w]*import")

    Constants = re.compile("[a-zA-Z_]+\w*\s*\=\s*[\w\W]+")

    Comment = re.compile("\s*#")
    MultilineComment = re.compile("\s*\"\"\"")

    LineEndWhitespace = re.compile("[ \t\f\v]$")
    MacLineEnd = re.compile("\r")
    NewlinesAtEnd = re.compile("[\n]$")
    DoubleNewline = re.compile("\n\n")
    Indentation = re.compile("[ \t]")
    ArbitraryIndentation = re.compile("[ \t]*")

    NoneComparison = re.compile("[=!]=[ \t]*None")
    BoolComparison = re.compile("(([=!]=)|(is([ \t]*not)*)[ \t])[ \t]*((True)|(False))")

    DocstringReturn = re.compile("@return\s*:")
    DocstringRetval = re.compile("@retval\:")

    OsSep = re.compile("\+\s*os\.sep\s*\+")



class ForEachFile(object):
    def __init__(self, WithEnding=None, Do=None):
        self.__ending = WithEnding
        self.__function = Do

    def __call__(self, path):
        for root, dirs, files in os.walk(path):
            for filename in files:
                if self.__ending is not None and filename.endswith("." + self.__ending):
                    result = self.__function(os.path.join(root, filename))
                    if result is not None:
                        location = "File \"" + os.path.join(root, filename) + "\""
                        if result[1] != "":
                            location += " " + result[1]
                        return result[0], location
        return None



class ProcessContent(object):
    def __init__(self, With):
        self.__function = With

    def __call__(self, path):
        with open(path, 'r') as f:
            content = f.read()
            result = self.__function(content)
        return result



class SplitLines(object):
    def __init__(self, For):
        self.__function = For

    def __call__(self, text):
        lines = text.split("\n")
        return self.__function(lines)



class IterateOverLines(object):
    def __init__(self, AndDo):
        self.__function = AndDo

    def __call__(self, lines):
        for i in range(len(lines)):
            result = self.__function(lines[i])
            if result is not None:
                location = "line " + str(i + 1)
                if result[1] != "":
                    location += " " + result[1]
                return result[0], location
        return None



class StripComments(object):
    def __init__(self, And):
        self.__function = And
        self.__in_comment = False

    def __call__(self, line):
        splits = line.split('"""')
        l = ""
        for s in splits:
            if not self.__in_comment:
                l += s
            self.__in_comment = not self.__in_comment
        self.__in_comment = not self.__in_comment
        l = l.split("#")[0]
        if l == "":
            return None
        else:
            return self.__function(l)



class ExpectFailure(object):
    def __init__(self, In):
        self.__function = In

    def __call__(self, *args):
        result = self.__function(*args)
        if result is None:
            return "Expected a failure", ""
        else:
            return None

