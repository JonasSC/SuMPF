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

import numpy

import sumpf

from .fileformat import FileFormat

spectrumformats = []


class NUMPY_NPZ(FileFormat):
	"""
	File format class for the numpy npz-format for Spectrums.
	http://docs.scipy.org/doc/numpy/reference/generated/numpy.savez.html
	"""
	ending = "npz"
	@classmethod
	def Load(cls, filename):
		data = numpy.load(filename + "." + cls.ending)
		channels = []
		for c in data["channels"]:
			channels.append(tuple(c))
		return sumpf.Spectrum(channels=channels, resolution=data["resolution"], labels=data["labels"])
	@classmethod
	def Save(cls, filename, data):
		numpy.savez(filename + "." + cls.ending,
		            channels=data.GetChannels(),
		            resolution=data.GetResolution(),
		            labels=data.GetLabels())

spectrumformats.append(NUMPY_NPZ)

