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

import sumpf

from .basetestcase import BaseCodingStyleTestCase
from .checks import CheckWhitespaceAtLineEnd, CheckNewlineAtFileend, CheckNewlinesBeforeClasses, \
                    CheckLineEndStyle, CheckNoneComparison, CheckBoolComparison, \
                    CheckWrongDocstringKeywords, CheckPassUsage, CheckOsSepUsage, \
                    CheckLicense
from .helper import ForEachFile, ProcessContent, SplitLines, IterateOverLines, StripComments


class TestCodingStyle(BaseCodingStyleTestCase):
    """
    Automatic testing for some common coding style issues
    """

    def test_whitespaces_at_lineend(self):
        """
        Tests for whitespace characters at line endings.
        Fails if there are lines with whitespaces at their end.
        """
        function = ForEachFile(WithEnding="py", Do=ProcessContent(With=SplitLines(For=IterateOverLines(AndDo=CheckWhitespaceAtLineEnd))))
        for d in sumpf.config.get("source_dirs"):
            self.EvaluateResult(function(d))

    def test_newline_at_fileend(self):
        """
        Tests if there is exactly one newline at the end of a file. Ignores empty files.
        Fails if there is no newline at the end or if there are more than one.
        """
        function = ForEachFile(WithEnding="py", Do=ProcessContent(With=CheckNewlineAtFileend))
        for d in sumpf.config.get("source_dirs"):
            self.EvaluateResult(function(d))

    def test_newline_before_classes(self):
        """
        Tests if there is the right number of blank lines before a class definition.
        Fails if the number of blank lines is not correct.
        The correct numbers are:
            no blank line if the class begins at the first line of the file
            1 blank line if the class begins after one block of imports or comments (no blank line between imports and/or comments)
            2 blank lines if the class begins after multiple blocks of imports or comments
            3 blank lines if the class begins after a method or a class definition
        """
        function = ForEachFile(WithEnding="py", Do=ProcessContent(With=SplitLines(For=CheckNewlinesBeforeClasses)))
        for d in sumpf.config.get("source_dirs"):
            self.EvaluateResult(function(d))

    def test_lineend_type(self):
        """
        Tests if line endings of another type than the unix one are present.
        Fails if other line end types are found.
        """
        function = ForEachFile(Do=CheckLineEndStyle)
        for d in sumpf.config.get("source_dirs"):
            self.EvaluateResult(function(d))

    def test_none_comparison(self):
        """
        Tests if comparisons with None are done with equality operators.
        Fails if such a comparison is found.
        It is recommended to use "is" or "is not" for comparisons with None.
        """
        function = ForEachFile(WithEnding="py", Do=ProcessContent(With=SplitLines(For=IterateOverLines(AndDo=CheckNoneComparison))))
        for d in sumpf.config.get("source_dirs"):
            self.EvaluateResult(function(d))

    def test_bool_comparison(self):
        """
        Tests if comparisons with boolean values are done.
        Fails if such a comparison is found.
        It is recommended to use something like "if value:" instead of comparisons.
        """
        function = ForEachFile(WithEnding="py", Do=ProcessContent(With=SplitLines(For=IterateOverLines(AndDo=StripComments(And=CheckBoolComparison)))))
        for d in sumpf.config.get("source_dirs"):
            self.EvaluateResult(function(d))

    def test_wrong_docstring_keywords(self):
        """
        Tests for commonly mistaken keywords in docstrings.
        Fails if a wrong keyword is found.
          - instead of "@return" "@retval" should be used, because Doxygen likes it that way
          - after "@retval" should be a whitespace
        """
        function = ForEachFile(WithEnding="py", Do=ProcessContent(With=CheckWrongDocstringKeywords))
        for d in sumpf.config.get("source_dirs"):
            self.EvaluateResult(function(d))

    def test_pass_usage(self):
        """
        Tests for unnecessary use of "pass".
        Fails if such a unnecessary use of pass is found.
        """
        function = ForEachFile(WithEnding="py", Do=ProcessContent(With=SplitLines(For=CheckPassUsage)))
        for d in sumpf.config.get("source_dirs"):
            self.EvaluateResult(function(d))

    def test_path_concatenation(self):
        """
        Tests if paths are created by the concatenation of strings and os.sep
        Fails if such a concatenation is found.
        It is recommended to use os.path.join as it is faster and often better readable
        """
        function = ForEachFile(WithEnding="py", Do=ProcessContent(With=SplitLines(For=IterateOverLines(AndDo=CheckOsSepUsage))))
        for d in sumpf.config.get("source_dirs"):
            self.EvaluateResult(function(d))

    def test_license_header(self):
        """
        Tests if every code file starts with the license header for the GPLv3.
        """
        function = ForEachFile(WithEnding="py", Do=ProcessContent(With=SplitLines(For=CheckLicense)))
        for d in sumpf.config.get("source_dirs"):
            self.EvaluateResult(function(d))

