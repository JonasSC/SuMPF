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

import math
from .baselineplotpanel import BaseLinePlotPanel


class TiledLinePlotPanel(BaseLinePlotPanel):
	"""
	A plot panel that shows one plot for each line that is added to the plot.
	The plots will be arranged in a grid-like way. The orientation of the grid
	can be specified with the orientation parameter.
	"""
	HORIZONTAL = 1
	VERTICAL = 2

	def __init__(self, parent, components, orientation, x_caption, x_interval, margin, show_legend, show_grid, show_cursors, cursor_positions, log_x, log_y, hidden_components):
		"""
		@param parent: the parent wx.Window of this panel
		@param components: a list of the names of the data's components (e.g. "Magnitude", "Phase" or "x", "y", "z")
		@param orientation: either HORIZONTAL or VERTICAL to specify whether the plot grid shall expand more horizontally or vertically
		@param x_caption: a string containing the caption for the x axis
		@param x_interval: a tuple (min, max) of the visible interval on the x axis, or None to set interval automatically
		@param margin: the margin between the plots and the window border
		@param show_legend: a boolean value whether to show the legend (True) or not (False)
		@param show_grid: True to show full grid behind plots, None to show major grid, False to hide grid
		@param show_cursors: a boolean value whether to show cursors in the plot (True) or not (False). Cursors are vertical lines to indicate x-Axis values, not a mouse cursor
		@param cursor_positions: a list of x-Axis values, where a cursor shall be drawn.
		@param log_x: a boolean value whether to show the x axis logarithmically (True) or linearly (False)
		@param log_y: a set of plot names whose plots shall be plotted with logarithmic y axis rather than linear
		@param hidden_components: a set of component names whose plots shall be hidden
		"""
		BaseLinePlotPanel.__init__(self,
		                           parent=parent,
		                           components=components,
		                           x_caption=x_caption,
		                           x_interval=x_interval,
		                           margin=margin,
		                           show_legend=show_legend,
		                           show_grid=show_grid,
		                           show_cursors=show_cursors,
		                           cursor_positions=cursor_positions,
		                           log_x=log_x,
		                           log_y=log_y,
		                           hidden_components=hidden_components)
		self.__orientation = orientation

	def _CreatePlots(self):
		"""
		Creates the necessary plots.
		"""
		number_of_shown_components = len(set(self._components) & set(self._shown))
		# determine number of rows and columns and tile dimensions
		number_of_plots = len(self._y_data.values()[0])
		cols = int(math.ceil(number_of_plots ** 0.5))
		rows = int(math.ceil(number_of_plots / float(cols)))
		if self.__orientation == TiledLinePlotPanel.VERTICAL:
			tmp = cols
			cols = rows
			rows = tmp
		width = (1.0 - self._margin) / float(cols) - self._margin
		height = (1.0 - self._margin) / float(rows) - self._margin
		subheight = height / number_of_shown_components
		# create the plots
		for i in range(len(self._y_data.values()[0])):
			left = self._margin + (i % cols) * (width + self._margin)
			bottom = self._margin + (rows - i // cols - 1) * (height + self._margin)
			offset = number_of_shown_components - 1
			linename = self._labels[i]
			if linename is None:
				linename = "Channel %i" % (i + 1)
				a = 0
				while linename in self._plots:
					linename = "Channel %i(%i)" % (i + 1, a)
			self._plots[linename] = {}
			self._y_plotdata[linename] = {}
			lastcomponent = None
			for c in self._components:
				if c in self._shown:
					subbottom = bottom + subheight * offset
					plot = self._figure.add_axes([left, subbottom, width, subheight])
					offset -= 1
					plot.plot(self._x_data, self._y_data[c][i], label=linename)
					plot.get_xaxis().set_visible(False)
					if lastcomponent is not None:
						plot.get_yticklabels()[-1].set_visible(False)
					plot.set_ylabel(c)
					lastcomponent = c
					self._plots[linename][c] = plot
					self._y_plotdata[linename][c] = [self._y_data[c][i]]
			self._plots[linename][lastcomponent].set_xlabel(self._x_caption)
			self._plots[linename][lastcomponent].get_xaxis().set_visible(True)

