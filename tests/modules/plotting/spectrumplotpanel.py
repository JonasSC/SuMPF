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
class TestSpectrumPlotPanel(BaseTestCase):
    """
    An interactive TestCase for the SpectrumPlotPanel module.
    """
    def test_interactively(self):
        # setup a SpectrumPlotPanel in a TestQuestionnaire
        questionnaire = common.TestQuestionnaire(title="Testing SpectrumPlotPanel class")
        plot = sumpf.modules.SpectrumPlotPanel(parent=questionnaire)
        questionnaire.SetMainElement(plot)
        sumpf.connect(self.fft.GetSpectrum, plot.SetSpectrum)
        questionnaire.Show()
        # run the tests
        try:
            questionnaire.AssertYes(question="Does the plot show the magnitude and phase of two spectrums? (both spectrums plotted together with one plot each for magnitude and phase)", testcase=self)
            self.properties.SetSamplingRate(4000.0)
            questionnaire.AssertYes(question="Does the x-axis go to 2kHz now?", testcase=self)
            plot.HideLegend()
            questionnaire.AssertYes(question="Has the legend been hidden correctly? (the respective checkbox in the toolbar should be unchecked as well)", testcase=self)
            plot.HideGrid()
            questionnaire.AssertYes(question="Has the grid behind all plots been hidden?", testcase=self)
            plot.SetCursors([100.0, 1400.0])
            questionnaire.AssertYes(question="Are there two cursors (vertical lines) in the plot now?", testcase=self)
            self.copy.SetChannelCount(1)
            questionnaire.AssertYes(question="Has the green curve disappeared? (the cursors should still be visible)", testcase=self)
            plot.HidePhase()
            questionnaire.AssertYes(question="Has the plot for the phase been hidden?", testcase=self)
            self.copy.SetChannelCount(5)
            plot.SetLayout(sumpf.modules.SpectrumPlotPanel.LAYOUT_HORIZONTALLY_TILED)
            plot.ShowContinuousPhase()
            plot.ShowGroupDelay()
            questionnaire.AssertYes(question="Does the plot now show five groups of plots in three columns with three plots each and one line per plot?", testcase=self)
            plot.MovePlotsTogether()
            questionnaire.AssertYes(question="Please pan or zoom one plot. Do the other plots move accordingly?", testcase=self)
            self.copy.SetChannelCount(1)
            plot.LinearX()
            plot.LinearMagnitude()
            plot.HideContinuousPhase()
            plot.LogarithmicGroupDelay()
            questionnaire.AssertYes(question="Is there now one group of plots with a linear x-axis scale, linearly scaled magnitude and logarithmically scaled group delay?", testcase=self)
            plot.ShowMajorGrid()
            plot.SetXInterval((300.0, 3500.0))
            questionnaire.AssertYes(question="Does the x axis now span from 300Hz to 3.5kHz?", testcase=self)
            plot.SetMargin(0.03)
            questionnaire.AssertYes(question="Has the size of the plots been increased slightly?", testcase=self)
        finally:
            questionnaire.Close()

