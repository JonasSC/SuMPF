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
from .lineplotpanel import LinePlotPanel


class SignalPlotPanel(LinePlotPanel):
    """
    A wx Panel that contains a plot of a Signal and the corresponding toolbar.
    This panel is meant to be integrated into a GUI. If you want a simple plot
    consider using SignalPlotWindow.
    """
    def __init__(self, parent, layout=LinePlotPanel.LAYOUT_ONE_PLOT, linemanager=LinePlotPanel.NO_DOWNSAMPLING, x_interval=None, margin=0.1, show_legend=True, show_grid=None, show_cursors=True, cursor_positions=[], log_x=False, log_y=False, move_plots_together=False):
        """
        @param parent: the parent wx.Window of this panel
        @param layout: one of the LAYOUT_... flags of the SignalPlotPanel class
        @param linemanager: as there are no downsamplers implemented yet, just set it to SignalPlotPanel.NO_DOWNSAMPLING
        @param x_interval: a tuple (min, max) of the visible interval on the x axis, or None to set interval automatically
        @param margin: the margin between the plots and the window border
        @param show_legend: a boolean value whether to show the legend (True) or not (False)
        @param show_grid: True to show full grid behind plots, None to show major grid, False to hide grid
        @param log_x: a boolean value whether to show the x axis logarithmically (True) or linearly (False)
        @param log_y: True if the Signal shall be plotted with logarithmically scaled y axis, False otherwise
        @param move_plots_together: True if panning or zooming in one plot shall cause the other plots to move accordingly, False if all plots shall be panned or zoomed independently
        """
        log_plots = set()
        if log_y:
            log_plots = set(["Signal"])
        LinePlotPanel.__init__(self,
                               parent=parent,
                               layout=layout,
                               linemanager=linemanager,
                               components=["Signal"],
                               margin=margin,
                               x_caption="Time [s]",
                               x_interval=x_interval,
                               show_legend=show_legend,
                               show_grid=show_grid,
                               show_cursors=show_cursors,
                               cursor_positions=cursor_positions,
                               log_x=log_x,
                               log_y=log_plots,
                               hidden_components=set(),
                               move_plots_together=move_plots_together)

    @sumpf.Input(sumpf.Signal)
    def SetSignal(self, signal):
        """
        Sets the Signal which shall be plotted.
        @param signal: The Signal to plot
        """
        self._SetData(data={"Signal": signal.GetChannels()},
                      interval=(0.0, signal.GetDuration()),
                      labels=signal.GetLabels())

    @sumpf.Trigger()
    def LinearY(self):
        """
        Shows the y axis linearly.
        """
        LinePlotPanel.LogarithmicY(self, component="Signal", log=False)

    @sumpf.Trigger()
    def LogarithmicY(self, component="Signal", log=True):
        """
        Shows the y axis logarithmically.
        """
        LinePlotPanel.LogarithmicY(self, component=component, log=log)

