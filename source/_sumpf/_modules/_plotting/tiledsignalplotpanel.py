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

import sumpf
from .tiledlineplotpanel import TiledLinePlotPanel


class TiledSignalPlotPanel(TiledLinePlotPanel):
	"""
	A wx Panel that contains a separate plot for each channel of a Signal and the
	toolbar for the plots.
	This panel is meant to be integrated into a GUI. If you want a simple plot
	window, consider using SignalPlotWindow, although that will plot all channels
	in one plot.
	"""
	def __init__(self, parent, orientation=TiledLinePlotPanel.HORIZONTAL, x_interval=None, margin=0.07, show_legend=False, show_grid=None, show_cursors=True, cursor_positions=[], log_x=False, log_y=False):
		"""
		@param parent: the parent wx.Window of this panel
		@param x_interval: a tuple (min, max) of the visible interval on the x axis, or None to set interval automatically
		@param margin: the margin between the plots and the window border
		@param show_legend: a boolean value whether to show the legend (True) or not (False)
		@param show_grid: True to show full grid behind plots, None to show major grid, False to hide grid
		@param log_x: a boolean value whether to show the x axis logarithmically (True) or linearly (False)
		@param log_y: True if the Signal shall be plotted with logarithmically scaled y axis, False otherwise
		"""
		log_plots = set()
		if log_y:
			log_plots = set(["Signal"])
		TiledLinePlotPanel.__init__(self,
		                            parent,
		                            components=["Signal"],
		                            orientation=orientation,
		                            x_caption="Time [s]",
		                            x_interval=x_interval,
		                            margin=margin,
		                            show_legend=show_legend,
		                            show_grid=show_grid,
		                            show_cursors=show_cursors,
		                            cursor_positions=cursor_positions,
		                            log_x=log_x,
		                            log_y=log_plots,
		                            hidden_components=set())

	@sumpf.Input(sumpf.Signal)
	def SetSignal(self, signal):
		"""
		Sets the Signal which shall be plotted.
		@param signal: The Signal to plot
		"""
		x_data = []
		for i in range(len(signal)):
			x_data.append(i / signal.GetSamplingRate())
		y_data = {}
		y_data["Signal"] = signal.GetChannels()
		self._SetData(x_data=x_data, y_data=y_data, labels=signal.GetLabels())

	@sumpf.Trigger()
	def LinearY(self):
		"""
		Shows the y axis linearly.
		"""
		TiledLinePlotPanel.LogarithmicY(self, component="Signal", log=False)

	@sumpf.Trigger()
	def LogarithmicY(self, component="Signal", log=True):
		"""
		Shows the y axis logarithmically.
		"""
		TiledLinePlotPanel.LogarithmicY(self, component=component, log=log)

