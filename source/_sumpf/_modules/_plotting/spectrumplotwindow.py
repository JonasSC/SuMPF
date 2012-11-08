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
from .plotwindow import PlotWindow


class SpectrumPlotWindow(PlotWindow):
	"""
	A class whose instances create a window in which plots of Spectrums are shown.
	"""
	def __init__(self):
		PlotWindow.__init__(self)
		self.LogarithmicX()
		self.__spectrum = sumpf.Spectrum()
		self.__log_magnitude = True
		self.__log_phase = False
		self.__log_groupdelay = False
		self.__show_magnitude = True
		self.__show_phase = True
		self.__show_groupdelay = False

	def _GetPanel(self):
		"""
		Returns a properly initialized SpectrumPlotPanel.
		@retval : a SpectrumPlotPanel instance
		"""
		panel = sumpf.modules.SpectrumPlotPanel(parent=self._window)
		panel.SetSpectrum(self.__spectrum)
		if self.__log_magnitude:
			panel.LogarithmicMagnitude()
		else:
			panel.LinearMagnitude()
		if self.__log_phase:
			panel.LogarithmicPhase()
		else:
			panel.LinearPhase()
		if self.__log_groupdelay:
			panel.LogarithmicGroupDelay()
		else:
			panel.LinearGroupDelay()
		if self.__show_magnitude:
			panel.ShowMagnitude()
		else:
			panel.HideMagnitude()
		if self.__show_phase:
			panel.ShowPhase()
		else:
			panel.HidePhase()
		if self.__show_groupdelay:
			panel.ShowGroupDelay()
		else:
			panel.HideGroupDelay()
		return panel

	@sumpf.Input(sumpf.Spectrum)
	def SetSpectrum(self, spectrum):
		"""
		Sets the Spectrum which shall be plotted.
		@param spectrum: The Spectrum to plot
		"""
		self.__spectrum = spectrum
		if self._panel is not None:
			self._panel.SetSpectrum(spectrum)

	@sumpf.Trigger()
	def LinearMagnitude(self):
		"""
		Shows the magnitude linearly
		"""
		self.__log_magnitude = False
		if self._panel is not None:
			self._panel.LinearMagnitude()

	@sumpf.Trigger()
	def LogarithmicMagnitude(self):
		"""
		Shows the magnitude logarithmically.
		"""
		self.__log_magnitude = True
		if self._panel is not None:
			self._panel.LogarithmicMagnitude()

	@sumpf.Trigger()
	def LinearPhase(self):
		"""
		Shows the phase linearly.
		"""
		self.__log_phase = False
		if self._panel is not None:
			self._panel.LinearPhase()

	@sumpf.Trigger()
	def LogarithmicPhase(self):
		"""
		Shows the phase logarithmically.
		"""
		self.__log_phase = True
		if self._panel is not None:
			self._panel.LogarithmicPhase()

	@sumpf.Trigger()
	def LinearGroupDelay(self):
		"""
		Shows the group delay linearly.
		"""
		self.__log_groupdelay = False
		if self._panel is not None:
			self._panel.LinearGroupDelay()

	@sumpf.Trigger()
	def LogarithmicGroupDelay(self):
		"""
		Shows the group delay logarithmically.
		"""
		self.__log_groupdelay = True
		if self._panel is not None:
			self._panel.LogarithmicGroupDelay()

	@sumpf.Trigger()
	def ShowMagnitude(self):
		"""
		Shows the magnitude plot.
		"""
		self.__show_magnitude = True
		if self._panel is not None:
			self._panel.ShowMagnitude()

	@sumpf.Trigger()
	def HideMagnitude(self):
		"""
		Hides the magnitude plot.
		"""
		self.__show_magnitude = False
		if self._panel is not None:
			self._panel.HideMagnitude()

	@sumpf.Trigger()
	def ShowPhase(self):
		"""
		Shows the phase plot.
		"""
		self.__show_phase = True
		if self._panel is not None:
			self._panel.ShowPhase()

	@sumpf.Trigger()
	def HidePhase(self):
		"""
		Hides the phase plot.
		"""
		self.__show_phase = False
		if self._panel is not None:
			self._panel.HidePhase()

	@sumpf.Trigger()
	def ShowGroupDelay(self):
		"""
		Shows the group delay plot.
		"""
		self.__show_groupdelay = True
		if self._panel is not None:
			self._panel.ShowGroupDelay()

	@sumpf.Trigger()
	def HideGroupDelay(self):
		"""
		Hides the group delay plot.
		"""
		self.__show_groupdelay = False
		if self._panel is not None:
			self._panel.HideGroupDelay()

