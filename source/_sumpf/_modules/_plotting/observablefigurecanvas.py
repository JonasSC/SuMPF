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

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg


class ObservableFigureCanvas(FigureCanvasWxAgg):
    """
    A FigureCanvasWxAgg whose draw method can call back observer functions.
    """
    def __init__(self, parent, id, figure, draw_observers=[]):
        FigureCanvasWxAgg.__init__(self, parent=parent, id=id, figure=figure)
        self.__draw_observers = draw_observers
        self.__drawing = False

    def draw(self, drawDC=None):
        """
        Override of the FigureCanvasWxAgg's draw method that calls the registered
        observer methods before the actual drawing.
        If the observer methods themselves call this method, their calls are skipped
        to avoid infinite loops.
        """
        if not self.__drawing:
            self.__drawing = True
            for o in self.__draw_observers:
                o()
            FigureCanvasWxAgg.draw(self, drawDC=drawDC)
            self.__drawing = False

