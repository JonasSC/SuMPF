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

import copy
import sumpf


class MergeChannelData(object):
	"""
	A base class for merging the data of multiple ChannelData instances into one instance.
	"""
	# Flags for the handling of length conflicts. See SetLengthConflictStrategy for documentation
	RAISE_ERROR_EXCEPT_EMPTY = 0
	RAISE_ERROR = 1
	FILL_WITH_ZEROS = 2

	def __init__(self):
		self.__strategy = MergeChannelData._FIRST_DATASET_FIRST
		self.__ids = []
		self.__datasets = []
		self._on_length_conflict = MergeChannelData.RAISE_ERROR_EXCEPT_EMPTY

	def AddInput(self, input):
		"""
		Abstract method whose overrides shall add an input data set to the merger.
		@param input: a data set that shall be merged into the output data set
		@retval : an id under which the data set is stored
		"""
		raise NotImplementedError("This method should have been overridden in a derived class")

	def RemoveInput(self, input_id):
		"""
		Removes a data set from the merger
		@param input_id: the id under which the data set is stored, which shall be removed
		"""
		index = self.__ids.index(input_id)
		self.__ids.pop(index)
		self.__datasets.pop(index)

	def GetOutput(self):
		"""
		Abstract method whose overrides shall generate and return the merged data set.
		@retval : the merged output data set
		"""
		raise NotImplementedError("This method should have been overridden in a derived class")

	@sumpf.Output(int)
	def GetNumberOfOutputChannels(self):
		"""
		Returns the number of channels of the output data set.
		@retval : the number of channels of the output data set as an integer
		"""
		result = 0
		for d in self.__datasets:
			result += len(d.GetChannels())
		return max(1, result)

	@sumpf.Input(type(GetOutput), "GetOutput")	# type is a method
	def SetMergeStrategy(self, strategy):
		"""
		Sets the strategy according to which the channels of the output data are sorted.
		@param strategy: a method that returns a tuple of channels
		"""
		self.__strategy = strategy

	@sumpf.Input(type(RAISE_ERROR_EXCEPT_EMPTY), "GetOutput")
	def SetLengthConflictStrategy(self, strategy):
		"""
		Sets the behavior for when the added data sets do not have the same length.
		The following flags are available:
		RAISE_ERROR for raising a ValueError if the input data set has a
			different length than the already added data. A RuntimeError is
			raised during merging if data sets with different lengths have been
			added and then the strategy has been changed to RAISE_ERROR.
		FILL_WITH_ZEROS for solving the conflict by filling the too short data
			sets with zeros until all sets have the same length
		RAISE_ERROR_EXCEPT_EMPTY for raising errors just like with RAISE_ERROR,
			but only when neither the input data set nor all the added data sets
			are empty.
		@param strategy: one of the MergeChannelData's flags for length conflict resolution
		"""
		self._on_length_conflict = strategy

	def _AddInput(self, input_data):
		"""
		Base method for adding input data.
		@param input_data: a ChannelData instance
		@retval : the id under which the new data is stored
		"""
		data_id = 0
		while data_id in self.__ids:
			data_id += 1
		self.__ids.append(data_id)
		self.__datasets.append(input_data)
		return data_id

	def _GetChannelsAndLabels(self):
		"""
		Creates the channels and labels for the merged ChannelData instance.
		@retval : a tuple (a, b), where a is a tuple of channels and b is a tuple of labels
		"""
		def fill_with_zeros(chs):
			length = 0
			for c in chs:
				length = max(length, len(c))
			for c in chs:
				for i in range(len(c), length):
					c.append(0.0)
			return chs
		channels, labels = self.__strategy(self.__datasets)
		if channels != []:
			if self._on_length_conflict == MergeChannelData.RAISE_ERROR:
				for c in channels[1:]:
					if len(c) != len(channels[0]):
						raise RuntimeError("The data sets do not have the same length")
			elif self._on_length_conflict == MergeChannelData.FILL_WITH_ZEROS:
				channels = fill_with_zeros(channels)
			elif self._on_length_conflict == MergeChannelData.RAISE_ERROR_EXCEPT_EMPTY:
				length = 0
				empty = True
				for c in channels:
					if c != [0.0, 0.0]:
						if empty:
							length = len(c)
							empty = False
						elif len(c) != length:
							raise RuntimeError("The data sets do not have the same length")
				channels = fill_with_zeros(channels)
		return channels, labels

	def _IsEmpty(self):
		"""
		Looks up if the merger contains data.
		This also depends on the length conflict strategy. Normally the merger
		considers itself empty only if no data sets have been added. But when
		the strategy is set to RAISE_ERROR_EXCEPT_EMPTY, it also considers itself
		empty if only empty data sets have been added.
		@retval : True if the merger is empty, False otherwise
		"""
		if self.__datasets == []:
			return True
		elif self._on_length_conflict == MergeChannelData.RAISE_ERROR_EXCEPT_EMPTY:
			for d in self.__datasets:
				if not d.IsEmpty():
					return False
			return True
		else:
			return False

	def _GetNumberOfDataSets(self):
		"""
		Returns the number of data sets that are about to be merged.
		@retval : the number of data sets as an integer
		"""
		return len(self.__datasets)

	def _GetLength(self):
		"""
		Returns the length of the resulting data set.
		@retval : the length as an integer
		"""
		if self.__datasets == []:
			return 2
		else:
			for d in self.__datasets:
				if not d.IsEmpty():
					return len(d)
			return len(self.__datasets[0])

	@staticmethod
	def _FIRST_DATASET_FIRST(datasets):
		"""
		Base function for a merge strategy method.
		This strategy puts the channels of the data sets that have been added
		first at the beginning

		example:
		((1.1,), (1.2,)) and ((2.1,), (2.2,)) are merged to ((1.1,), (1.2,), (2.1,), (2.2,))
		"""
		channels = []
		labels = []
		for d in datasets:
			for i in range(len(d.GetChannels())):
				channels.append(list(d.GetChannels()[i]))
				labels.append(d.GetLabels()[i])
		return channels, labels

	@staticmethod
	def FIRST_CHANNEL_FIRST(datasets):
		"""
		A merge strategy function.
		This strategy puts the first channels of each data set at the beginning

		example:
		((1.1,), (1.2,)) and ((2.1,), (2.2,)) are merged to ((1.1,), (2.1,), (1.2,), (2.2,))
		"""
		channels = []
		labels = []
		dataset_indices = list(range(len(datasets)))
		i = 0
		while dataset_indices != []:
			for d in copy.copy(dataset_indices):
				if len(datasets[d].GetChannels()) > i:
					channels.append(list(datasets[d].GetChannels()[i]))
					labels.append(datasets[d].GetLabels()[i])
				else:
					dataset_indices.remove(d)
			i += 1
		return channels, labels



class MergeSignals(MergeChannelData):
	"""
	A module for merging multiple Signals into one Signal.

	There are different strategies to merge the Signals, which affect the order
	of the output Signal's channels. These strategies are implemented in the
	methods "FirstSignalFirst" and "FirstChannelFirst". Look there for further
	details of these strategies. The strategy can be set by passing one of these
	methods to the "SetMergeStrategy" method.

	There are also different strategies to merge Signals which have a different
	length. They are documented in the documentation of "SetLengthConflictStrategy".

	The merged Signals must have the same sampling rate.
	"""
	def __init__(self):
		MergeChannelData.__init__(self)
		self.__samplingrate = sumpf.config.get("default_samplingrate")

	@sumpf.Output(sumpf.Signal)
	def GetOutput(self):
		"""
		Generates the merged Signal and returns it.
		@retval : the merged output Signal
		"""
		signal = None
		try:
			channels, labels = self._GetChannelsAndLabels()
			signal = sumpf.Signal(channels=channels, samplingrate=self.__samplingrate, labels=labels)
		except ValueError:
			signal = sumpf.Signal(samplingrate=self.__samplingrate)
		return signal

	@sumpf.MultiInput(sumpf.Signal, "RemoveInput", ["GetOutput", "GetNumberOfOutputChannels"])
	def AddInput(self, input):
		"""
		Adds a Signal to the merger
		@param input: a Signal that shall be merged into the output Signal
		@retval : an id under which the Signal is stored
		"""
		if self._IsEmpty():
			self.__samplingrate = input.GetSamplingRate()
		elif not self.AddInput.GetNumberOfExpectedInputs() == self._GetNumberOfDataSets():
			if input.GetSamplingRate() != self.__samplingrate:
				if self._on_length_conflict != MergeSignals.RAISE_ERROR_EXCEPT_EMPTY or not input.IsEmpty():
					raise ValueError("The Signal has a different sampling rate than the other Signals in the merger")
			if len(input) != self._GetLength():
				if self._on_length_conflict == MergeSignals.RAISE_ERROR or \
				  (self._on_length_conflict == MergeSignals.RAISE_ERROR_EXCEPT_EMPTY and not input.IsEmpty()):
					raise ValueError("The Signal has a different length than the other Signals in the merger")
		return self._AddInput(input)

	@staticmethod
	def FIRST_SIGNAL_FIRST(datasets):
		"""
		A merge strategy for merging Signals.
		This strategy puts the channels of the Signals that have been added first at the beginning

		example:
		((1.1,), (1.2,)) and ((2.1,), (2.2,)) are merged to ((1.1,), (1.2,), (2.1,), (2.2,))
		"""
		return MergeChannelData._FIRST_DATASET_FIRST(datasets)



class MergeSpectrums(MergeChannelData):
	"""
	A module for merging multiple Spectrums into one Spectrum

	There are different strategies to merge the Spectrums, which affect the order
	of the output Spectrum's channels. These strategies are implemented in the
	methods "FirstSpectrumFirst" and "FirstChannelFirst". Look there for further
	details of these strategies. The strategy can be set by passing one of these
	methods to the "SetMergeStrategy" method.

	There are also different strategies to merge Spectrums which have a different
	length. They are documented in the documentation of "SetLengthConflictStrategy".

	The merged Spectrums must have the same resolution.
	"""
	def __init__(self):
		MergeChannelData.__init__(self)
		self.__resolution = 48000

	@sumpf.Output(sumpf.Spectrum)
	def GetOutput(self):
		"""
		Generates the merged Spectrum and returns it.
		@retval : the merged output Spectrum
		"""
		spectrum = None
		try:
			channels, labels = self._GetChannelsAndLabels()
			spectrum = sumpf.Spectrum(channels=channels, resolution=self.__resolution, labels=labels)
		except ValueError:
			spectrum = sumpf.Spectrum(resolution=self.__resolution)
		return spectrum

	@sumpf.MultiInput(sumpf.Spectrum, "RemoveInput", ["GetOutput", "GetNumberOfOutputChannels"])
	def AddInput(self, input):
		"""
		Adds a Spectrum to the merger
		@param input: a Spectrum that shall be merged into the output Spectrum
		@retval : an id under which the Spectrum is stored
		"""
		if self._IsEmpty():
			self.__resolution = input.GetResolution()
		elif not self.AddInput.GetNumberOfExpectedInputs() == self._GetNumberOfDataSets():
			if input.GetResolution() != self.__resolution:
				if self._on_length_conflict != MergeSpectrums.RAISE_ERROR_EXCEPT_EMPTY or not input.IsEmpty():
					raise ValueError("The Spectrum has a different resolution than the other Spectrums in the merger")
			if len(input) != self._GetLength():
				if self._on_length_conflict == MergeSpectrums.RAISE_ERROR or \
				  (self._on_length_conflict == MergeSpectrums.RAISE_ERROR_EXCEPT_EMPTY and not input.IsEmpty()):
					raise ValueError("The Spectrums has a different length than the other Spectrums in the merger")
		return self._AddInput(input)

	@staticmethod
	def FIRST_SPECTRUM_FIRST(datasets):
		"""
		A merge strategy for merging Spectrums
		This strategy puts the channels of the Spectrums that have been added first at the beginning

		example:
		((1.1,), (1.2,)) and ((2.1,), (2.2,)) are merged to ((1.1,), (1.2,), (2.1,), (2.2,))
		"""
		return MergeChannelData._FIRST_DATASET_FIRST(datasets)

