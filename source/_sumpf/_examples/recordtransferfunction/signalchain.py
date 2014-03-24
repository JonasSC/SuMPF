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


class SignalChain(object):
	def __init__(self):
		"""
		Sets up the chain of SuMPF modules.
		"""
		#             PROPERTIES <=========#---+      self.__properties
		#           / / /  |  \ \          |   |
		#          / / /   |   \ DURATION  |   |      self.__silence_duration
		#         / / /    |    \   /      |   |
		#        / / /     |   SILENCE     |   |      self.__silence
		#       / / /  DURATION     |      |   |      self.__sweep_duration
		#      / / /     /   \      |      |   |
		#     / /  +> SWEEP   \     |      |   |      self.__generator
		#    /  |      |    WINDOW  |      |   |      self.__fade_sweep
		#   /   |       \    /      |      |   |
		#  /    |      MULTIPLY    /       |   |      self.__apply_fade
		#  |    |     AMPLIFIER   /        |   |      self.__amplifier
		#  |    |          \     /         |   |
		#  |    |      CONCATENATION-------+   |      self.__concatenation
		#  |    |         /       \            |
		#  |    |       FFT        \           |      self.__playback_fft
		#  |    |       / \  +-> AUDIO IO------+      self.__audio_io
		#  |    |      /   \ +---AVERAGE              self.__average
		#  |    |      |    \     FFT                 self.__record_fft
		#  |    | REGULARIZE \   /  |                 self.__regularization
		#  |    |       \   o \ o  /
		#  |    |        \ /   DIVIDE                 self.__divide
		#  |    |     MULTIPLY   |                    self.__multiply
		#  |    |          \    /
		#  |    |          SELECT                     self.__select_regularization
		#  |    |          RELABEL                    self.__relabel
		#  |    |           MERGE --------> Plot      self.__merge_utf
		#  |    |           /    \+-------> Save
		#  |    |          /      +<------- Load
		#  |    |        IFFT                         self.__ifft
		#  |    |     +- MERGE ----+------> Plot      self.__merge_uir
		#  |    |     |   / \ \    +------> Save
		#  |    |     |  |   | |   +<------ Load
		#  |  WINDOW  |  |   | |                      self.__window
		#  |   COPY <-+  |   | |                      self.__copy_window
		#  |     \    |  |   | |
		#  |  +-o \ o-+  |   | |
		#  |  |    \    /    | |
		#  |   \  MULTIPLY   | |                      self.__apply_window
		#  |    \      \    /  |
		#   \    \     SELECT  |                      self.__bypass_window
		#    \    \     FFT    |                      self.__last_fft
		#  FILTER  |    | |    |                      self.__filter
		#   COPY <-+    | |    |                      self.__copy_filter
		#     \        /  |    |
		#      MULTIPLY   |    |                      self.__apply_filter
		#           \    /     |
		#           SELECT     |                      self.__bypass_filter
		#          KEEPLABEL <-+                      self.__keeplabel
		#         /    |    \
		#   NORMALIZE  |     |                        self.__normalize_avg
		#       | NORMALIZE  |                        self.__normalize_frq
		#       \    /      /
		#       SELECT     /                          self.__select_normalization
		#          \      /
		#           SELECT                            self.__bypass_normalize
		#           MERGE ----------------> Plot      self.__merge_ptf
		#             |  \+---------------> Save
		#             |   +<--------------- Load
		#            IFFT                             self.__last_ifft
		#           MERGE ----------------> Plot      self.__merge_pir
		#                \+---------------> Save
		#                 +<--------------- Load
		#
		# properties
		self.__properties = sumpf.modules.ChannelDataProperties()
		self.__silence_duration = sumpf.modules.DurationToLength(even_length=True)
		sumpf.connect(self.__properties.GetSamplingRate, self.__silence_duration.SetSamplingRate)
		self.__silence = sumpf.modules.SilenceGenerator()
		sumpf.connect(self.__silence_duration.GetLength, self.__silence.SetLength)
		sumpf.connect(self.__properties.GetSamplingRate, self.__silence.SetSamplingRate)
		self.__sweep_duration = sumpf.modules.DurationToLength(even_length=True)
		sumpf.connect(self.__properties.GetSamplingRate, self.__sweep_duration.SetSamplingRate)
		self.__generator = sumpf.modules.SweepGenerator()
		sumpf.connect(self.__sweep_duration.GetLength, self.__generator.SetLength)
		sumpf.connect(self.__properties.GetSamplingRate, self.__generator.SetSamplingRate)
		self.__fade_sweep = sumpf.modules.WindowGenerator()
		sumpf.connect(self.__sweep_duration.GetLength, self.__fade_sweep.SetLength)
		sumpf.connect(self.__properties.GetSamplingRate, self.__fade_sweep.SetSamplingRate)
		self.__apply_fade = sumpf.modules.MultiplySignals()
		sumpf.connect(self.__generator.GetSignal, self.__apply_fade.SetInput1)
		sumpf.connect(self.__fade_sweep.GetSignal, self.__apply_fade.SetInput2)
		self.__amplifier = sumpf.modules.AmplifySignal()
		sumpf.connect(self.__apply_fade.GetOutput, self.__amplifier.SetInput)
		# recording
		self.__concatenation = sumpf.modules.ConcatenateSignals()
		sumpf.connect(self.__amplifier.GetOutput, self.__concatenation.SetInput1)
		sumpf.connect(self.__silence.GetSignal, self.__concatenation.SetInput2)
		sumpf.connect(self.__concatenation.GetOutputLength, self.__properties.SetSignalLength)
		self.__playback_fft = sumpf.modules.FourierTransform()
		sumpf.connect(self.__concatenation.GetOutput, self.__playback_fft.SetSignal)
		self.__audio_io = sumpf.modules.audioio.factory(playbackchannels=1, recordchannels=1)
		sumpf.connect(self.__audio_io.GetSamplingRate, self.__properties.SetSamplingRate)
		sumpf.connect(self.__concatenation.GetOutput, self.__audio_io.SetPlaybackSignal)
		self.__average = sumpf.modules.AverageSignals()
		sumpf.connect(self.__audio_io.GetRecordedSignal, self.__average.AddInput)
		sumpf.connect(self.__average.TriggerDataCreation, self.__audio_io.Start)
		self.__record_fft = sumpf.modules.FourierTransform()
		sumpf.connect(self.__average.GetOutput, self.__record_fft.SetSignal)
		# calculate the excitation out of the recorded Signal
		self.__regularization = sumpf.modules.RegularizedSpectrumInversion(start_frequency=20.0,
		                                                                   stop_frequency=20000.0,
		                                                                   transition_length=int(round(20 * self.__properties.GetResolution())),
		                                                                   epsilon_max=0.1)
		sumpf.connect(self.__playback_fft.GetSpectrum, self.__regularization.SetSpectrum)
		self.__divide = sumpf.modules.DivideSpectrums()
		sumpf.connect(self.__record_fft.GetSpectrum, self.__divide.SetInput1)
		sumpf.connect(self.__playback_fft.GetSpectrum, self.__divide.SetInput2)
		self.__multiply = sumpf.modules.MultiplySpectrums()
		sumpf.connect(self.__record_fft.GetSpectrum, self.__multiply.SetInput1)
		sumpf.connect(self.__regularization.GetOutput, self.__multiply.SetInput2)
		self.__select_regularization = sumpf.modules.SelectSpectrum()
		sumpf.connect(self.__multiply.GetOutput, self.__select_regularization.SetInput1)
		sumpf.connect(self.__divide.GetOutput, self.__select_regularization.SetInput2)
		self.__REGULARIZE = 1
		self.__NOT_REGULARIZE = 2
		self.__relabel = sumpf.modules.RelabelSpectrum(labels=("Recent",))
		sumpf.connect(self.__select_regularization.GetOutput, self.__relabel.SetInput)
		# unprocessed data
		self.__merge_utf = sumpf.modules.MergeSpectrums()
		sumpf.connect(self.__relabel.GetOutput, self.__merge_utf.AddInput)
		self.__ifft = sumpf.modules.InverseFourierTransform()
		sumpf.connect(self.__merge_utf.GetOutput, self.__ifft.SetSpectrum)
		self.__merge_uir = sumpf.modules.MergeSignals()
		sumpf.connect(self.__ifft.GetSignal, self.__merge_uir.AddInput)
		# post processing: window
		self.__window = sumpf.modules.WindowGenerator()
		sumpf.connect(self.__properties.GetSignalLength, self.__window.SetLength)
		self.__copy_window = sumpf.modules.CopySignalChannels()
		sumpf.connect(self.__window.GetSignal, self.__copy_window.SetInput)
		sumpf.connect(self.__merge_uir.GetNumberOfOutputChannels, self.__copy_window.SetChannelCount)
		self.__apply_window = sumpf.modules.MultiplySignals()
		sumpf.connect(self.__merge_uir.GetOutput, self.__apply_window.SetInput1)
		sumpf.connect(self.__copy_window.GetOutput, self.__apply_window.SetInput2)
		self.__bypass_window = sumpf.modules.SelectSignal()
		sumpf.connect(self.__bypass_window.SetInput1, self.__merge_uir.GetOutput)
		sumpf.connect(self.__bypass_window.SetInput2, self.__apply_window.GetOutput)
		self.__BYPASS = 1
		self.__WINDOW = 2
		# post processing: filter
		self.__last_fft = sumpf.modules.FourierTransform()
		sumpf.connect(self.__bypass_window.GetOutput, self.__last_fft.SetSignal)
		self.__filter = sumpf.modules.FilterGenerator()
		self.__filter_id = self.__filter.AddFilter(sumpf.modules.FilterGenerator.BUTTERWORTH_LOWPASS(frequency=20000, order=16))
		sumpf.connect(self.__properties.GetSpectrumLength, self.__filter.SetLength)
		sumpf.connect(self.__properties.GetResolution, self.__filter.SetResolution)
		self.__copy_filter = sumpf.modules.CopySpectrumChannels()
		sumpf.connect(self.__filter.GetSpectrum, self.__copy_filter.SetInput)
		sumpf.connect(self.__merge_uir.GetNumberOfOutputChannels, self.__copy_filter.SetChannelCount)
		self.__apply_filter = sumpf.modules.MultiplySpectrums()
		sumpf.connect(self.__last_fft.GetSpectrum, self.__apply_filter.SetInput1)
		sumpf.connect(self.__copy_filter.GetOutput, self.__apply_filter.SetInput2)
		self.__bypass_filter = sumpf.modules.SelectSpectrum()
		sumpf.connect(self.__bypass_filter.SetInput1, self.__last_fft.GetSpectrum)
		sumpf.connect(self.__bypass_filter.SetInput2, self.__apply_filter.GetOutput)
		self.__FILTER = 2
		self.__keeplabel = sumpf.modules.CopyLabelsToSpectrum()
		sumpf.connect(self.__bypass_filter.GetOutput, self.__keeplabel.SetDataInput)
		sumpf.connect(self.__merge_uir.GetOutput, self.__keeplabel.SetLabelInput)
		# post processing: normalization
		self.__normalize_avg = sumpf.modules.NormalizeSpectrumToAverage(order=1)
		sumpf.connect(self.__keeplabel.GetOutput, self.__normalize_avg.SetInput)
		self.__normalize_frq = sumpf.modules.NormalizeSpectrumToFrequency(frequency=1000)
		sumpf.connect(self.__keeplabel.GetOutput, self.__normalize_frq.SetInput)
		self.__select_normalization = sumpf.modules.SelectSpectrum()
		sumpf.connect(self.__normalize_avg.GetOutput, self.__select_normalization.SetInput1)
		sumpf.connect(self.__normalize_frq.GetOutput, self.__select_normalization.SetInput2)
		self.__AVERAGE = 1
		self.__FREQUENCY = 2
		self.__bypass_normalize = sumpf.modules.SelectSpectrum()
		sumpf.connect(self.__bypass_normalize.SetInput1, self.__keeplabel.GetOutput)
		sumpf.connect(self.__bypass_normalize.SetInput2, self.__select_normalization.GetOutput)
		self.__NORMALIZE = 2
		# processed data
		self.__merge_ptf = sumpf.modules.MergeSpectrums()
		sumpf.connect(self.__bypass_normalize.GetOutput, self.__merge_ptf.AddInput)
		self.__last_ifft = sumpf.modules.InverseFourierTransform()
		sumpf.connect(self.__merge_ptf.GetOutput, self.__last_ifft.SetSpectrum)
		self.__merge_pir = sumpf.modules.MergeSignals()
		sumpf.connect(self.__last_ifft.GetSignal, self.__merge_pir.AddInput)
		# make outputs publicly available
		self.GetUnprocessedTransferFunction = self.__merge_utf.GetOutput
		self.GetUnprocessedImpulseResponse = self.__merge_uir.GetOutput
		self.GetProcessedTransferFunction = self.__merge_ptf.GetOutput
		self.GetProcessedImpulseResponse = self.__merge_pir.GetOutput
		self.GetPlaybackPorts = self.__audio_io.GetPlaybackPorts
		self.GetCapturePorts = self.__audio_io.GetCapturePorts
		self.GetSamplingRate = self.__properties.GetSamplingRate
		# initialize other attributes
		self.__kept_ids = []
		self.__loaded_ids_utf = {}
		self.__loaded_ids_uir = {}
		self.__loaded_ids_ptf = {}
		self.__loaded_ids_pir = {}
		self.__showrecent = True
		self.__has_data = False

	def Delete(self):
		self.__audio_io.Delete()

	#########################
	# Data creation methods #
	#########################

	def Start(self, amplitude, sweep_duration, silence_duration, start_frequency, stop_frequency, exponential, fade, averages, capture_port, playback_port):
		"""
		Starts the recording process.
		@param amplitude:
		@param sweep_duration:
		@param silence_duration:
		@param start_frequency:
		@param stop_frequency:
		@param exponential:
		@param fade: a time in seconds as a float, that specifies the length of the fade in and fade out of the sweep
		@param averages:
		@param capture_port: the name of the other program's capture port
		@param playback_port: the name of the other program's playback port
		"""
		self.__has_data = True
		# deactivate modules
		sumpf.deactivate_output(self.__divide.GetOutput)
		sumpf.deactivate_output(self.__concatenation)
		sumpf.deactivate_output(self.__generator.GetSignal)
		sumpf.deactivate_output(self.__fade_sweep.GetSignal)
		sumpf.deactivate_output(self.__apply_fade.GetOutput)
		# set parameters
		self.__generator.SetStartFrequency(start_frequency)
		self.__generator.SetStopFrequency(stop_frequency)
		if exponential:
			self.__generator.SetSweepFunction(sumpf.modules.SweepGenerator.Exponential)
		else:
			self.__generator.SetSweepFunction(sumpf.modules.SweepGenerator.Linear)
		if sweep_duration is not None:
			self.__sweep_duration.SetDuration(sweep_duration)
		if silence_duration is not None:
			self.__silence_duration.SetDuration(silence_duration)
		fade_length = sumpf.modules.DurationToLength(duration=fade).GetLength()
		if fade_length == 0:
			self.__generator.SetInterval(None)
			self.__fade_sweep.SetRaiseInterval(None)
			self.__fade_sweep.SetFallInterval(None)
		else:
			self.__generator.SetInterval((fade_length, self.__sweep_duration.GetLength() - fade_length))
			self.__fade_sweep.SetRaiseInterval((0, fade_length))
			self.__fade_sweep.SetFallInterval((self.__sweep_duration.GetLength() - fade_length, self.__sweep_duration.GetLength()))
		self.__amplifier.SetAmplificationFactor(amplitude)
		self.__average.SetNumber(averages)
		# reactivate modules
		sumpf.activate_output(self.__fade_sweep.GetSignal)
		sumpf.activate_output(self.__generator.GetSignal)
		sumpf.activate_output(self.__apply_fade.GetOutput)
		sumpf.activate_output(self.__concatenation)
		# connect to jack
		input = self.__audio_io.GetInputs()[0]
		output = self.__audio_io.GetOutputs()[0]
		if capture_port is not None:
			self.__audio_io.Connect(output, capture_port)
		if playback_port is not None:
			self.__audio_io.Connect(playback_port, input)
		# run the recording
		self.__average.Start()
		sumpf.activate_output(self.__divide.GetOutput)
		# disconnect from jack
		if capture_port is not None:
			self.__audio_io.Disconnect(playback_port, input)
		if playback_port is not None:
			self.__audio_io.Disconnect(output, capture_port)

	def Keep(self, label):
		"""
		Stores the current spectrum in the merger.
		"""
		sumpf.deactivate_output(self.__merge_utf)
		if self.__showrecent:
			sumpf.disconnect(self.__relabel.GetOutput, self.__merge_utf.AddInput)
		self.__relabel.SetLabels((label,))
		data_id = self.__merge_utf.AddInput(self.__relabel.GetOutput())
		self.__kept_ids.append(data_id)
		self.__relabel.SetLabels(("Recent",))
		if self.__showrecent:
			sumpf.connect(self.__relabel.GetOutput, self.__merge_utf.AddInput)
		sumpf.activate_output(self.__merge_utf)

	def Clear(self):
		"""
		Removes all kept spectrums.
		"""
		sumpf.deactivate_output(self.__merge_utf)
		while self.__kept_ids != []:
			data_id = self.__kept_ids.pop()
			self.__merge_utf.RemoveInput(data_id)
		self.ShowRecent(True)
		sumpf.activate_output(self.__merge_utf)

	################
	# File methods #
	################

	def __Save(self, merger, filename, format):
		data = merger.GetOutput()
		if isinstance(data, sumpf.Signal):
			filehandler = sumpf.modules.SignalFile()
			filehandler.SetSignal(data)
		else:
			filehandler = sumpf.modules.SpectrumFile()
			filehandler.SetSpectrum(data)
		filehandler.SetFormat(format)
		filehandler.SetFilename(filename)

	def __Load(self, merger, id_dict, filename):
		def prepare_for_loading():
			total_length = self.__properties.GetSignalLength()
			ratio = float(self.__sweep_duration.GetLength()) / float(self.__concatenation.GetOutputLength())
			sweep_length = total_length * ratio
			sumpf.deactivate_output(self.__concatenation.GetOutput)
			self.__playback_fft.SetSignal.NoticeAnnouncement(self.__concatenation.GetOutput)
			sumpf.activate_output(self.__properties)
			self.__sweep_duration.SetDuration(sweep_length / self.__properties.GetSamplingRate())
			self.__silence_duration.SetDuration((total_length - sweep_length) / self.__properties.GetSamplingRate())
			self.__record_fft.SetSignal(sumpf.modules.SilenceGenerator(samplingrate=self.__properties.GetSamplingRate(), length=total_length).GetSignal())
			sumpf.activate_output(self.__concatenation.GetOutput)
		loaded = None
		ending = filename.split(".")[-1]
		if merger in [self.__merge_uir, self.__merge_pir]:
			filehandler = sumpf.modules.SignalFile()
			format = sumpf.modules.SignalFile.GetFormats()[0]
			for f in sumpf.modules.SignalFile.GetFormats():
				if f.ending == ending:
					format = f
					break
			filehandler.SetFormat(format)
			filehandler.SetFilename(filename)
			loaded = filehandler.GetSignal()
			if not self.__has_data:
				sumpf.deactivate_output(self.__properties)
				self.__properties.SetSignalLength(len(loaded))
				self.__properties.SetSamplingRate(loaded.GetSamplingRate())
				prepare_for_loading()
		else:
			filehandler = sumpf.modules.SpectrumFile()
			format = sumpf.modules.SpectrumFile.GetFormats()[0]
			for f in sumpf.modules.SpectrumFile.GetFormats():
				if f.ending == ending:
					format = f
					break
			filehandler.SetFormat(format)
			filehandler.SetFilename(filename)
			loaded = filehandler.GetSpectrum()
			if not self.__has_data:
				sumpf.deactivate_output(self.__properties)
				self.__properties.SetSpectrumLength(len(loaded))
				self.__properties.SetResolution(loaded.GetResolution())
				prepare_for_loading()
		data_id = merger.AddInput(loaded)
		if filename in id_dict:
			i = 2
			while filename + " (" + str(i) + ")" in id_dict:
				i += 1
			id_dict[filename + " (" + str(i) + ")"] = data_id
		else:
			id_dict[filename] = data_id
		self.__has_data = True

	def __Unload(self, merger, id_dict, filenames):
		sumpf.deactivate_output(merger.GetOutput)
		for f in filenames:
			data_id = id_dict.pop(f)
			merger.RemoveInput(data_id)
		sumpf.activate_output(merger.GetOutput)

	def SaveUnprocessedTransferFunction(self, filename, format):
		self.__Save(merger=self.__merge_utf, filename=filename, format=format)

	def SaveUnprocessedImpulseResponse(self, filename, format):
		self.__Save(merger=self.__merge_uir, filename=filename, format=format)

	def SaveProcessedTransferFunction(self, filename, format):
		self.__Save(merger=self.__merge_ptf, filename=filename, format=format)

	def SaveProcessedImpulseResponse(self, filename, format):
		self.__Save(merger=self.__merge_pir, filename=filename, format=format)

	def LoadUnprocessedTransferFunction(self, filename):
		self.__Load(merger=self.__merge_utf, id_dict=self.__loaded_ids_utf, filename=filename)

	def LoadUnprocessedImpulseResponse(self, filename):
		self.__Load(merger=self.__merge_uir, id_dict=self.__loaded_ids_uir, filename=filename)

	def LoadProcessedTransferFunction(self, filename):
		self.__Load(merger=self.__merge_ptf, id_dict=self.__loaded_ids_ptf, filename=filename)

	def LoadProcessedImpulseResponse(self, filename):
		self.__Load(merger=self.__merge_pir, id_dict=self.__loaded_ids_pir, filename=filename)

	def UnloadUnprocessedTransferFunction(self, filenames):
		self.__Unload(merger=self.__merge_utf, id_dict=self.__loaded_ids_utf, filenames=filenames)

	def UnloadUnprocessedImpulseResponse(self, filenames):
		self.__Unload(merger=self.__merge_uir, id_dict=self.__loaded_ids_uir, filenames=filenames)

	def UnloadProcessedTransferFunction(self, filenames):
		self.__Unload(merger=self.__merge_ptf, id_dict=self.__loaded_ids_ptf, filenames=filenames)

	def UnloadProcessedImpulseResponse(self, filenames):
		self.__Unload(merger=self.__merge_pir, id_dict=self.__loaded_ids_pir, filenames=filenames)

	def GetLoadedUnprocessedTransferFunctions(self):
		return list(self.__loaded_ids_utf.keys())

	def GetLoadedUnprocessedImpulseResponses(self):
		return list(self.__loaded_ids_uir.keys())

	def GetLoadedProcessedTransferFunctions(self):
		return list(self.__loaded_ids_ptf.keys())

	def GetLoadedProcessedImpulseResponses(self):
		return list(self.__loaded_ids_pir.keys())

	#############################
	# Postprocessing parameters #
	#############################

	def SetRegularization(self, start_frequency, stop_frequency, transition_width, epsilon_max):
		if epsilon_max == 0.0:
			self.__select_regularization.SetSelection(self.__NOT_REGULARIZE)
		else:
			sumpf.deactivate_output(self.__select_regularization.GetOutput)
			self.__regularization.SetStartFrequency(start_frequency)
			self.__regularization.SetStopFrequency(stop_frequency)
			self.__regularization.SetTransitionLength(int(round(transition_width * self.__properties.GetResolution())))
			self.__regularization.SetEpsilonMax(epsilon_max)
			self.__select_regularization.SetSelection(self.__REGULARIZE)
			sumpf.activate_output(self.__select_regularization.GetOutput)

	def SetLowpass(self, frequency, order=16):
		if frequency is not None:
			sumpf.deactivate_output(self.__bypass_filter.GetOutput)
			self.__filter.ReplaceFilter(self.__filter_id, sumpf.modules.FilterGenerator.BUTTERWORTH_LOWPASS(frequency=frequency, order=order))
			self.__bypass_filter.SetSelection(self.__FILTER)
			sumpf.activate_output(self.__bypass_filter)
		else:
			self.__bypass_filter.SetSelection(self.__BYPASS)

	def SetWindow(self, function, interval=None):
		if function is not None:
			sumpf.deactivate_output(self.__bypass_window.GetOutput)
			self.__bypass_window.SetSelection(self.__WINDOW)
			self.__window.SetFunction(function)
			if interval is not None:
				linterval = []
				for d in interval:
					d2l = sumpf.modules.DurationToLength(duration=d, samplingrate=self.__properties.GetSamplingRate())
					linterval.append(d2l.GetLength())
				self.__window.SetFallInterval(linterval)
			sumpf.activate_output(self.__bypass_window.GetOutput)
		else:
			self.__bypass_window.SetSelection(self.__BYPASS)

	def SetNormalize(self, normalize, individual=False, frequency=1000.0):
		"""
		@param normalize: False, to disable normalization, "average" to normalize to average, "frequency" to normalize to frequency
		"""
		sumpf.deactivate_output(self.__bypass_normalize.GetOutput)
		if normalize == "average":
			self.__select_normalization.SetSelection(self.__AVERAGE)
			self.__bypass_normalize.SetSelection(self.__NORMALIZE)
			self.__normalize_avg.SetIndividual(individual)
		elif normalize == "frequency":
			self.__select_normalization.SetSelection(self.__FREQUENCY)
			self.__bypass_normalize.SetSelection(self.__NORMALIZE)
			self.__normalize_frq.SetFrequency(frequency)
		else:
			self.__bypass_normalize.SetSelection(self.__BYPASS)
		sumpf.activate_output(self.__bypass_normalize.GetOutput)

	def ShowRecent(self, show=True):
		if show:
			if not self.__showrecent:
				sumpf.connect(self.__relabel.GetOutput, self.__merge_utf.AddInput)
				self.__showrecent = True
		else:
			if self.__showrecent:
				sumpf.disconnect(self.__relabel.GetOutput, self.__merge_utf.AddInput)
				self.__showrecent = False

	####################
	# Other parameters #
	####################

	def GetSignalDuration(self):
		return self.__properties.GetSignalLength() / self.__properties.GetSamplingRate()

