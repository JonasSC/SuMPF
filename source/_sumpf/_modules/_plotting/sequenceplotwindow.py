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

import collections
import sumpf
from .plotwindow import PlotWindow
from .sequenceplotpanel import SequencePlotPanel


class SequencePlotWindow(PlotWindow):
    """
    A class whose instances create a window in which plots of iterable sequences
    like tuples or lists are shown.
    It is also possible to plot multiple lines by giving a sequence of sequences.
    """
    def __init__(self):
        PlotWindow.__init__(self)
        self.__sequence = [[0.0, 0.0]]
        self.__x_resolution = 1.0
        self.__log_y = False

    def _GetPanel(self):
        """
        Returns a properly initialized plot panel instance.
        @retval : a plot panel instance
        """
        panel = SequencePlotPanel(parent=self._window)
        panel.SetSequence(self.__sequence)
        panel.SetXResolution(self.__x_resolution)
        if self.__log_y:
            panel.LogarithmicY()
        else:
            panel.LinearY()
        return panel

    @sumpf.Input(collections.Iterable)
    def SetSequence(self, sequence):
        """
        Sets the sequence which shall be plotted.
        @param sequence: an iterable sequence like a tuple or a list
        """
        self.__sequence = sequence
        if self._panel is not None:
            self._panel.SetSequence(sequence)

    @sumpf.Input(float)
    def SetXResolution(self, resolution):
        """
        Sets the x axis gap between two samples of the given sequence.
        @param resolution: a float
        """
        self.__x_resolution = resolution
        if self._panel is not None:
            self._panel.SetXResolution(resolution)

    @sumpf.Trigger()
    def LinearY(self):
        """
        Shows the y axis linearly.
        """
        if self._panel is not None:
            self._panel.LinearY()

    @sumpf.Trigger()
    def LogarithmicY(self):
        """
        Shows the y axis logarithmically.
        """
        if self._panel is not None:
            self._panel.LogarithmicY()

