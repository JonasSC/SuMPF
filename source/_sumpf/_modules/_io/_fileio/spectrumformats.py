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

import numpy
import sumpf
from .fileformat import FileFormat

try:
	import oct2py
	import inspect
	import os
	oct2py_available = True
except ImportError:
	oct2py_available = False

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



if oct2py_available:
	class ITA_AUDIO(FileFormat):
		"""
		File format class for the format used by the ITA-Toolbox from the Institute
		of Technical Acoustics, RWTH Aachen University.
		http://www.ita-toolbox.org
		This class can only read itaAudio files. Writing is not possible.
		"""
		ending = "ita"
		read_only = True

		@classmethod
		def Load(cls, filename):
			# retrieve the Matlab data through octave
			path_of_this_file = sumpf.helper.normalize_path(inspect.getfile(inspect.currentframe()))
			read_ita_file = os.sep.join(path_of_this_file.split(os.sep)[0:-1] + ["read_ita_file.m"])
			filename = "%s.%s" % (filename, cls.ending)
			samples, samplingrate, domain, names, units = oct2py.octave.call(read_ita_file, filename)
			channels = tuple(numpy.transpose(samples))
			# create channel labels
			labels = []
			for i in range(len(names)):
				if i < len(units):
					labels.append(str("%s [%s]" % (names[i], units[i])))
				else:
					labels.append(str(names[i]))
			# transform to the frequency domain, if necessary
			if domain == "freq":
				return sumpf.Spectrum(channels=channels,
				                      resolution=sumpf.modules.ChannelDataProperties(spectrum_length=len(channels[0]), samplingrate=samplingrate).GetResolution(),
				                      labels=labels)
			elif domain == "time":
				signal = sumpf.Signal(channels=channels, samplingrate=samplingrate, labels=labels)
				return sumpf.modules.FourierTransform(signal=signal).GetSpectrum()
			else:
				raise RuntimeError("Unknown domain: %s" % domain)

	spectrumformats.append(ITA_AUDIO)

