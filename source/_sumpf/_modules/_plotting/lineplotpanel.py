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


class LinePlotPanel(wx.Panel):
	"""
	A subclass of wx.Panel that encapsulates the matplotlib stuff.
	"""
	def __init__(self, parent, plotnames, x_caption="", x_interval=None, margin=0.1, show_legend=True, show_grid=None, show_cursors=True, cursor_positions=[], log_x=False, log_y=set(), hidden_plots=set()):
		"""
		@param parent: the parent wx.Window of this panel
		@param plotnames: a list of names. For each name a plot will be created
		@param x_caption: a string containing the caption for the x axis
		@param x_interval: a tuple (min, max) of the visible interval on the x axis, or None to set interval automatically
		@param margin: the margin between the plots and the window border
		@param show_legend: a boolean value whether to show the legend (True) or not (False)
		@param show_grid: True to show full grid behind plots, None to show major grid, False to hide grid
		@param show_cursors: a boolean value whether to show cursors in the plot (True) or not (False). Cursors are vertical lines to indicate x-Axis values, not a mouse cursor
		@param cursor_positions: a list of x-Axis values, where a cursor shall be drawn.
		@param log_x: a boolean value whether to show the x axis logarithmically (True) or linearly (False)
		@param log_y: a set of plot names whose plots shall be plotted with logarithmic y axis rather than linear
		@param hidden_plots: a set of plot names whose plots shall be hidden
		"""
		# initialize Panel
		wx.Panel.__init__(self, parent=parent)
		# store arguments
		self.__plotnames = plotnames
		self.__x_caption = x_caption
		self.__x_interval = x_interval
		self.__margin = margin
		self.__show_legend = show_legend
		self.__show_grid = show_grid
		self.__show_cursors = show_cursors
		self.__cursor_positions = cursor_positions
		self.__logx = log_x
		self.__logy = set(log_y)
		self.__shown = set(plotnames) - set(hidden_plots)
		# store other stuff
		self.__plots = {}
		self.__has_data = False
		def dBlabel(y, pos):
			spl = 20.0 * math.log(y, 10)
			return "%.1f dB" % spl
		self.__ytick_linformatter = ScalarFormatter()
		self.__ytick_logformatter = FuncFormatter(dBlabel)
		# wx stuff
		self.__sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.__sizer)
		# matplotlib stuff
		self.__figure = Figure()
		self.__canvas = FigureCanvas(parent=self, id=wx.ID_ANY, figure=self.__figure)
		self.__toolbar = Toolbar(parent=self, canvas=self.__canvas, plots=plotnames)
		self.__sizer.Add(self.__toolbar, 0, wx.LEFT | wx.EXPAND)
		self.__sizer.Add(self.__canvas, 1, wx.EXPAND)
		self.__CreatePlots()
		# data
		self.__x_data = None
		self.__y_data = None
		self.__labels = None

	def Layout(self):
		"""
		Runs the layout algorithm and draws the plots.
		"""
		wx.Panel.Layout(self)
		self.__UpdateGUI()

	def _SetData(self, x_data, y_data, labels):
		"""
		Sets the data for the plot.
		@param x_data: A tuple of x-axis values
		@param y_data: A dictionary which maps captions to tuples of channels where a channel is a tuple of samples
		@param labels: a tuple of labels, one for each channel. A label can be either a string or None
		"""
		self.__Clear()
		for n in self.__plotnames:
			if n in self.__shown:
				for i in range(len(y_data[n])):
					linename = labels[i]
					if linename is None:
						linename = "Channel " + str(i + 1)
					self.__AddLine(plotname=n, linename=linename, xdata=x_data, ydata=y_data[n][i])
				for c in self.__cursor_positions:
					self.__plots[n].axvline(x=c, color='k', linestyle='--')
		if self.__show_legend:
			self.ShowLegend()
		else:
			self.__UpdateGUI()
		if self.__logx:
			self.LogarithmicX()
		for p in self.__logy:
			self.LogarithmicY(plot=p, log=True)
		self.__x_data = x_data
		self.__y_data = y_data
		self.__labels = labels

	def __AddLine(self, plotname, linename, xdata, ydata):
		"""
		Adds a line to a plot.
		@param plotname: the name of the plot to which the line shall be added
		@param linename: the name of the line in the plot's legend
		@param xdata: a tuple of x axis values
		@param ydata: a tuple of y axis values
		"""
		self.__plots[plotname].plot(xdata, ydata, label=linename)
		if tuple(numpy.nonzero(xdata)[0]) != () and\
		   tuple(numpy.nonzero(ydata)[0]) != ():
			self.__has_data = True

	def __Clear(self):
		"""
		Deletes all plot lines from the plot.
		"""
		self.__has_data = False
		for p in list(self.__plots.values()):
			self.__figure.delaxes(p)
			del p.lines[:]
		self.__figure.clear()
		self.__CreatePlots()
		self.__UpdateGUI()

	@sumpf.Input(tuple)
	def SetXInterval(self, interval):
		"""
		Sets the interval on the x axis, which part of the plot is visible.
		@param interval: a tuple (min, max) of the visible interval on the x axis, or None to set interval automatically
		"""
		self.__x_interval = interval
		for p in list(self.__plots.values()):
			if interval is None:
				p.set_xlim(auto=True)
			else:
				p.set_xlim(left=interval[0], right=interval[1])
		self.__UpdateGUI()

	@sumpf.Input(int)
	def SetMargin(self, margin):
		"""
		Sets the margin between the plots and the panel border.
		@param margin: the margin as integer
		"""
		self.__margin = margin
		self.__Clear()
		if self.__x_data is not None and self.__y_data is not None and self.__labels is not None:
			self._SetData(self.__x_data, self.__y_data, self.__labels)

	@sumpf.Trigger()
	def ShowFullGrid(self):
		"""
		Shows the full grid behind the plots.
		"""
		self.__show_grid = True
		for p in self.__plots:
			def showfullgrid():
				self.__plots[p].grid(b=True, which="both")
				if p in self.__logy:
					self.__plots[p].yaxis.set_major_formatter(self.__ytick_logformatter)
					self.__plots[p].yaxis.set_minor_formatter(self.__ytick_logformatter)
				else:
					self.__plots[p].yaxis.set_major_formatter(self.__ytick_linformatter)
					self.__plots[p].yaxis.set_minor_formatter(self.__ytick_linformatter)
			sumpf.gui.run_in_mainloop(showfullgrid)
		self.__UpdateGUI()

	@sumpf.Trigger()
	def ShowMajorGrid(self):
		"""
		Shows the grid only for major numbers.
		"""
		self.__show_grid = None
		for p in self.__plots:
			self.__plots[p].grid(b=False, which="minor")
			self.__plots[p].grid(b=True, which="major")
			if p in self.__logy:
				self.__plots[p].yaxis.set_major_formatter(self.__ytick_logformatter)
			else:
				self.__plots[p].yaxis.set_major_formatter(self.__ytick_linformatter)
			self.__plots[p].yaxis.set_minor_formatter(NullFormatter())
		self.__UpdateGUI()

	@sumpf.Trigger()
	def HideGrid(self):
		"""
		Hides the grid behind the plots.
		"""
		self.__show_grid = False
		for p in self.__plots:
			self.__plots[p].grid(b=False, which="both")
			if p in self.__logy:
				self.__plots[p].yaxis.set_major_formatter(self.__ytick_logformatter)
			else:
				self.__plots[p].yaxis.set_major_formatter(self.__ytick_linformatter)
			self.__plots[p].yaxis.set_minor_formatter(NullFormatter())
		self.__UpdateGUI()

	@sumpf.Trigger()
	def ShowLegend(self):
		"""
		Shows a legend in the plot.
		"""
		self.__show_legend = True
		plot = None
		for n in self.__plotnames:
			if n in self.__shown:
				plot = n
				break
		if plot is not None:
			self.__plots[plot].legend(loc='best')
		self.__UpdateGUI()

	@sumpf.Trigger()
	def HideLegend(self):
		"""
		Hides the plot's legend.
		"""
		self.__show_legend = False
		plot = None
		for n in self.__plotnames:
			if n in self.__shown:
				plot = n
				break
		if plot is not None:
			self.__plots[plot].legend_ = None
		self.__UpdateGUI()

	@sumpf.Trigger()
	def ShowCursors(self):
		"""
		Shows the cursors in the plots.
		In this case, "cursors" does not mean the mouse cursor, but a vertical
		line, that indicates a position on the x-Axis.
		"""
		self.__show_cursors = True
		for p in self.__plots.values():
			for i in range(len(self.__y_data.values()[0]), len(p.lines)):
				p.lines[i].set_visible(True)
		self.__UpdateGUI()

	@sumpf.Trigger()
	def HideCursors(self):
		"""
		Hides the cursors in the plots.
		In this case, "cursors" does not mean the mouse cursor, but a vertical
		line, that indicates a position on the x-Axis.
		"""
		self.__show_cursors = False
		for p in self.__plots.values():
			for i in range(len(self.__y_data.values()[0]), len(p.lines)):
				p.lines[i].set_visible(False)
		self.__UpdateGUI()

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
		for p in self.__plots.values():
			# update existing cursors
			for i in range(len(self.__y_data.values()[0]), min(len(p.lines), len(self.__y_data.values()[0]) + len(self.__cursor_positions))):
				p.lines[i].set_xdata([self.__cursor_positions[i - len(self.__y_data.values()[0])], self.__cursor_positions[i - len(self.__y_data.values()[0])]])
			# delete surplus cursors, if needed
			del p.lines[len(self.__y_data.values()[0]) + len(self.__cursor_positions):]
			# create new cursors, if needed
			for i in range(len(p.lines), len(self.__y_data.values()[0]) + len(self.__cursor_positions)):
				l = p.axvline(x=self.__cursor_positions[i - len(self.__y_data.values()[0])], color='k', linestyle='--')
				if not self.__show_cursors:
					l.set_visible(False)
		self.__UpdateGUI()

	@sumpf.Trigger()
	def LinearX(self):
		"""
		Shows the x axis linearly
		"""
		self.__logx = False
		if self.__has_data:
			for p in list(self.__plots.values()):
				p.set_xscale("linear")
		self.__UpdateGUI()

	@sumpf.Trigger()
	def LogarithmicX(self):
		"""
		Shows the x axis logarithmically
		"""
		self.__logx = True
		if self.__has_data:
			for p in list(self.__plots.values()):
				p.set_xscale("log")
		self.__UpdateGUI()

	def LogarithmicY(self, plot, log):
		"""
		Shows the y axis of the given plot logarithmically or linearly.
		Other than LinearX and LogarithmicX methods there should be a facade for
		this method in a derived class.
		@param plot: the name of the plot that shall be changed
		@param log: if True, the plot will be plotted logarithmically, otherwise linearly
		"""
		if plot in self.__shown:
			scale = "linear"
			formatter = self.__ytick_linformatter
			if log:
				self.__logy.add(plot)
				scale = "log"
				formatter = self.__ytick_logformatter
			else:
				self.__logy.discard(plot)
				self.__ytick_formatter = ScalarFormatter()
			if self.__has_data:
				self.__plots[plot].set_yscale(scale)
				self.__plots[plot].yaxis.set_major_formatter(formatter)
				if bool(self.__show_grid):
					self.__plots[plot].yaxis.set_minor_formatter(formatter)
				else:
					self.__plots[plot].yaxis.set_minor_formatter(NullFormatter())
			self.__UpdateGUI()

	def ShowPlot(self, plot, show):
		"""
		Shows or hides the given plot.
		@param plot: the name of the plot that shall be changed
		@param show: if True, the plot will be shown, otherwise it will be hidden
		"""
		changed = False
		if show:
			if plot not in self.__shown:
				self.__shown.add(plot)
				changed = True
		else:
			if plot in self.__shown:
				if len(self.__shown) <= 1:
					raise RuntimeError("It is not possible to hide all plots at once")
				self.__shown.discard(plot)
				changed = True
		if changed:
			self.__Clear()
			if self.__x_data is not None and self.__y_data is not None and self.__labels is not None:
				self._SetData(self.__x_data, self.__y_data, self.__labels)

	def __CreatePlots(self):
		"""
		Creates the necessary empty plots.
		"""
		self.__plots = {}
		shown_plots = []
		for n in self.__plotnames:
			if n in self.__shown:
				shown_plots.append(n)
		for i in range(len(shown_plots)):
			width = 1 - 2 * self.__margin
			height = (1 - self.__margin) / len(shown_plots) - self.__margin / 2
			left = self.__margin
			bottom = self.__margin + (len(shown_plots) - i - 1) * (height + self.__margin / 2)
			plot = self.__figure.add_axes([left, bottom, width, height])
			if self.__x_interval is not None:
				plot.set_xlim(self.__x_interval[0], self.__x_interval[1])
			plot.set_ylabel(shown_plots[i])
			plot.grid(b=True, which="major")
			self.__plots[shown_plots[i]] = plot
		self.__plots[shown_plots[-1]].set_xlabel(self.__x_caption)

	def __UpdateGUI(self):
		"""
		Updates the GUI by redrawing the plot canvas and updating the toolbar status.
		"""
		sumpf.gui.run_in_mainloop(self.__canvas.draw)
		self.__toolbar.UpdateToolbar(legend=self.__show_legend,
		                             grid=self.__show_grid,
		                             cursors=self.__show_cursors,
		                             logx=self.__logx,
		                             logy=self.__logy,
		                             shown=self.__shown)

