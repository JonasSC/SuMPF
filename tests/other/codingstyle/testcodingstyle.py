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

import sumpf

from .basetestcase import BaseCodingStyleTestCase
from .helper import ForEachFile, ProcessContent, SplitLines, ExpectFailure
from .checks import CheckNewlinesBeforeClasses


class TestTestCodingStyle(BaseCodingStyleTestCase):
    """
    Some coding style tests are rather complex, so these tests can be tested here.
    """

    def test_newline_before_classes(self):
        """
        Tests test_newline_before_classes.
        """
        testfile_dir = os.path.join(sumpf.config.get("test_dir"), "codingstyle", "testfiles", "CheckNewlinesBeforeClasses")
        function = ForEachFile(WithEnding="pass", Do=ProcessContent(With=SplitLines(For=CheckNewlinesBeforeClasses)))
        self.EvaluateResult(function(testfile_dir))
        function = ForEachFile(WithEnding="fail", Do=ProcessContent(With=SplitLines(For=ExpectFailure(In=CheckNewlinesBeforeClasses))))
        self.EvaluateResult(function(testfile_dir))

