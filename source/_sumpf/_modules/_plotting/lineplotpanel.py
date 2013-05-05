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
from .baselineplotpanel import BaseLinePlotPanel


class LinePlotPanel(BaseLinePlotPanel):
	"""
	A plot panel that shows one plot for each component of the input data. All
	added input data sets are plotted in the same plots.
	"""
	def _CreatePlots(self):
		"""
		Creates the necessary plots.
		"""
		number_of_shown_components = len(set(self._components) & set(self._shown))
		width = 1.0 - 2.0 * self._margin
		height = (1.0 - self._margin) / number_of_shown_components - self._margin / 2.0
		lastcomponent = None
		self._plots["main"] = {}
		self._y_plotdata["main"] = {}
		for c in self._components:
			if c in self._shown:
				left = self._margin
				bottom = self._margin + (number_of_shown_components - 1.0) * (height + self._margin / 2.0)
				number_of_shown_components -= 1
				plot = sumpf.gui.run_in_mainloop(self._figure.add_axes, [left, bottom, width, height])
				self._plots["main"][c] = plot
				self._y_plotdata["main"][c] = []
				for i in range(len(self._y_data[c])):
					linename = self._labels[i]
					if linename is None:
						linename = "Channel " + str(i + 1)
					plot.plot(self._x_data, self._y_data[c][i], label=linename)
					self._y_plotdata["main"][c].append(self._y_data[c][i])
				plot.set_ylabel(c)
				lastcomponent = c
		self._plots["main"][lastcomponent].set_xlabel(self._x_caption)

