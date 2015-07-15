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
import collections
from .lineplotpanel import LinePlotPanel


class SequencePlotPanel(LinePlotPanel):
    """
    A wx Panel that contains a plot of an iterable sequence like a tuple or a
    list.
    It is also possible to plot multiple lines by giving a sequence of sequences.
    """
    def __init__(self, parent, x_resolution=1.0, layout=LinePlotPanel.LAYOUT_ONE_PLOT, linemanager=LinePlotPanel.NO_DOWNSAMPLING, x_interval=None, margin=0.1, show_grid=None, show_cursors=True, cursor_positions=[], log_x=False, log_y=False, move_plots_together=False):
        """
        @param parent: the parent wx.Window of this panel
        @param x_resolution: a float that gives the x axis gap between two samples of the given sequence
        @param layout: one of the LAYOUT_... flags of the SequencePlotPanel class
        @param linemanager: as there are no downsamplers implemented yet, just set it to SequencePlotPanel.NO_DOWNSAMPLING
        @param x_interval: a tuple (min, max) of the visible interval on the x axis, or None to set interval automatically
        @param margin: the margin between the plots and the window border
        @param show_grid: True to show full grid behind plots, None to show major grid, False to hide grid
        @param log_x: a boolean value whether to show the x axis logarithmically (True) or linearly (False)
        @param log_y: True if the sequence shall be plotted with logarithmically scaled y axis, False otherwise
        @param move_plots_together: True if panning or zooming in one plot shall cause the other plots to move accordingly, False if all plots shall be panned or zoomed independently
        """
        self.__x_resolution = x_resolution
        self.__sequence = [[0.0, 0.0]]
        log_plots = set()
        if log_y:
            log_plots = set(["Y"])
        LinePlotPanel.__init__(self,
                               parent=parent,
                               layout=layout,
                               linemanager=linemanager,
                               components=["Y"],
                               margin=margin,
                               x_caption="X",
                               x_interval=x_interval,
                               show_legend=False,
                               show_grid=show_grid,
                               show_cursors=show_cursors,
                               cursor_positions=cursor_positions,
                               log_x=log_x,
                               log_y=log_plots,
                               hidden_components=set(),
                               move_plots_together=move_plots_together)

    @sumpf.Input(collections.Iterable)
    def SetSequence(self, sequence):
        """
        Sets the sequence which shall be plotted.
        If the items of the given sequence are again sequences themselves, each
        item will be plotted as a separate line.
        @param sequence: an iterable sequence like a tuple or a list
        """
        if isinstance(sequence[0], collections.Iterable):
            self.__sequence = sequence
        else:
            self.__sequence = [sequence]
        self._SetData(data={"Y": self.__sequence},
                      interval=(0.0, self.__x_resolution * (len(self.__sequence[0]))),
                      labels=[None] * len(self.__sequence))

    @sumpf.Input(float)
    def SetXResolution(self, resolution):
        """
        Sets the x axis gap between two samples of the given sequence.
        @param resolution: a float
        """
        self.__x_resolution = resolution
        self.SetSequence(self.__sequence)

    @sumpf.Trigger()
    def LinearY(self):
        """
        Shows the y axis linearly.
        """
        LinePlotPanel.LogarithmicY(self, component="Y", log=False)

    @sumpf.Trigger()
    def LogarithmicY(self, component="Y", log=True):
        """
        Shows the y axis logarithmically.
        """
        LinePlotPanel.LogarithmicY(self, component=component, log=log)

