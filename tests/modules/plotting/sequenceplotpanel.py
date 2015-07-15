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
import _common as common
from .basetestcase import BaseTestCase


@unittest.skipUnless(sumpf.config.get("run_interactive_tests"), "Tests that require input from the user are skipped.")
@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestSequencePlotPanel(BaseTestCase):
    """
    An interactive TestCase for the SequencePlotPanel module.
    """
    def test_interactively(self):
        # setup a SequencePlotPanel in a TestQuestionnaire
        questionnaire = common.TestQuestionnaire(title="Testing SequencePlotPanel class")
        plot = sumpf.modules.SequencePlotPanel(parent=questionnaire)
        questionnaire.SetMainElement(plot)
        questionnaire.Show()
        # run the tests
        try:
            questionnaire.AssertNo(question="Is there shown anything in the plot area at all?", testcase=self)
            plot.SetSequence((1.0, 2.0, 3.0, 4.5))
            questionnaire.AssertYes(question="Does the plot show an ascending line in the x-interval between 0.0 and 3.0?", testcase=self)
            plot.SetXResolution(2.0)
            questionnaire.AssertYes(question="Does the x-interval of the lines range from 0.0 to 6.0 now?", testcase=self)
            plot.SetSequence(((0.0, 1.0, 2.0, 3.0), (2.0, 1.5, 1.0, 0.5)))
            questionnaire.AssertYes(question="Does the plot show two crossing lines now?", testcase=self)
            plot.SetXInterval((0.0, 5.0))
            questionnaire.AssertYes(question="Does the shown x-interval range from 0.0 to 5.0 now?", testcase=self)
            plot.LogarithmicY()
            plot.LogarithmicX()
            plot.ShowFullGrid()
            questionnaire.AssertYes(question="Are both axes now log scaled?", testcase=self)
        finally:
            questionnaire.Close()

