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

import math

import numpy
import wx

import matplotlib
matplotlib.interactive(False)
if matplotlib.get_backend() != 'WXAgg':
    matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from .observablefigurecanvas import ObservableFigureCanvas
from matplotlib.ticker import FuncFormatter, ScalarFormatter, NullFormatter

import sumpf
from .toolbar import Toolbar
from .plotlayouts import PlotLayout, PlotLayout_OnePlot, PlotLayout_HorizontallyTiled, PlotLayout_VerticallyTiled
from .linemanagers import LineManager, LineManagerNoDownsample


class LinePlotPanel(wx.Panel):
    NO_DOWNSAMPLING = LineManagerNoDownsample
    LAYOUT_ONE_PLOT = PlotLayout_OnePlot
    LAYOUT_HORIZONTALLY_TILED = PlotLayout_HorizontallyTiled
    LAYOUT_VERTICALLY_TILED = PlotLayout_VerticallyTiled

    def __init__(self, parent, layout, linemanager, components, margin, x_caption, x_interval, show_legend, show_grid, show_cursors, cursor_positions, log_x, log_y, hidden_components, move_plots_together):
        """
        @param parent: the parent wx.Window of this panel
        @param layout: one of the LAYOUT_... flags of the LinePlotPanel class
        @param linemanager: as there are no downsamplers implemented yet, just set it to LinePlotPanel.NO_DOWNSAMPLING
        @param components: a list of the names of the data's components (e.g. "Magnitude", "Phase" or "x", "y", "z")
        @param margin: the margin between the plots and the window border and the margin between different plots
        @param x_caption: a string containing the caption for the x axis
        @param x_interval: a tuple (min, max) of the visible interval on the x axis, or None to set interval automatically
        @param show_legend: a boolean value whether to show the legend (True) or not (False)
        @param show_grid: True to show full grid behind plots, None to show major grid, False to hide grid
        @param show_cursors: a boolean value whether to show cursors in the plots (True) or not (False). Cursors are vertical lines to indicate x-Axis values, not a mouse cursor
        @param cursor_positions: a list of x-Axis values, where a cursor shall be drawn.
        @param log_x: a boolean value whether to show the x axis logarithmically (True) or linearly (False)
        @param log_y: a set of component names whose plots shall be plotted with logarithmic y axis rather than linear
        @param hidden_components: a set of component names whose plots shall be hidden
        @param move_plots_together: True if panning or zooming in one plot shall cause the other plots to move accordingly, False if all plots shall be panned or zoomed independently
        """
        # initialize Panel
        wx.Panel.__init__(self, parent=parent)
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)
        self.__figure = sumpf.gui.run_in_mainloop(Figure)
        self.__canvas = sumpf.gui.run_in_mainloop(ObservableFigureCanvas, parent=self, id=wx.ID_ANY, figure=self.__figure, draw_observers=[self.__OnCanvasDraw])
        self.__canvas.mpl_connect('pick_event', self.__OnPick)
        self.__toolbar = Toolbar(parent=self, canvas=self.__canvas, components=components)
        self.__sizer.Add(self.__toolbar, 0, wx.LEFT | wx.EXPAND)
        self.__sizer.Add(self.__canvas, 1, wx.EXPAND)
        # store arguments
        self.__layout = layout
        self.__linemanager_class = linemanager
        self.__components = components
        self.__margin = margin
        self.__x_caption = x_caption
        self.__shown_x_interval = x_interval
        self.__show_legend = show_legend
        self.__show_grid = show_grid
        self.__show_cursors = show_cursors
        self.__cursor_positions = cursor_positions
        self.__logx = log_x
        self.__logy = set(log_y)
        self.__shown_components = []
        for c in self.__components:
            if c not in hidden_components:
                self.__shown_components.append(c)
        self.__move_plots_together = move_plots_together
        # store state variables
        self.__plots = []
        self.__lines = {}
        self.__data = None
        self.__labels = None
        self.__ordered_data = None
        self.__data_x_interval = (0.0, 1.0)
        self.__ordered_labels = None
        def dBlabel(y, pos):
            if y <= 0.0:
                return "0.0"
            else:
                spl = 20.0 * math.log(y, 10)
                return "%.1f dB" % spl
        self.__ytick_linformatter = ScalarFormatter()
        self.__ytick_logformatter = FuncFormatter(dBlabel)
        self.__picked = set()
        self.__updating = False

    def Layout(self):
        """
        Runs the layout algorithm and draws the plots.
        """
        sumpf.gui.run_in_mainloop(wx.Panel.Layout, self)
        self._UpdateGUI()

    @sumpf.Input(PlotLayout)
    def SetLayout(self, layout):
        """
        Sets the way, in which the plots shall be layouted.
        @param layout: One of the LAYOUT_... flags of this class
        """
        if layout != self.__layout:
            self.__layout = layout
            self.__picked = set()
            self.__RebuildFigure()
            self._SetData(data=self.__data, interval=self.__data_x_interval, labels=self.__labels)

    @sumpf.Input(LineManager)
    def SetLinemanager(self, linemanager):
        """
        Since there are no downsamplers implemented yet, do not use this method.
        It will, one day, provide a way to enable automatic downsampling, if the
        input data has too many samples to be plotted directly.
        """
        if linemanager != self.__linemanager_class:
            self.__linemanager_class = linemanager
            self.__RebuildFigure()
            self.__UpdatePlotLines()

    @sumpf.Input(float)
    def SetMargin(self, margin):
        """
        Sets the margin between the plots and the panel border.
        @param margin: the margin as integer
        """
        if margin != self.__margin:
            self.__margin = margin
            self.__RebuildFigure()
            self.__UpdatePlotLines()

    @sumpf.Input(tuple)
    def SetXInterval(self, interval):
        """
        Sets the interval on the x axis, which part of the plot is visible.
        @param interval: a tuple (min, max) of the visible interval on the x axis, or None to set interval automatically
        """
        changed = False
        shown_interval = self.__shown_x_interval
        if interval is None:
            if self.__shown_x_interval != self.__data_x_interval:
                shown_interval = self.__data_x_interval
                changed = True
        elif interval != self.__shown_x_interval:
            shown_interval = interval
            changed = True
        self.__shown_x_interval = interval
        if changed:
            number_of_samples = len(self.__data.values()[0][0])
            x_data = self.__CalculateXData(data_interval=self.__data_x_interval, shown_interval=shown_interval, number_of_samples=number_of_samples)
            for g in range(len(self.__plots)):
                for c in self.__plots[g]:
                    self.__plots[g][c].set_xlim(left=shown_interval[0], right=shown_interval[1])
                    for l in self.__lines[g][c]:
                        l.SetXData(x_data)

    @sumpf.Trigger()
    def ShowFullGrid(self):
        """
        Shows the full grid behind the plots.
        """
        self.__show_grid = True
        for g in range(len(self.__plots)):
            for c in self.__plots[g]:
                self.__plots[g][c].grid(b=True, which="both")
                if c in self.__logy:
                    if len(numpy.nonzero(self.__ordered_data[g][c])[0]) != 0:
                        self.__plots[g][c].yaxis.set_major_formatter(self.__ytick_logformatter)
                        self.__plots[g][c].yaxis.set_minor_formatter(self.__ytick_logformatter)
                else:
                    self.__plots[g][c].yaxis.set_major_formatter(self.__ytick_linformatter)
                    self.__plots[g][c].yaxis.set_minor_formatter(self.__ytick_linformatter)
        self._UpdateGUI()

    @sumpf.Trigger()
    def ShowMajorGrid(self):
        """
        Shows the grid only for major numbers.
        """
        self.__show_grid = None
        for g in range(len(self.__plots)):
            for c in self.__plots[g]:
                self.__plots[g][c].grid(b=False, which="minor")
                self.__plots[g][c].grid(b=True, which="major")
                if c in self.__logy:
                    if len(numpy.nonzero(self.__ordered_data[g][c])[0]) != 0:
                        self.__plots[g][c].yaxis.set_major_formatter(self.__ytick_logformatter)
                else:
                    self.__plots[g][c].yaxis.set_major_formatter(self.__ytick_linformatter)
                self.__plots[g][c].yaxis.set_minor_formatter(NullFormatter())
        self._UpdateGUI()

    @sumpf.Trigger()
    def HideGrid(self):
        """
        Hides the grid behind the plots.
        """
        self.__show_grid = False
        for g in range(len(self.__plots)):
            for c in self.__plots[g]:
                self.__plots[g][c].grid(b=False, which="both")
                if c in self.__logy:
                    if len(numpy.nonzero(self.__ordered_data[g][c])[0]) != 0:
                        self.__plots[g][c].yaxis.set_major_formatter(self.__ytick_logformatter)
                else:
                    self.__plots[g][c].yaxis.set_major_formatter(self.__ytick_linformatter)
                self.__plots[g][c].yaxis.set_minor_formatter(NullFormatter())
        self._UpdateGUI()

    @sumpf.Trigger()
    def ShowLegend(self):
        """
        Shows a legend in the plot.
        """
        self.__show_legend = True
        for g in self.__plots:
            g[self.__shown_components[0]].legend(loc='best')
        self._UpdateGUI()

    @sumpf.Trigger()
    def HideLegend(self):
        """
        Hides the plot's legend.
        """
        self.__show_legend = False
        for g in self.__plots:
            g[self.__shown_components[0]].legend_ = None
        self._UpdateGUI()

    @sumpf.Trigger()
    def ShowCursors(self):
        """
        Shows the cursors in the plots.
        In this case, "cursors" does not mean the mouse cursor, but a vertical
        line, that indicates a position on the x-Axis.
        """
        self.__show_cursors = True
        for g in range(len(self.__plots)):
            for c in self.__plots[g]:
                for i in range(len(self.__ordered_data[g][c]), len(self.__plots[g][c].lines)):
                    self.__plots[g][c].lines[i].set_visible(True)
        self._UpdateGUI()

    @sumpf.Trigger()
    def HideCursors(self):
        """
        Hides the cursors in the plots.
        In this case, "cursors" does not mean the mouse cursor, but a vertical
        line, that indicates a position on the x-Axis.
        """
        self.__show_cursors = False
        for g in range(len(self.__plots)):
            for c in self.__plots[g]:
                for i in range(len(self.__ordered_data[g][c]), len(self.__plots[g][c].lines)):
                    self.__plots[g][c].lines[i].set_visible(False)
        self._UpdateGUI()

    @sumpf.Input(list)
    def SetCursors(self, cursors):
        """
        Draws cursors at the given positions at the x-Axis. The number of cursors
        will be the number of given lines.
        In this case, "cursors" does not mean the mouse cursor, but a vertical
        line, that indicates a position on the x-Axis.
        If the cursors are hidden, it might be useful to make them visible with
        the ShowCursors method.
        @param cursors: a list of x-Axis values, where cursors shall be shown
        """
        self.__cursor_positions = cursors
        for g in range(len(self.__plots)):
            for c in self.__plots[g]:
                plot = self.__plots[g][c]
                number_of_lines = len(self.__ordered_data[g][c])
                # update existing cursors
                for i in range(number_of_lines, min(len(plot.lines), number_of_lines + len(self.__cursor_positions))):
                    plot.lines[i].set_xdata([self.__cursor_positions[i - number_of_lines], self.__cursor_positions[i - number_of_lines]])
                # delete surplus cursors, if needed
                del plot.lines[number_of_lines + len(self.__cursor_positions):]
                # create new cursors, if needed
                for i in range(len(plot.lines), number_of_lines + len(self.__cursor_positions)):
                    l = plot.axvline(x=self.__cursor_positions[i - number_of_lines], color='k', linestyle='--')
                    if not self.__show_cursors:
                        l.set_visible(False)
        self._UpdateGUI()

    @sumpf.Trigger()
    def LinearX(self):
        """
        Shows the x axis linearly
        """
        self.__logx = False
        for g in range(len(self.__plots)):
            for c in self.__plots[g]:
                plot = self.__plots[g][c]
                plot.set_xscale("linear")
                # revert the possible changes in the shown interval, that might
                # have been made during log scaling
                xlim = plot.get_xlim()
                if xlim != self.__shown_x_interval:
                    if self.__shown_x_interval is None:
                        data_range = self.__data_x_interval[1] - self.__data_x_interval[0]
                        plot.set_xlim(left=self.__data_x_interval[0] - 0.05 * data_range, right=self.__data_x_interval[1] + 0.05 * data_range)
                    else:
                        plot.set_xlim(left=self.__shown_x_interval[0], right=self.__shown_x_interval[1])
        self._UpdateGUI()

    @sumpf.Trigger()
    def LogarithmicX(self):
        """
        Shows the x axis logarithmically
        """
        self.__logx = True
        for g in range(len(self.__plots)):
            for c in self.__plots[g]:
                plot = self.__plots[g][c]
                xlim = plot.get_xlim()                                              # avoid an error
                if xlim[0] == 0.0:                                                  # when the shown
                    resolution = xlim[1] / float(len(self.__ordered_data[g][c]))    # interval starts
                    plot.set_xlim(left=resolution / 2.0, right=xlim[1])             # with zero
                plot.set_xscale("log")
        self._UpdateGUI()

    def LogarithmicY(self, component, log):
        """
        Shows the y axis of the plot the given component logarithmically or linearly.
        Other than LinearX and LogarithmicX methods there should be a facade for
        this method in a derived class.
        @param component: the name of the component that shall be changed
        @param log: if True, the component's y data will be plotted logarithmically, otherwise linearly
        """
        if log:
            self.__logy.add(component)
            formatter = self.__ytick_logformatter
        else:
            self.__logy.discard(component)
        if component in self.__shown_components:
            formatter = self.__ytick_linformatter
            if log:
                formatter = self.__ytick_logformatter
            for g in range(len(self.__plots)):
                data_max = numpy.max(self.__ordered_data[g][component])
                if data_max > 0.0:
                    if log:
                        # read just visible interval, if it goes below zero
                        ylim = self.__plots[g][component].get_ylim()
                        new_ylim_min, new_ylim_max = ylim
                        if ylim[0] <= 0.0:
                            data_min = numpy.min(self.__ordered_data[g][component])
                            if data_min > 0.0:
                                new_ylim_min = data_min / 2.0
                        if ylim[1] <= 0.0:
                            new_ylim_max = data_max * 2.0
                            if new_ylim_min <= 0.0:
                                new_ylim_min = new_ylim_max / 1000.0
                        if (new_ylim_min, new_ylim_max) != ylim:
                            self.__plots[g][component].set_ylim(new_ylim_min, new_ylim_max)
                        self.__plots[g][component].set_yscale("log")
                    else:
                        # set the visible y axis interval to something useful, when switching to linear scale
                        if self.__plots[g][component].get_yscale() != "linear":
                            self.__plots[g][component].set_yscale("linear")
                            data_min = numpy.min(self.__ordered_data[g][component])
                            new_ylim_min = 0.9 * data_min
                            new_ylim_max = 1.1 * data_max
                            if data_min < 0.0:
                                new_ylim_min = 1.1 * data_min
                            elif new_ylim_min < 0.2 * new_ylim_max:
                                new_ylim_min = 0.0
                            self.__plots[g][component].set_ylim(new_ylim_min, new_ylim_max)
                    self.__plots[g][component].yaxis.set_major_formatter(formatter)
                    if bool(self.__show_grid):
                        self.__plots[g][component].yaxis.set_minor_formatter(formatter)
                    else:
                        self.__plots[g][component].yaxis.set_minor_formatter(NullFormatter())
            self._UpdateGUI()

    def _SetData(self, data, interval, labels):
        """
        Sets the data for the plot.
        @param data: a dictionary of components, which are a list of channels, which are a list of samples
        @param interval: the interval on the x axis between which the given data is located
        @param labels: a tuple of labels, one for each channel. A label can be either a string or None
        """
        self.__data = data
        self.__data_x_interval = interval
        self.__labels = []
        for i in range(len(self.__data.values()[0])):
            if labels[i] is not None:
                self.__labels.append(labels[i])
            else:
                self.__labels.append("Channel %i" % (i + 1))
        ordered_data, ordered_labels = self.__layout.FormatData(data=data, labels=labels, components=self.__shown_components)
        self.__ordered_data = ordered_data
        self.__ordered_labels = ordered_labels
        self.__UpdatePlotLines()

    def ShowComponent(self, component, show):
        """
        Shows or hides the plots of the given component.
        @param component: the name of the component that shall be shown or hidden
        @param show: if True, the component will be shown, otherwise it will be hidden
        """
        changed = False
        if show:
            if component not in self.__shown_components:
                shown = []
                for c in self.__components:
                    if c in self.__shown_components or c == component:
                        shown.append(c)
                self.__shown_components = shown
                changed = True
        else:
            if component in self.__shown_components:
                if len(self.__shown_components) <= 1:
                    raise RuntimeError("It is not possible to hide all plots at once")
                self.__shown_components.remove(component)
                changed = True
        if changed:
            self.__RebuildFigure()
            self._SetData(data=self.__data, interval=self.__data_x_interval, labels=self.__labels)

    @sumpf.Trigger()
    def MovePlotsTogether(self):
        """
        Sets that all plots shall be moved accordingly, when one plot is panned or zoomed.
        """
        self.__move_plots_together = True
        self._UpdateGUI()

    @sumpf.Trigger()
    def MovePlotsIndependently(self):
        """
        Sets that all plots shall be panned or zoomed independently.
        """
        self.__move_plots_together = False
        self._UpdateGUI()

    def _UpdateGUI(self):
        """
        Updates the GUI by redrawing the plot canvas and updating the toolbar status.
        """
        if not self.__updating:
            sumpf.gui.run_in_mainloop(self.__canvas.draw)
            self.__toolbar.UpdateToolbar(legend=self.__show_legend,
                                         grid=self.__show_grid,
                                         cursors=self.__show_cursors,
                                         logx=self.__logx,
                                         logy=self.__logy,
                                         shown=self.__shown_components,
                                         move_plots_together=self.__move_plots_together)

    def __OnPick(self, event):
        """
        An event handler for the matplotlib event of clicking on a line.
        If the line is not picked yet, this method adds its line number to the
        self.__picked set and displays the line a bit thicker. Otherwise, it
        removes the respective line number from the set and resets the line display
        to normal thickness.
        """
        def get_picked_line_number(line):
            # returns the plot number and the line number in the plot
            for p in self.__lines:
                for c in self.__lines[p]:
                    for n in range(len(self.__lines[p][c])):
                        if self.__lines[p][c][n].HasLine(line):
                            return (p, n)
            return None, None
        picked = get_picked_line_number(event.artist)
        if picked[0] is not None:
            if picked in self.__picked:
                for c in self.__lines[picked[0]]:
                    self.__lines[picked[0]][c][picked[1]].Normal()
                self.__picked.remove(picked)
            else:
                for c in self.__lines[picked[0]]:
                    self.__lines[picked[0]][c][picked[1]].Bold()
                self.__picked.add(picked)
        if self.__show_legend:
            for g in self.__plots:
                g[self.__shown_components[0]].legend(loc='best')
        self.__canvas.draw()

    def __CalculateXData(self, data_interval, shown_interval, number_of_samples):
        """
        Calculates and returns the x data for the plots and the line labels.
        @param data_interval: the x data interval of the input data
        @param shown_interval: the interval on the plot's x axis that is currently visible
        @param number_of_samples: the number of samples of the input data
        @retval : a tuple (data, labels) which contains the x data and labels in the structure as self.__plots
        """
        figure_width = int(self.__figure.get_size_inches()[0] * self.__figure.get_dpi())
        return self.__linemanager_class.GetXData(data_interval=data_interval,
                                                 shown_interval=shown_interval,
                                                 number_of_samples=number_of_samples,
                                                 figure_width=figure_width)

    def __UpdatePlotLines(self):
        """
        Updates the plotted data and restores the plot's settings (grid, legend, ...).
        """
        if len(self.__ordered_data) != len(self.__plots):
            self.__RebuildFigure()
        shown_interval = self.__shown_x_interval
        if shown_interval is None:
            shown_interval = self.__data_x_interval
        x_data = self.__CalculateXData(data_interval=self.__data_x_interval, shown_interval=shown_interval, number_of_samples=len(self.__ordered_data[0].values()[0][0]))
        for g in range(len(self.__plots)):
            for c in self.__plots[g]:
                plot = self.__plots[g][c]
                lines = self.__lines[g][c]
                lines_data = self.__ordered_data[g][c]
                for i in range(min(len(lines), len(lines_data))):   # replace values of existing lines
                    lines[i].SetData(x_data=x_data, y_data=lines_data[i], interval=self.__data_x_interval, label=self.__ordered_labels[g][c][i])
                for i in range(len(lines), len(lines_data)):        # create new lines if necessary
                    lines.append(self.__linemanager_class(plot=plot, x_data=x_data, y_data=lines_data[i], interval=self.__data_x_interval, label=self.__ordered_labels[g][c][i]))
                    if (g, i) in self.__picked:
                        lines[i].Bold()
                for i in range(len(lines_data), len(lines)):        # Delete surplus lines
                    lines[i].Delete()
                    if (g, i) in self.__picked:
                        self.__picked.remove((g, i))
                del lines[len(lines_data):]
        # restore settings
        self.__updating = True
        if self.__show_legend:
            self.ShowLegend()
        if self.__show_grid is None:
            self.ShowMajorGrid()
        elif self.__show_grid:
            self.ShowFullGrid()
        self.SetCursors(self.__cursor_positions)
        if self.__logx:
            self.LogarithmicX()
        for p in self.__logy:
            self.LogarithmicY(component=p, log=True)
        self.SetXInterval(interval=self.__shown_x_interval)
        self.__updating = False
        self._UpdateGUI()

    def __RebuildFigure(self):
        """
        Destroys all plots in the figure and rebuilds them again.
        This is necessary, when the shown components have changed, or the layout
        of the plots has changed.
        """
        def rebuild_figure():
            for g in range(len(self.__plots)):
                for c in self.__plots[g]:
                    for l in self.__lines[g][c]:
                        l.Delete()
                    self.__figure.delaxes(self.__plots[g][c])
            self.__figure.clear()
            self.__plots = self.__layout.CreatePlots(figure=self.__figure, data=self.__data, components=self.__shown_components, margin=self.__margin, x_caption=self.__x_caption)
        sumpf.gui.run_in_mainloop(rebuild_figure)
        self.__lines = {}
        for g in range(len(self.__plots)):
            self.__lines[g] = {}
            for c in self.__plots[g]:
                self.__lines[g][c] = []
                if self.__shown_x_interval is not None:
                    self.__plots[g][c].set_xlim(left=self.__shown_x_interval[0], right=self.__shown_x_interval[1])

    def __OnCanvasDraw(self):
        """
        A callback that is called, when the FigureCanvas's draw method is called.
        Currently this is only used to move all other plots accordingly, when one
        plot is panned or zoomed.
        """
        if self.__move_plots_together:
            changed = self.__GetIndicesOfChangedPlot(self.__plots, self.__shown_x_interval)
            if changed is not None:
                cg, cc = changed
                x_interval = self.__plots[cg][cc].get_xlim()
                y_interval = self.__plots[cg][cc].get_ylim()
                for g in self.__plots:
                    g[cc].set_ylim(*y_interval)
                self.SetXInterval(x_interval)

    def __GetIndicesOfChangedPlot(self, plots, current_x_interval):
        """
        When one plot is panned or zoomed, this method can be used to find out
        which one of the plots it is.
        @param plots: the __plots data structure of this panel
        @param current_x_interval: the shown interval on the x axis
        @retval : a tuple (group, component), whose elements can be used as indices to address the plot in the plot data structure
        """
        if current_x_interval is None:
            if len(plots) * len(plots[0]) < 3:
                return 0, plots[0].keys()[0]
            # search for changes of the shown x interval, when the current x interval is None
            xlims = {}
            for g in range(len(plots)):
                for c in plots[g]:
                    xlim = plots[g][c].get_xlim()
                    if xlim in xlims:
                        if len(xlims) == 1:
                            xlims[xlim].append((g, c))
                        else:
                            for l in xlims:
                                if l != xlim:
                                    return xlims[l][0]
                    else:
                        if len(xlims) > 0 and len(xlims.values()[0]) > 1:
                            return g, c
                        else:
                            xlims[xlim] = [(g, c)]
        else:
            # search for changes of the shown x interval, by looking which plot has another interval than the current x interval
            for g in range(len(plots)):
                for c in plots[g]:
                    xlim = plots[g][c].get_xlim()
                    if xlim != current_x_interval:
                        return g, c
        # search for changes of the shown y interval
        group = None
        component = None
        display_intervals = []
        ylim = plots[g][c].get_ylim()
        intervals = (xlim, ylim)
        if intervals in display_intervals:
            if len(display_intervals) > 1:
                return group, component
        else:
            group = g
            component = c
            display_intervals.append(intervals)
        return None

