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

from .helper import RegEx

def CheckWhitespaceAtLineEnd(line):
    if RegEx.LineEndWhitespace.search(line):
        return "whitespace at lineend", ""

def CheckNewlineAtFileend(text):
    text = text[0:-1]
    if text != "":
        match = RegEx.NewlinesAtEnd.search(text)
        if match is None:
            return "No newline at end of file", ""
        elif match.start() < len(text) - 1:
            return "More than one newline at end of file", ""

def CheckNewlinesBeforeClasses(lines):
    for i in range(1, len(lines)):
        if RegEx.Class.match(lines[i]):
            blank_lines = 0
            for l in range(i - 1, -1, -1):
                if lines[l] == "":
                    blank_lines += 1
                if blank_lines == i:
                    if blank_lines != 0:
                        return "wrong number of blank lines (expected none, got " + str(blank_lines) + ") before class definition at beginning of file", "line " + str(i + 1)
                if RegEx.Import.match(lines[l]) or \
                   RegEx.FromImport.match(lines[l]) or \
                   RegEx.Constants.match(lines[l]) or \
                   RegEx.Comment.match(lines[l]) or \
                   RegEx.MultilineComment.match(lines[l]):
                    if RegEx.DoubleNewline.search("\n".join(lines[0:l + 1])):
                        if blank_lines != 2:
                            return "wrong number of blank lines (expected 2, got " + str(blank_lines) + ") after multiple blocks of imports", "line " + str(i + 1)
                    elif blank_lines != 1:
                        return "wrong number of blank lines (expected 1, got " + str(blank_lines) + ") after single block of imports", "line " + str(i + 1)
                    break
                elif RegEx.Indentation.match(lines[l]):
                    if blank_lines != 3:
                        return "wrong number of blank lines (expected 3, got " + str(blank_lines) + ") after method or class definition", "line " + str(i + 1)
                    break
                elif RegEx.Decorator.match(lines[l]):
                    pass
                elif lines[l] == "":
                    pass    # Blank lines have already been counted on top of loop body
                else:
                    return "Got unexpected code", "line " + str(i + 1)

def CheckLineEndStyle(path):
    f = open(path, 'rb')
    content = f.read()
    f.close()
    if RegEx.MacLineEnd.search(content):
        return "Incorrect line end style", ""

def CheckNoneComparison(line):
    if RegEx.NoneComparison.search(line.split("#")[0]):
        return "equality operator for comparison with None", ""

def CheckBoolComparison(line):
    if RegEx.BoolComparison.search(line.split("#")[0]):
        return "comparison with a boolean value", ""

def CheckWrongDocstringKeywords(text):
    keywords = {}
    keywords[RegEx.DocstringReturn] = "wrong docstring keyword '@return'"
    keywords[RegEx.DocstringRetval] = "no whitespace after '@retval'-documentation-command"
    start = len(text) - 1
    match = None
    message = ""
    for k in keywords:
        s = k.search(text)
        if s:
            if s.span()[1] < start:
                match = s
                start = match.span()[1]
                message = keywords[k]
    while match:
        if len(RegEx.MultilineComment.findall(text[0:match.span()[0]])) % 2 == 1:
            if len(RegEx.MultilineComment.findall(text[start:])) % 2 == 1:
                return message, ""
        first = len(text) - 1
        for k in keywords:
            s = k.search(text[start:])
            if s:
                if s.span()[1] < first:
                    match = s
                    first = match.span()[1]
                    message = keywords[k]
        start = first

def CheckPassUsage(lines):
    for i in range(1, len(lines)):
        if RegEx.Pass.match(lines[i]):
            comment = False
            for l in range(i - 1, -1, -1):
                if RegEx.MultilineComment.match(lines[l]):
                    comment = not comment
                elif not comment:
                    if lines[l] == "\n":
                        return "blank line before pass", "line " + str(l + 1)
                    elif len(RegEx.ArbitraryIndentation.match(lines[l]).group()) < len(RegEx.ArbitraryIndentation.match(lines[i]).group()):
                        break
                    elif not RegEx.Comment.match(lines[l]):
                        return "unnecessary use of pass", "line " + str(i + 1)

def CheckOsSepUsage(line):
    if RegEx.OsSep.search(line):
        return "string concatenation with os.sep", ""

def CheckLicense(lines):
    license = []
    license.append("# SuMPF - Sound using a Monkeyforest-like processing framework")
    license.append("# Copyright (C) 2012-2015 Jonas Schulte-Coerne")
    license.append("#")
    license.append("# This program is free software: you can redistribute it and/or modify")
    license.append("# it under the terms of the GNU General Public License as published by")
    license.append("# the Free Software Foundation, either version 3 of the License, or")
    license.append("# (at your option) any later version.")
    license.append("#")
    license.append("# This program is distributed in the hope that it will be useful,")
    license.append("# but WITHOUT ANY WARRANTY; without even the implied warranty of")
    license.append("# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the")
    license.append("# GNU General Public License for more details.")
    license.append("#")
    license.append("# You should have received a copy of the GNU General Public License")
    license.append("# along with this program. If not, see <http://www.gnu.org/licenses/>.")
    start = 0
    if len(lines) >= 2:
        if lines[0].strip() == "#!/usr/bin/env python":
            if lines[1].strip() == "":
                start = 2
    i = 0
    for l in range(start, len(lines)):
        if i == len(license):
            return
        elif lines[l].strip() != license[i]:
            return "the license header is missing", ""
        else:
            i += 1

