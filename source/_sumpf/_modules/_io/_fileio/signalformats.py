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

import os
import numpy
import sumpf

try:
	import scikits.audiolab as audiolab
	audiolab_available = True
except ImportError:
	audiolab_available = False

try:
	import oct2py
	import inspect
	oct2py_available = True
except ImportError:
	oct2py_available = False

from .fileformat import FileFormat

signalformats = []


class NUMPY_NPZ(FileFormat):
	"""
	File format class for the numpy npz-format for Signals.
	http://docs.scipy.org/doc/numpy/reference/generated/numpy.savez.html
	"""
	ending = "npz"

	@classmethod
	def Load(cls, filename):
		data = numpy.load(filename + "." + cls.ending)
		channels = []
		for c in data["channels"]:
			channels.append(tuple(c))
		return sumpf.Signal(channels=channels, samplingrate=data["samplingrate"], labels=data["labels"])

	@classmethod
	def Save(cls, filename, data):
		numpy.savez(filename + "." + cls.ending,
		            channels=data.GetChannels(),
		            samplingrate=data.GetSamplingRate(),
		            labels=data.GetLabels())

signalformats.insert(0, NUMPY_NPZ)	# Make NUMPY_NPZ the default format, if no other format is available



if audiolab_available:
	class AudioLabFileFormat(FileFormat):
		"""
		An abstract base class for file formats that are available through
		the scikits.audiolab module.
		"""
		format = None
		encoding = None

		@classmethod
		def Load(cls, filename):
			name = filename.split(os.sep)[-1]
			soundfile = audiolab.Sndfile(filename=filename + "." + cls.ending, mode="r")
			frames = soundfile.read_frames(nframes=soundfile.nframes, dtype=numpy.float64)
			channels = tuple(frames.transpose())
			if soundfile.channels == 1:
				channels = (channels,)
			labels = []
			for c in range(soundfile.channels):
				labels.append(str(" ".join([name, str(c + 1)])))
			return sumpf.Signal(channels=channels, samplingrate=soundfile.samplerate, labels=labels)

		@classmethod
		def Save(cls, filename, data):
			channels = data.GetChannels()
			frames = numpy.array(channels).transpose()
			fileformat = audiolab.Format(type=cls.format, encoding=cls.encoding, endianness="file")
			soundfile = audiolab.Sndfile(filename=filename + "." + cls.ending,
			                        mode="w",
			                        format=fileformat,
			                        channels=len(channels),
			                        samplerate=int(round(data.GetSamplingRate())))
			soundfile.write_frames(frames)



	class AIFF_FLOAT(AudioLabFileFormat):
		"""
		File format class for the Apple aiff format.
		This one uses 32bit float samples.
		"""
		ending = "aif"
		format = "aiff"
		encoding = "float32"

	signalformats.append(AIFF_FLOAT)



	class AIFF_INT(AudioLabFileFormat):
		"""
		File format class for the Apple aiff format.
		This one uses 24bit integer samples.
		"""
		ending = "aif"
		format = "aiff"
		encoding = "pcm24"

	signalformats.append(AIFF_INT)



	class FLAC(AudioLabFileFormat):
		"""
		File format class for the flac format.
		This one uses 24bit integer samples.
		"""
		ending = "flac"
		format = "flac"
		encoding = "pcm24"

	signalformats.append(FLAC)



	class WAV_FLOAT(AudioLabFileFormat):
		"""
		File format class for the wav format.
		This one uses 32bit float samples.
		"""
		ending = "wav"
		format = "wav"
		encoding = "float32"

	signalformats.insert(0, WAV_FLOAT)	# make WAV_FLOAT the default format



	class WAV_INT(AudioLabFileFormat):
		"""
		File format class for the wav format.
		This one uses 24bit integer samples.
		"""
		ending = "wav"
		format = "wav"
		encoding = "pcm24"

	signalformats.append(WAV_INT)



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
			# transform to the time domain, if necessary
			if domain == "time":
				return sumpf.Signal(channels=channels, samplingrate=samplingrate, labels=labels)
			elif domain == "freq":
				spectrum = sumpf.Spectrum(channels=channels,
				                          resolution=sumpf.modules.ChannelDataProperties(spectrum_length=len(channels[0]), samplingrate=samplingrate).GetResolution(),
				                          labels=labels)
				return sumpf.modules.InverseFourierTransform(spectrum=spectrum).GetSignal()
			else:
				raise RuntimeError("Unknown domain: %s" % domain)

	signalformats.append(ITA_AUDIO)

