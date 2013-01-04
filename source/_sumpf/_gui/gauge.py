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

import wx
import sumpf


class Gauge(wx.Gauge):
	"""
	An extension to a standard wx.Gauge, so it can be connected to a progress
	indicator. This way, the connection system can automatically update the
	visualization of its progress.
	"""
	@sumpf.Input(tuple)
	def SetProgress(self, progress):
		"""
		This method can be connected to a progress indicator's GetProgressAsTuple
		method, so this Gauge can keep updated about the progress of a processing
		chain's calculation.
		@param progress: a tuple (max, current), where max is the total number of methods, that have to be run and current is the number of those, which have finished
		"""
		if progress[1] == 0:
			self.Pulse()
		else:
			self.SetRange(progress[0])
			self.SetValue(progress[1])

