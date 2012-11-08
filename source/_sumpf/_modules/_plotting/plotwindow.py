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

import wx
import sumpf


class PlotWindow(object):
	"""
	An abstract base class for windows which display plots.
	Other than the sumpf.gui.Window these windows can be shown again after they
	have been closed.
	"""
	def __init__(self):
		self._window = None
		self._panel = None
		# plot properties
		self.__x_interval = None
		self.__show_grid = None
		self.__show_legend = True
		self.__show_cursors = True
		self.__cursor_positions = []
		self.__log_x = False

	def _GetPanel(self):
		"""
		Abstract method that has to be implemented in derived classes so it
		returns a properly initialized PlotPanel instance.
		@retval : a PlotPanel instance
		"""
		raise NotImplementedError("This method should have been overridden in a derived class")

	@sumpf.Trigger()
	def Show(self):
		"""
		Shows the window.
		"""
		# setup window
		self._window = sumpf.gui.Window(parent=None, id=wx.ID_ANY, title="Plot", size=(800, 600))
		sizer = wx.BoxSizer(wx.VERTICAL)
		self._window.SetSizer(sizer)
		# setup panel
		self._panel = self._GetPanel()
		self._panel.SetXInterval(self.__x_interval)
		if self.__show_grid is None:
			self._panel.ShowMajorGrid()
		elif self.__show_grid:
			self._panel.ShowFullGrid()
		else:
			self._panel.HideGrid()
		if self.__show_legend:
			self._panel.ShowLegend()
		else:
			self._panel.HideLegend()
		self._panel.SetCursors(self.__cursor_positions)
		if self.__show_cursors:
			self._panel.ShowCursors()
		else:
			self._panel.HideCursors()
		if self.__log_x:
			self._panel.LogarithmicX()
		else:
			self._panel.LinearX()
		# layout
		sizer.Add(self._panel, 1, wx.EXPAND)
		self._window.Layout()
		# arrange cleanup after closing window
		def reset():
			self._window = None
			self._panel = None
		self._window.AddObserverOnClose(function=reset)
		# and finally:
		self._window.Show()

	@sumpf.Trigger()
	def Close(self):
		"""
		Closes the window.
		"""
		if self._window is not None:
			self._window.Close()

	@sumpf.Trigger()
	def Join(self):
		"""
		Blocks as long as the window is shown.
		"""
		if self._window is not None:
			self._window.Join()

	@sumpf.Input(tuple)
	def SetXInterval(self, interval):
		"""
		Sets the interval on the x axis, which part of the plot is visible.
		@param interval: a tuple (min, max) of the visible interval on the x axis, or None to set interval automatically
		"""
		self.__x_interval = interval
		if self._panel is not None:
			self._panel.SetXInterval(interval)

	@sumpf.Input(int)
	def SetMargin(self, margin):
		"""
		Sets the margin between the plots and the panel border.
		@param margin: the margin as integer
		"""
		self.__margin = margin
		if self._panel is not None:
			self._panel.SetMargin(margin)

	@sumpf.Trigger()
	def ShowFullGrid(self):
		"""
		Shows the full grid behind the plots.
		"""
		self.__show_grid = True
		if self._panel is not None:
			self._panel.ShowFullGrid()

	@sumpf.Trigger()
	def ShowMajorGrid(self):
		"""
		Shows the grid only for major numbers.
		"""
		self.__show_grid = None
		if self._panel is not None:
			self._panel.ShowMajorGrid()

	@sumpf.Trigger()
	def HideGrid(self):
		"""
		Hides the grid behind the plots.
		"""
		self.__show_grid = False
		if self._panel is not None:
			self._panel.HideGrid()

	@sumpf.Trigger()
	def ShowLegend(self):
		"""
		Shows a legend in the plot.
		"""
		self.__show_legend = True
		if self._panel is not None:
			self._panel.ShowLegend()

	@sumpf.Trigger()
	def HideLegend(self):
		"""
		Hides the plot's legend.
		"""
		self.__show_legend = False
		if self._panel is not None:
			self._panel.HideLegend()

	@sumpf.Trigger()
	def ShowCursors(self):
		"""
		Shows the cursors in the plots.
		In this case, "cursors" does not mean the mouse cursor, but a vertical
		line, that indicates a position on the x-Axis.
		"""
		self.__show_cursors = True
		if self._panel is not None:
			self._panel.ShowCursors()

	@sumpf.Trigger()
	def HideCursors(self):
		"""
		Hides the cursors in the plots.
		In this case, "cursors" does not mean the mouse cursor, but a vertical
		line, that indicates a position on the x-Axis.
		"""
		self.__show_cursors = False
		if self._panel is not None:
			self._panel.HideCursors()

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
		if self._panel is not None:
			self._panel.SetCursors(self.__cursor_positions)


	@sumpf.Trigger()
	def LinearX(self):
		"""
		Shows the x axis linearly
		"""
		self.__log_x = False
		if self._panel is not None:
			self._panel.LinearX()

	@sumpf.Trigger()
	def LogarithmicX(self):
		"""
		Shows the x axis logarithmically
		"""
		self.__log_x = True
		if self._panel is not None:
			self._panel.LogarithmicX()

