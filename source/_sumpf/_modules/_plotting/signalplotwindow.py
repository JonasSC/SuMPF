# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2014 Jonas Schulte-Coerne
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
from .plotwindow import PlotWindow
from .signalplotpanel import SignalPlotPanel


class SignalPlotWindow(PlotWindow):
	"""
	A class whose instances create a window in which plots of Signals are shown.
	By default, it plots all channels of the given Signal in one plot. It is however
	possible to supply a different plot panel class, that plots each channel in
	a separate plot.
	"""
	def __init__(self):
		"""
		@param panel_class: a plot panel like sumpf.modules.SignalPlotPanel or sumpf.modules.TiledSignalPlotPanel
		"""
		PlotWindow.__init__(self)
		self.__signal = sumpf.Signal()
		self.__log_y = False

	def _GetPanel(self):
		"""
		Returns a properly initialized plot panel instance.
		@retval : a plot panel instance
		"""
		panel = SignalPlotPanel(parent=self._window)
		panel.SetSignal(self.__signal)
		if self.__log_y:
			panel.LogarithmicY()
		else:
			panel.LinearY()
		return panel

	@sumpf.Input(sumpf.Signal)
	def SetSignal(self, signal):
		"""
		Sets the Signal which shall be plotted.
		@param signal: The Signal to plot
		"""
		self.__signal = signal
		if self._panel is not None:
			self._panel.SetSignal(signal)

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

