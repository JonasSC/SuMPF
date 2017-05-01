# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2016 Jonas Schulte-Coerne
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
from .lineplotpanel import LinePlotPanel


class SpectrumPlotPanel(LinePlotPanel):
    """
    A wx Panel that contains a plot of a Spectrum and the corresponding toolbar.
    This panel is meant to be integrated into a GUI. If you want a simple plot
    consider using SpectrumPlotWindow.
    """
    def __init__(self, parent, layout=LinePlotPanel.LAYOUT_ONE_PLOT, linemanager=LinePlotPanel.NO_DOWNSAMPLING, x_interval=None, margin=0.1, show_legend=True, show_grid=None, show_cursors=True, cursor_positions=[], log_x=True, log_y=set(["Magnitude"]), hidden_components=set(["Phase", "Continuous phase", "Group delay", "Real part", "Imaginary part"]), move_plots_together=False):
        """
        @param parent: the parent wx.Window of this panel
        @param layout: one of the LAYOUT_... flags of the SpectrumPlotPanel class
        @param linemanager: as there are no downsamplers implemented yet, just set it to SpectrumPlotPanel.NO_DOWNSAMPLING
        @param margin: the margin between the plots and the window border
        @param x_interval: a tuple (min, max) of the visible interval on the x axis, or None to set interval automatically
        @param margin: the margin between the plots and the window border
        @param show_legend: a boolean value whether to show the legend (True) or not (False)
        @param show_grid: True to show full grid behind plots, None to show major grid, False to hide grid
        @param log_x: a boolean value whether to show the x axis logarithmically (True) or linearly (False)
        @param log_y: a set of plot names whose plots shall be plotted with logarithmic y axis rather than linear
        @param hidden_components: a set of component names whose plots shall be hidden
        @param move_plots_together: True if panning or zooming in one plot shall cause the other plots to move accordingly, False if all plots shall be panned or zoomed independently
        """
        LinePlotPanel.__init__(self,
                               parent=parent,
                               layout=layout,
                               linemanager=linemanager,
                               components=("Magnitude", "Phase", "Continuous phase", "Group delay", "Real part", "Imaginary part"),
                               x_caption="Frequency [Hz]",
                               x_interval=x_interval,
                               margin=margin,
                               show_legend=show_legend,
                               show_grid=show_grid,
                               show_cursors=show_cursors,
                               cursor_positions=cursor_positions,
                               log_x=log_x,
                               log_y=log_y,
                               hidden_components=hidden_components,
                               move_plots_together=move_plots_together)

    @sumpf.Input(sumpf.Spectrum)
    def SetSpectrum(self, spectrum):
        """
        Sets the Spectrum which shall be plotted.
        @param spectrum: The Spectrum to plot
        """
        self._SetData(data={"Magnitude": spectrum.GetMagnitude(),
                            "Phase": spectrum.GetPhase(),
                            "Continuous phase": spectrum.GetContinuousPhase(),
                            "Group delay": spectrum.GetGroupDelay(),
                            "Real part": spectrum.GetReal(),
                            "Imaginary part": spectrum.GetImaginary()},
                      interval=(0.0, spectrum.GetResolution() * (len(spectrum) - 1)),
                      labels=spectrum.GetLabels())

    @sumpf.Trigger()
    def LinearMagnitude(self):
        """
        Shows the magnitude linearly.
        """
        self.LogarithmicY(component="Magnitude", log=False)

    @sumpf.Trigger()
    def LogarithmicMagnitude(self):
        """
        Shows the magnitude logarithmically.
        """
        self.LogarithmicY(component="Magnitude", log=True)

    @sumpf.Trigger()
    def LinearPhase(self):
        """
        Shows the phase linearly.
        """
        self.LogarithmicY(component="Phase", log=False)

    @sumpf.Trigger()
    def LogarithmicPhase(self):
        """
        Shows the phase logarithmically.
        """
        self.LogarithmicY(component="Phase", log=True)

    @sumpf.Trigger()
    def LinearContinuousPhase(self):
        """
        Shows the continuous phase linearly.
        """
        self.LogarithmicY(component="Continuous phase", log=False)

    @sumpf.Trigger()
    def LogarithmicContinuousPhase(self):
        """
        Shows the continuous phase logarithmically.
        """
        self.LogarithmicY(component="Continuous phase", log=True)

    @sumpf.Trigger()
    def LinearGroupDelay(self):
        """
        Shows the group delay linearly.
        """
        self.LogarithmicY(component="Group delay", log=False)

    @sumpf.Trigger()
    def LogarithmicGroupDelay(self):
        """
        Shows the group delay logarithmically.
        """
        self.LogarithmicY(component="Group delay", log=True)

    @sumpf.Trigger()
    def LinearReal(self):
        """
        Shows the real part linearly.
        """
        self.LogarithmicY(component="Real part", log=False)

    @sumpf.Trigger()
    def LogarithmicReal(self):
        """
        Shows the real part logarithmically.
        """
        self.LogarithmicY(component="Real part", log=True)

    @sumpf.Trigger()
    def LinearImaginary(self):
        """
        Shows the imaginary part linearly.
        """
        self.LogarithmicY(component="Imaginary part", log=False)

    @sumpf.Trigger()
    def LogarithmicImaginary(self):
        """
        Shows the imaginary part logarithmically.
        """
        self.LogarithmicY(component="Imaginary part", log=True)

    @sumpf.Trigger()
    def ShowMagnitude(self):
        """
        Shows the magnitude plot.
        """
        self.ShowComponent(component="Magnitude", show=True)

    @sumpf.Trigger()
    def HideMagnitude(self):
        """
        Hides the magnitude plot.
        """
        self.ShowComponent(component="Magnitude", show=False)

    @sumpf.Trigger()
    def ShowPhase(self):
        """
        Shows the phase plot.
        """
        self.ShowComponent(component="Phase", show=True)

    @sumpf.Trigger()
    def HidePhase(self):
        """
        Hides the phase plot.
        """
        self.ShowComponent(component="Phase", show=False)

    @sumpf.Trigger()
    def ShowContinuousPhase(self):
        """
        Shows the continuous phase plot.
        """
        self.ShowComponent(component="Continuous phase", show=True)

    @sumpf.Trigger()
    def HideContinuousPhase(self):
        """
        Hides the continuous phase plot.
        """
        self.ShowComponent(component="Continuous phase", show=False)

    @sumpf.Trigger()
    def ShowGroupDelay(self):
        """
        Shows the group delay plot.
        """
        self.ShowComponent(component="Group delay", show=True)

    @sumpf.Trigger()
    def HideGroupDelay(self):
        """
        Hides the group delay plot.
        """
        self.ShowComponent(component="Group delay", show=False)

    @sumpf.Trigger()
    def ShowReal(self):
        """
        Shows the plot of the real part.
        """
        self.ShowComponent(component="Real part", show=True)

    @sumpf.Trigger()
    def HideReal(self):
        """
        Hides the plot of the real part.
        """
        self.ShowComponent(component="Real part", show=False)

    @sumpf.Trigger()
    def ShowImaginary(self):
        """
        Shows the plot of the imaginary part.
        """
        self.ShowComponent(component="Imaginary part", show=True)

    @sumpf.Trigger()
    def HideImaginary(self):
        """
        Hides the plot of the imaginary part.
        """
        self.ShowComponent(component="Imaginary part", show=False)

