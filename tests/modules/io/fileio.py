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

import os
import shutil
import tempfile
import unittest

import sumpf
import _common as common

@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestFileIO(unittest.TestCase):
	"""
	A TestCase for the SignalFile and SpectrumFile modules.
	"""
	@unittest.skipUnless(sumpf.config.get("write_to_disk"), "Tests that write to disk are skipped")
	def test_signal_file(self):
		"""
		Tests if the SignalFile module works as expected.
		"""
		tempdir = tempfile.mkdtemp()
		filename1 = os.path.join(tempdir, "TestFileIO1")
		filename2 = os.path.join(tempdir, "TestFileIO2")
		signal1 = sumpf.Signal(channels=((0.0, 0.1, 0.2, 0.3), (0.4, 0.5, 0.6, 0.7)), samplingrate=23.0, labels=("one", "two"))
		signal2 = sumpf.Signal(channels=((-0.1, -0.2, -0.3), (-0.4, -0.5, -0.6), (-0.7, -0.8, -0.9)), samplingrate=25.0, labels=("three", "four", "five"))
		formats = {}#                                 exact,labels,float samplingrate
		formats[sumpf.modules.SignalFile.NUMPY_NPZ] = (True, True, True)
		if common.lib_available("scikits.audiolab"):
			formats[sumpf.modules.SignalFile.AIFF_FLOAT] = (False, False, False)
			formats[sumpf.modules.SignalFile.AIFF_INT] = (False, False, False)
			formats[sumpf.modules.SignalFile.FLAC] = (False, False, False)
			formats[sumpf.modules.SignalFile.WAV_INT] = (False, False, False)
			formats[sumpf.modules.SignalFile.WAV_FLOAT] = (False, False, False)
		self.assertEqual(set(formats.keys()), set(sumpf.modules.SignalFile.GetFormats()))
		fileio = sumpf.modules.SignalFile(format=list(formats.keys())[0])
		self.assertEqual(os.listdir(tempdir), [])											# if no filename was provided, no file should have been written
		try:
			for f in formats:
				format_info = formats[f]
				filename1e = filename1 + "." + f.ending
				filename2e = filename2 + "." + f.ending
				fileio = sumpf.modules.SignalFile(filename=filename1, format=f)
				self.assertTrue(f.Exists(filename1))										# with a filename provided, a file should have been created
				output = fileio.GetSignal()
				self.__CompareSignals(output, sumpf.Signal(), format_info, "TestFileIO1")	# this file should contain an empty data set
				fileio = sumpf.modules.SignalFile(filename=filename1, signal=signal1, format=f)
				fileio = sumpf.modules.SignalFile(filename=filename1, format=f)
				output = fileio.GetSignal()
				self.__CompareSignals(output, signal1, format_info, "TestFileIO1")			# the existent file should be overwritten when a data set is provided
				fileio.SetSignal(signal2)													# changing the data set should have triggered a rewrite of the file
				fileio = sumpf.modules.SignalFile()
				fileio.SetFilename(filename1)
				fileio.SetFormat(f)
				output = fileio.GetSignal()
				self.__CompareSignals(output, signal2, format_info, "TestFileIO1")			# creating an empty file module and the giving it the filename and the format should have loaded the file into the empty module
				tmpio = sumpf.modules.SignalFile(filename=filename2e, signal=signal1, format=f)
				fileio.SetFilename(filename2e)
				output = fileio.GetSignal()
				self.__CompareSignals(output, signal2, format_info, "TestFileIO2")			# both the constructor and the SetFilename method should have cropped the file ending from the filename
				output = tmpio.GetSignal()
				self.__CompareSignals(output, signal2, format_info, "TestFileIO2")			# both fileio and tmpio have loaded the same file. fileio has changed it, so it should also have changed in tmpio
				os.remove(filename1e)
				os.remove(filename2e)
		finally:
			shutil.rmtree(tempdir)

	def __CompareSignals(self, signal1, signal2, format_info, filename):
		if format_info[0]:
			self.assertEqual(signal1.GetChannels(), signal2.GetChannels())
		else:
			for c in range(len(signal1.GetChannels())):
				for s in range(len(signal1.GetChannels()[c])):
					self.assertAlmostEqual(signal1.GetChannels()[c][s], signal2.GetChannels()[c][s], 6)
		if format_info[2]:
			self.assertEqual(signal1.GetSamplingRate(), signal2.GetSamplingRate())
		else:
			self.assertEqual(signal1.GetSamplingRate(), round(signal2.GetSamplingRate()))
		if format_info[1]:
			self.assertEqual(signal1.GetLabels(), signal2.GetLabels())
		else:
			for l in signal1.GetLabels():
				self.assertTrue(l.startswith(filename))

	@unittest.skipUnless(sumpf.config.get("write_to_disk"), "Tests that write to disk are skipped")
	def test_spectrum_file(self):
		"""
		Tests if the SpectrumFile module works as expected.
		"""
		tempdir = tempfile.mkdtemp()
		filename1 = os.path.join(tempdir, "TestFileIO1")
		filename2 = os.path.join(tempdir, "TestFileIO2")
		spectrum1 = sumpf.Spectrum(channels=((1.1 + 1.4j, 2.0 + 3.0j), (3.0, 4.0)), resolution=23.0, labels=("one", "two"))
		spectrum2 = sumpf.Spectrum(channels=((5.0, 6.0), (7.0, 8.2 + 2.7j)), resolution=25.0, labels=("three", "four"))
		formats = []
		formats.append(sumpf.modules.SpectrumFile.NUMPY_NPZ)
		try:
			for f in formats:
				filename1e = filename1 + "." + f.ending
				filename2e = filename2 + "." + f.ending
				fileio = sumpf.modules.SpectrumFile(format=f)
				self.assertEqual(os.listdir(tempdir), [])										# if no filename was provided, no file should have been written
				fileio = sumpf.modules.SpectrumFile(filename=filename1, format=f)
				self.assertTrue(f.Exists(filename1))											# with a filename provided, a file should have been created
				output = fileio.GetSpectrum()
				self.assertEqual(output.GetChannels(), sumpf.Spectrum().GetChannels())			# this file should contain an empty data set
				self.assertEqual(output.GetResolution(), sumpf.Spectrum().GetResolution())		#
				self.assertEqual(output.GetLabels(), sumpf.Spectrum().GetLabels())				#
				fileio = sumpf.modules.SpectrumFile(filename=filename1, spectrum=spectrum1, format=f)
				fileio = sumpf.modules.SpectrumFile(filename=filename1, format=f)
				output = fileio.GetSpectrum()
				self.assertEqual(output.GetChannels(), spectrum1.GetChannels())					# the existent file should be overwritten when a data set is provided
				self.assertEqual(output.GetResolution(), spectrum1.GetResolution())				# ...and then loaded when no data set, but a filename has been provided
				self.assertEqual(output.GetLabels(), spectrum1.GetLabels())						#
				fileio.SetSpectrum(spectrum2)
				fileio = sumpf.modules.SpectrumFile()
				fileio.SetFilename(filename1)
				fileio.SetFormat(f)
				output = fileio.GetSpectrum()
				self.assertEqual(output.GetChannels(), spectrum2.GetChannels())					# changing the data set should have triggered a rewrite of the file
				self.assertEqual(output.GetResolution(), spectrum2.GetResolution())				# creating an empty file module and the giving it the filename and the format should have loaded the file into the empty module
				self.assertEqual(output.GetLabels(), spectrum2.GetLabels())						#
				tmpio = sumpf.modules.SpectrumFile(filename=filename2e, spectrum=spectrum1, format=f)
				fileio.SetFilename(filename2e)
				output = fileio.GetSpectrum()
				self.assertEqual(output.GetChannels(), spectrum2.GetChannels())					# both the constructor and the SetFilename method should have cropped the file ending from the filename
				self.assertEqual(output.GetResolution(), spectrum2.GetResolution())				#
				self.assertEqual(output.GetLabels(), spectrum2.GetLabels())						#
				output = tmpio.GetSpectrum()
				self.assertEqual(output.GetChannels(), spectrum2.GetChannels())					# both fileio and tmpio have loaded the same file
				self.assertEqual(output.GetResolution(), spectrum2.GetResolution())				# fileio has changed it
				self.assertEqual(output.GetLabels(), spectrum2.GetLabels())						# so it should also have changed in tmpio
				os.remove(filename1e)
				os.remove(filename2e)
		finally:
			shutil.rmtree(tempdir)

	def test_connectors(self):
		"""
		Tests if the connectors are properly decorated.
		This is only a shallow test, so it does not write to the disk.
		"""
		# SignalFile
		sf = sumpf.modules.SignalFile()
		self.assertEqual(sf.SetSignal.GetType(), sumpf.Signal)
		self.assertEqual(sf.SetFilename.GetType(), str)
#		self.assertEqual(sf.SetFormat.GetType(), type(sumpf.modules.SignalFile.GetFormats()[0]))
		self.assertEqual(sf.GetSignal.GetType(), sumpf.Signal)
		self.assertEqual(sf.SetSignal.GetObservers(), [sf.GetSignal])
		self.assertEqual(sf.SetFilename.GetObservers(), [sf.GetSignal])
		self.assertEqual(sf.SetFormat.GetObservers(), [sf.GetSignal])
		# SignalFile
		sf = sumpf.modules.SpectrumFile()
		self.assertEqual(sf.SetSpectrum.GetType(), sumpf.Spectrum)
		self.assertEqual(sf.SetFilename.GetType(), str)
#		self.assertEqual(sf.SetFormat.GetType(), type(sumpf.modules.SpectrumFile.GetFormats()[0]))
		self.assertEqual(sf.GetSpectrum.GetType(), sumpf.Spectrum)
		self.assertEqual(sf.SetSpectrum.GetObservers(), [sf.GetSpectrum])
		self.assertEqual(sf.SetFilename.GetObservers(), [sf.GetSpectrum])
		self.assertEqual(sf.SetFormat.GetObservers(), [sf.GetSpectrum])

