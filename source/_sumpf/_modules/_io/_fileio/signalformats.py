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

import os

import numpy

import sumpf

try:
	import scikits.audiolab as audiolab
	audiolab_available = True
except ImportError:
	audiolab_available = False

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
			file = audiolab.Sndfile(filename=filename + "." + cls.ending, mode="r")
			frames = file.read_frames(nframes=file.nframes, dtype=numpy.float32)
			channels = tuple(frames.transpose())
			if file.channels == 1:
				channels = (channels,)
			labels = []
			for c in range(file.channels):
				labels.append(" ".join([name, str(c + 1)]))
			return sumpf.Signal(channels=channels, samplingrate=file.samplerate, labels=labels)

		@classmethod
		def Save(cls, filename, data):
			channels = data.GetChannels()
			# this somehow does not work...
#				frames = numpy.array(channels).transpose()
			# ... so we do it this way:
			frames = []
			frame = []
			for c in range(len(channels)):
				for s in range(len(channels[c])):
					frame.append(channels[c][s])
					if len(frame) == len(channels):
						frames.append(frame)
						frame = []
			frames = numpy.array(frames)
			format = audiolab.Format(type=cls.format, encoding=cls.encoding, endianness="file")
			file = audiolab.Sndfile(filename=filename + "." + cls.ending,
			                        mode="w",
			                        format=format,
			                        channels=len(channels),
			                        samplerate=int(round(data.GetSamplingRate())))
			file.write_frames(frames)



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

