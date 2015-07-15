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
class TestSignalPlotPanel(BaseTestCase):
    """
    An interactive TestCase for the SignalPlotPanel module.
    """
    def test_interactively(self):
        # setup a SignalPlotPanel in a TestQuestionnaire
        questionnaire = common.TestQuestionnaire(title="Testing SignalPlotPanel class")
        plot = sumpf.modules.SignalPlotPanel(parent=questionnaire)
        questionnaire.SetMainElement(plot)
        sumpf.connect(self.copy.GetOutput, plot.SetSignal)
        questionnaire.Show()
        # run the tests
        try:
            questionnaire.AssertYes(question="Does the plot show a sweep and a triangle wave in the same plot?", testcase=self)
            self.properties.SetSamplingRate(4000.0)
            questionnaire.AssertYes(question="Does the x-axis go to 125ms now?", testcase=self)
            plot.HideLegend()
            questionnaire.AssertYes(question="Has the legend been hidden correctly? (the respective checkbox in the toolbar should be unchecked as well)", testcase=self)
            plot.HideGrid()
            questionnaire.AssertYes(question="Has the grid behind the plot lines been hidden?", testcase=self)
            plot.SetCursors([0.04, 0.08])
            questionnaire.AssertYes(question="Are there two cursors (vertical lines) in the plot now?", testcase=self)
            self.copy.SetChannelCount(1)
            questionnaire.AssertYes(question="Has the green curve disappeared? (the cursors should still be visible)", testcase=self)
            self.copy.SetChannelCount(5)
            plot.SetLayout(sumpf.modules.SignalPlotPanel.LAYOUT_HORIZONTALLY_TILED)
            questionnaire.AssertYes(question="Does the plot now show five plots in three columns and one line per plot?", testcase=self)
            sumpf.disconnect(self.copy.GetOutput, plot.SetSignal)
            self.copy.SetChannelCount(1)
            rectify = sumpf.modules.RectifySignal()
            sumpf.connect(self.copy.GetOutput, rectify.SetInput)
            shift = sumpf.modules.ShiftSignal(shift=30, circular=True)
            sumpf.connect(rectify.GetOutput, shift.SetInput)
            add = sumpf.modules.AddSignals()
            sumpf.connect(rectify.GetOutput, add.SetInput1)
            sumpf.connect(shift.GetOutput, add.SetInput2)
            sumpf.connect(add.GetOutput, plot.SetSignal)
            plot.LogarithmicX()
            plot.LogarithmicY()
            questionnaire.AssertYes(question="Are both axes now scaled logarithmically?", testcase=self)
            plot.ShowMajorGrid()
            plot.SetXInterval((0.01, 0.1))
            questionnaire.AssertYes(question="Does the x axis now span from 10ms to 100ms?", testcase=self)
            plot.SetMargin(0.03)
            questionnaire.AssertYes(question="Has the size of the plots been increased slightly?", testcase=self)
        finally:
            questionnaire.Close()

