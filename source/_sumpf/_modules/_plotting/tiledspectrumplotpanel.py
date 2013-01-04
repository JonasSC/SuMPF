# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2013 Jonas Schulte-Coerne
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


class TiledSpectrumPlotPanel(TiledLinePlotPanel):
	"""
	A wx Panel that contains a separate plot for each channel of a Spectrum and
	the toolbar for the plots.
	This panel is meant to be integrated into a GUI. If you want a simple plot
	window, consider using SpectrumPlotWindow and give this class as panel_class
	parameter to the constructor.
	"""
	def __init__(self, parent, orientation=TiledLinePlotPanel.HORIZONTAL, x_interval=(20, 20000), margin=0.07, show_legend=False, show_grid=None, show_cursors=True, cursor_positions=[], log_x=True, log_y=set(["Magnitude"]), hidden_components=set(["Phase", "GroupDelay"])):
		"""
		@param parent: the parent wx.Window of this panel
		@param margin: the margin between the plots and the window border
		@param x_interval: a tuple (min, max) of the visible interval on the x axis, or None to set interval automatically
		@param margin: the margin between the plots and the window border
		@param show_legend: a boolean value whether to show the legend (True) or not (False)
		@param show_grid: True to show full grid behind plots, None to show major grid, False to hide grid
		@param log_x: a boolean value whether to show the x axis logarithmically (True) or linearly (False)
		@param log_y: a set of plot names whose plots shall be plotted with logarithmic y axis rather than linear
		@param hidden_components: a set of component names whose plots shall be hidden
		"""
		TiledLinePlotPanel.__init__(self,
		                            parent=parent,
		                            components=["Magnitude", "Phase", "GroupDelay"],
		                            orientation=orientation,
		                            x_caption="Frequency [Hz]",
		                            x_interval=x_interval,
		                            margin=margin,
		                            show_legend=show_legend,
		                            show_grid=show_grid,
		                            show_cursors=show_cursors,
		                            cursor_positions=cursor_positions,
		                            log_x=log_x,
		                            log_y=log_y,
		                            hidden_components=hidden_components)

	@sumpf.Input(sumpf.Spectrum)
	def SetSpectrum(self, spectrum):
		"""
		Sets the Spectrum which shall be plotted.
		@param spectrum: The Spectrum to plot
		"""
		x_data = []
		for i in range(len(spectrum)):
			x_data.append(i * spectrum.GetResolution())
		y_data = {}
		y_data["Magnitude"] = spectrum.GetMagnitude()
		y_data["Phase"] = spectrum.GetPhase()
		y_data["GroupDelay"] = spectrum.GetGroupDelay()
		self._SetData(x_data=x_data, y_data=y_data, labels=spectrum.GetLabels())

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
	def LinearGroupDelay(self):
		"""
		Shows the group delay linearly.
		"""
		self.LogarithmicY(component="GroupDelay", log=False)

	@sumpf.Trigger()
	def LogarithmicGroupDelay(self):
		"""
		Shows the group delay logarithmically.
		"""
		self.LogarithmicY(component="GroupDelay", log=True)

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
	def ShowGroupDelay(self):
		"""
		Shows the group delay plot.
		"""
		self.ShowComponent(component="GroupDelay", show=True)

	@sumpf.Trigger()
	def HideGroupDelay(self):
		"""
		Hides the group delay plot.
		"""
		self.ShowComponent(component="GroupDelay", show=False)

