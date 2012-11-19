# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012 Jonas Schulte-Coerne
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
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.ticker import FuncFormatter, ScalarFormatter, NullFormatter

import sumpf
from .toolbar import Toolbar


class BaseLinePlotPanel(wx.Panel):
	"""
	A subclass of wx.Panel that encapsulates the matplotlib stuff.
	"""
	def __init__(self, parent, components, x_caption, x_interval, margin, show_legend, show_grid, show_cursors, cursor_positions, log_x, log_y, hidden_components):
		"""
		@param parent: the parent wx.Window of this panel
		@param components: a list of the names of the data's components (e.g. "Magnitude", "Phase" or "x", "y", "z")
		@param x_caption: a string containing the caption for the x axis
		@param x_interval: a tuple (min, max) of the visible interval on the x axis, or None to set interval automatically
		@param margin: the margin between the plots and the window border and the margin between different plots
		@param show_legend: a boolean value whether to show the legend (True) or not (False)
		@param show_grid: True to show full grid behind plots, None to show major grid, False to hide grid
		@param show_cursors: a boolean value whether to show cursors in the plots (True) or not (False). Cursors are vertical lines to indicate x-Axis values, not a mouse cursor
		@param cursor_positions: a list of x-Axis values, where a cursor shall be drawn.
		@param log_x: a boolean value whether to show the x axis logarithmically (True) or linearly (False)
		@param log_y: a set of component names whose plots shall be plotted with logarithmic y axis rather than linear
		@param hidden_components: a set of component names whose plots shall be hidden
		"""
		# initialize Panel
		wx.Panel.__init__(self, parent=parent)
		# store arguments
		self._components = components
		self._x_caption = x_caption
		self.__x_interval = x_interval
		self._margin = margin
		self._show_legend = show_legend
		self.__show_grid = show_grid
		self.__show_cursors = show_cursors
		self.__cursor_positions = cursor_positions
		self.__logx = log_x
		self.__logy = set(log_y)
		self._shown = set(components) - set(hidden_components)
		# store other stuff
		self._plots = {}	# self._plots[GROUP_NAME][COMPONENT_NAME] = INSTANCE_OF_"matplotlib.Axes"
		def dBlabel(y, pos):
			if y <= 0.0:
				return "0.0"
			else:
				spl = 20.0 * math.log(y, 10)
				return "%.1f dB" % spl
		self.__ytick_linformatter = ScalarFormatter()
		self.__ytick_logformatter = FuncFormatter(dBlabel)
		# wx stuff
		self.__sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.__sizer)
		# matplotlib stuff
		self._figure = Figure()
		self.__canvas = FigureCanvas(parent=self, id=wx.ID_ANY, figure=self._figure)
		self.__toolbar = Toolbar(parent=self, canvas=self.__canvas, components=components)
		self.__sizer.Add(self.__toolbar, 0, wx.LEFT | wx.EXPAND)
		self.__sizer.Add(self.__canvas, 1, wx.EXPAND)
		# data
		self._x_data = None
		self._y_data = None
		self._labels = None
		self._y_plotdata = {}	# a dictionary for plotted y-axis data with the same structure as self._plots: self._y_plotdata[GROUP_NAME][COMPONENT_NAME] = LIST_OF_CHANNELS

	def Layout(self):
		"""
		Runs the layout algorithm and draws the plots.
		"""
		wx.Panel.Layout(self)
		self._UpdateGUI()

	def _SetData(self, x_data, y_data, labels):
		"""
		Sets the data for the plot.
		@param x_data: A tuple of x-axis values
		@param y_data: A dictionary which maps captions to tuples of channels where a channel is a tuple of samples
		@param labels: a tuple of labels, one for each channel. A label can be either a string or None
		"""
		# store new data
		self._x_data = x_data
		self._y_data = y_data
		self._labels = labels
		# clear the canvas
		for g in list(self._plots.values()):
			for p in g.values():
				del p.lines[:]
				self._figure.delaxes(p)
		self._figure.clear()
		self._plots = {}
		self._y_plotdata = {}
		# create new plots
		self._CreatePlots()
		# restore old settings
		self.SetXInterval(self.__x_interval)
		if self._show_legend:
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

	@sumpf.Input(tuple)
	def SetXInterval(self, interval):
		"""
		Sets the interval on the x axis, which part of the plot is visible.
		@param interval: a tuple (min, max) of the visible interval on the x axis, or None to set interval automatically
		"""
		self.__x_interval = interval
		for g in self._plots.values():
			for p in g.values():
				if interval is None:
					p.set_xlim(auto=True)
				else:
					p.set_xlim(left=interval[0], right=interval[1])
		self._UpdateGUI()

	@sumpf.Input(int)
	def SetMargin(self, margin):
		"""
		Sets the margin between the plots and the panel border.
		@param margin: the margin as integer
		"""
		self._margin = margin
		if self._x_data is not None and self._y_data is not None and self._labels is not None:
			self._SetData(self._x_data, self._y_data, self._labels)

	@sumpf.Trigger()
	def ShowFullGrid(self):
		"""
		Shows the full grid behind the plots.
		"""
		self.__show_grid = True
		for g in self._plots.values():
			for c in g:
				g[c].grid(b=True, which="both")
				if c in self.__logy:
					if len(numpy.nonzero([l.get_ydata() for l in g[c].lines])[0]) != 0:
						g[c].yaxis.set_major_formatter(self.__ytick_logformatter)
						g[c].yaxis.set_minor_formatter(self.__ytick_logformatter)
				else:
					g[c].yaxis.set_major_formatter(self.__ytick_linformatter)
					g[c].yaxis.set_minor_formatter(self.__ytick_linformatter)
		self._UpdateGUI()

	@sumpf.Trigger()
	def ShowMajorGrid(self):
		"""
		Shows the grid only for major numbers.
		"""
		self.__show_grid = None
		for g in self._plots.values():
			for c in g:
				g[c].grid(b=False, which="minor")
				g[c].grid(b=True, which="major")
				if c in self.__logy:
					if len(numpy.nonzero([l.get_ydata() for l in g[c].lines])[0]) != 0:
						g[c].yaxis.set_major_formatter(self.__ytick_logformatter)
				else:
					g[c].yaxis.set_major_formatter(self.__ytick_linformatter)
				g[c].yaxis.set_minor_formatter(NullFormatter())
		self._UpdateGUI()

	@sumpf.Trigger()
	def HideGrid(self):
		"""
		Hides the grid behind the plots.
		"""
		self.__show_grid = False
		for g in self._plots.values():
			for c in g:
				g[c].grid(b=False, which="both")
				if c in self.__logy:
					if len(numpy.nonzero([l.get_ydata() for l in g[c].lines])[0]) != 0:
						g[c].yaxis.set_major_formatter(self.__ytick_logformatter)
				else:
					g[c].yaxis.set_major_formatter(self.__ytick_linformatter)
				g[c].yaxis.set_minor_formatter(NullFormatter())
		self._UpdateGUI()

	@sumpf.Trigger()
	def ShowLegend(self):
		"""
		Shows a legend in the plot.
		"""
		self._show_legend = True
		component = None
		for c in self._components:
			if c in self._shown:
				component = c
				break
		if component is not None:
			for g in self._plots.values():
				g[component].legend(loc='best')
		self._UpdateGUI()

	@sumpf.Trigger()
	def HideLegend(self):
		"""
		Hides the plot's legend.
		"""
		self._show_legend = False
		component = None
		for c in self._components:
			if c in self._shown:
				component = c
				break
		if component is not None:
			for g in self._plots.values():
				g[component].legend_ = None
		self._UpdateGUI()

	@sumpf.Trigger()
	def ShowCursors(self):
		"""
		Shows the cursors in the plots.
		In this case, "cursors" does not mean the mouse cursor, but a vertical
		line, that indicates a position on the x-Axis.
		"""
		self.__show_cursors = True
		for g in self._plots:
			for c in self._plots[g]:
				for i in range(len(self._y_plotdata[g][c]), len(self._plots[g][c].lines)):
					self._plots[g][c].lines[i].set_visible(True)
		self._UpdateGUI()

	@sumpf.Trigger()
	def HideCursors(self):
		"""
		Hides the cursors in the plots.
		In this case, "cursors" does not mean the mouse cursor, but a vertical
		line, that indicates a position on the x-Axis.
		"""
		self.__show_cursors = False
		for g in self._plots:
			for c in self._plots[g]:
				for i in range(len(self._y_plotdata[g][c]), len(self._plots[g][c].lines)):
					self._plots[g][c].lines[i].set_visible(False)
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
		for g in self._plots:
			for c in self._plots[g]:
				plot = self._plots[g][c]
				number_of_lines = len(self._y_plotdata[g][c])
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
		for g in self._plots.values():
			for p in g.values():
				p.set_xscale("linear")
		self._UpdateGUI()

	@sumpf.Trigger()
	def LogarithmicX(self):
		"""
		Shows the x axis logarithmically
		"""
		self.__logx = True
		if len(numpy.nonzero(self._x_data)[0]) != 0:
			for g in self._plots.values():
				for p in g.values():
					p.set_xscale("log")
		self._UpdateGUI()

	def LogarithmicY(self, component, log):
		"""
		Shows the y axis of the plot the given component logarithmically or linearly.
		Other than LinearX and LogarithmicX methods there should be a facade for
		this method in a derived class.
		@param component: the name of the component that shall be changed
		@param log: if True, the component's y data will be plotted logarithmically, otherwise linearly
		"""
		if component in self._shown:
			scale = "linear"
			formatter = self.__ytick_linformatter
			if log:
				self.__logy.add(component)
				scale = "log"
				formatter = self.__ytick_logformatter
			else:
				self.__logy.discard(component)
			for g in self._plots:
				if len(numpy.nonzero([l.get_ydata() for l in self._plots[g][component].lines])[0]) != 0:
					self._plots[g][component].set_yscale(scale)
					self._plots[g][component].yaxis.set_major_formatter(formatter)
					if bool(self.__show_grid):
						self._plots[g][component].yaxis.set_minor_formatter(formatter)
					else:
						self._plots[g][component].yaxis.set_minor_formatter(NullFormatter())
			self._UpdateGUI()

	def ShowComponent(self, component, show):
		"""
		Shows or hides the plots of the given component.
		@param component: the name of the component that shall be shown or hidden
		@param show: if True, the component will be shown, otherwise it will be hidden
		"""
		changed = False
		if show:
			if component not in self._shown:
				self._shown.add(component)
				changed = True
		else:
			if component in self._shown:
				if len(self._shown) <= 1:
					raise RuntimeError("It is not possible to hide all plots at once")
				self._shown.discard(component)
				changed = True
		if changed:
			if self._x_data is not None and self._y_data is not None and self._labels is not None:
				self._SetData(self._x_data, self._y_data, self._labels)

	def _CreatePlots(self):
		"""
		Overrides of this method shall create the plots and plot the data in them.
		"""
		raise NotImplementedError("This method should have been overridden in a derived class")

	def _UpdateGUI(self):
		"""
		Updates the GUI by redrawing the plot canvas and updating the toolbar status.
		"""
		sumpf.gui.run_in_mainloop(self.__canvas.draw)
		self.__toolbar.UpdateToolbar(legend=self._show_legend,
		                             grid=self.__show_grid,
		                             cursors=self.__show_cursors,
		                             logx=self.__logx,
		                             logy=self.__logy,
		                             shown=self._shown)

