# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2015 Jonas Schulte-Coerne
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
    CROP = 3

    def __init__(self, datasets, merge_strategy, on_length_conflict):
        """
        @param datasets: a list of data sets that shall be added to the merger. As the constructor can not return the data ids for these data sets, they can only be removed from the merger with the Clear method.
        @param merge_strategy: a function that implements the strategy according to which the channels of the output data are sorted
        @param on_length_conflict: one of the merger class's flags for length conflict resolution (e.g. RAISE_ERROR_EXCEPT_EMPTY)
        """
        self.__strategy = merge_strategy
        self._on_length_conflict = on_length_conflict
        self._data = sumpf.helper.MultiInputData()
        for d in datasets:
            self._AddInput(d)

    def AddInput(self, data):
        """
        Abstract method whose overrides shall add an input data set to the merger.
        This method has to be overridden, so it can be decorated to be an Input
        with the correct type. The overrides must also implement sanity checks
        for the input data.
        @param data: a data set that shall be merged into the output data set
        @retval : the id under which the data set is stored
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def RemoveInput(self, data_id):
        """
        Removes a data set from the merger.
        @param data_id: the id under which the data set is stored, which shall be removed
        """
        self._data.Remove(data_id)

    def ReplaceInput(self, data_id, data):
        """
        Abstract method whose overrides shall replace the data set, which is stored
        under the given id with the new data.
        This method has to be overridden, so the derived classes can check the
        new data for compatibility with the other data in the merger.
        @param data_id: the id under which the data set is stored, which shall be replaced
        @param data: the new data that shall be stored under that id
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def GetOutput(self):
        """
        Abstract method whose overrides shall generate and return the merged data set.
        @retval : the merged output data set
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    @sumpf.Trigger("GetOutput")
    def Clear(self):
        """
        Removes all input data sets from the merger.
        """
        self._data.Clear()

    @sumpf.Output(int)
    def GetNumberOfOutputChannels(self):
        """
        Returns the number of channels of the output data set.
        @retval : the number of channels of the output data set as an integer
        """
        result = 0
        for d in self._data.GetData():
            result += len(d.GetChannels())
        return max(1, result)

    @sumpf.Input(type(GetOutput), "GetOutput")  # type is a method
    def SetMergeStrategy(self, strategy):
        """
        Sets the strategy according to which the channels of the output data are sorted.
        @param strategy: a function that returns a tuple of channels
        """
        self.__strategy = strategy

    @sumpf.Input(type(RAISE_ERROR_EXCEPT_EMPTY), "GetOutput")
    def SetLengthConflictStrategy(self, strategy):
        """
        Sets the behavior for when the added data sets do not have the same length.
        The following flags are available:
        RAISE_ERROR for raising a RuntimeError during merging, if data sets with
            different lengths have been added.
        RAISE_ERROR_EXCEPT_EMPTY for raising errors just like with RAISE_ERROR,
            but only when neither the new input data set nor all the already added
            data sets are empty.
        FILL_WITH_ZEROS for solving the conflict by filling the too short data
            sets with zeros until all sets have the same length.
        CROP for cropping the length of all added data sets to the length of the
            shortest data set.
        @param strategy: one of the merger class's flags for length conflict resolution
        """
        self._on_length_conflict = strategy

    def _AddInput(self, data):
        """
        A protected method that can be called from the overrides of AddInput, after
        they have checked the given input data.
        It adds the given data to the merger and returns the id under which it is
        stored.
        @param data: a data set that shall be merged into the output data set
        @retval : the id under which the data set is stored
        """
        return self._data.Add(data)

    def _GetChannelsAndLabels(self):
        """
        Creates the channels and labels for the merged ChannelData instance.
        @retval : a tuple (a, b), where a is a tuple of channels and b is a tuple of labels
        """
        # functions for length conflict resolution
        def fill_with_zeros(chs):
            length = 0
            for c in chs:
                length = max(length, len(c))
            for c in chs:
                for i in range(len(c), length):
                    c.append(0.0)
            return chs
        def crop(chs):
            length = len(chs[0])
            for c in chs[1:]:
                length = min(length, len(c))
            result = []
            for c in chs:
                result.append(c[0:length])
            return result
        # get the channels and labels in the correct order
        channels, labels = self.__strategy(self._data.GetData())
        # resolve length conflicts
        if channels != []:
            if self._on_length_conflict == MergeChannelData.RAISE_ERROR:
                for c in channels[1:]:
                    if len(c) != len(channels[0]):
                        raise RuntimeError("The data sets do not have the same length")
            elif self._on_length_conflict == MergeChannelData.FILL_WITH_ZEROS:
                channels = fill_with_zeros(channels)
            elif self._on_length_conflict == MergeChannelData.CROP:
                channels = crop(channels)
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
        if self._data.GetData() == []:
            return True
        elif self._on_length_conflict == MergeChannelData.RAISE_ERROR_EXCEPT_EMPTY:
            for d in self._data.GetData():
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
        return len(self._data.GetData())

    def _GetLength(self):
        """
        Returns the length of the resulting data set.
        @retval : the length as an integer
        """
        if self._data.GetData() == []:
            return 2
        elif self._on_length_conflict == MergeChannelData.RAISE_ERROR_EXCEPT_EMPTY:
            for d in self._data.GetData():
                if not d.IsEmpty():
                    return len(d)
        elif self._on_length_conflict == MergeChannelData.RAISE_ERROR:
            return len(self._data.GetData()[0])
        elif self._on_length_conflict == MergeChannelData.FILL_WITH_ZEROS:
            length = 2
            for d in self._data.GetData():
                length = max(length, len(d))
            return length

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
    def __init__(self, signals=[], merge_strategy=MergeChannelData._FIRST_DATASET_FIRST, on_length_conflict=MergeChannelData.RAISE_ERROR_EXCEPT_EMPTY):
        """
        @param signals: a list of Signals that shall be added to the merger. As the constructor can not return the data ids for these Signals, they can only be removed from the merger with the Clear method.
        @param merge_strategy: a function that implements the strategy according to which the channels of the output Signal are sorted
        @param on_length_conflict: one of the flags of the MergeSignals class for length conflict resolution (e.g. RAISE_ERROR_EXCEPT_EMPTY)
        """
        MergeChannelData.__init__(self, datasets=signals, merge_strategy=merge_strategy, on_length_conflict=on_length_conflict)

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Generates the merged Signal and returns it.
        @retval : the merged output Signal
        """
        data = self._data.GetData()
        if data == []:
            return sumpf.Signal()
        else:
            i = 0
            if self._on_length_conflict == MergeSignals.RAISE_ERROR_EXCEPT_EMPTY:
                while i < len(data) and data[i].IsEmpty():
                    i += 1
            samplingrate = data[i % len(data)].GetSamplingRate()
            for d in data[i + 1:]:
                if d.GetSamplingRate() != samplingrate:
                    if self._on_length_conflict != MergeSignals.RAISE_ERROR_EXCEPT_EMPTY or not d.IsEmpty():
                        raise RuntimeError("The Signals in the merger do not all have the same sampling rate")
            channels, labels = self._GetChannelsAndLabels()
            return sumpf.Signal(channels=channels, samplingrate=samplingrate, labels=labels)

    @sumpf.MultiInput(data_type=sumpf.Signal, remove_method="RemoveInput", observers=["GetOutput", "GetNumberOfOutputChannels"], replace_method="ReplaceInput")
    def AddInput(self, signal):
        """
        Adds a Signal to the merger
        @param signal: a Signal that shall be merged into the output Signal
        @retval : an id under which the Signal is stored
        """
        return self._AddInput(signal)

    def ReplaceInput(self, data_id, data):
        """
        Replaces the Signal, which is stored under the given id with the new data.
        @param data_id: the id under which the Signal is stored, which shall be replaced
        @param data: the new Signal that shall be stored under that id
        """
        self._data.Replace(data_id=data_id, data=data)

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
    def __init__(self, spectrums=[], merge_strategy=MergeChannelData._FIRST_DATASET_FIRST, on_length_conflict=MergeChannelData.RAISE_ERROR_EXCEPT_EMPTY):
        """
        @param spectrums: a list of Spectrums that shall be added to the merger. As the constructor can not return the data ids for these Spectrums, they can only be removed from the merger with the Clear method.
        @param merge_strategy: a function that implements the strategy according to which the channels of the output Signal are sorted
        @param on_length_conflict: one of the flags of the MergeSpectrums class for length conflict resolution (e.g. RAISE_ERROR_EXCEPT_EMPTY)
        """
        MergeChannelData.__init__(self, datasets=spectrums, merge_strategy=merge_strategy, on_length_conflict=on_length_conflict)

    @sumpf.Output(sumpf.Spectrum)
    def GetOutput(self):
        """
        Generates the merged Spectrum and returns it.
        @retval : the merged output Spectrum
        """
        data = self._data.GetData()
        if data == []:
            return sumpf.Spectrum()
        else:
            i = 0
            if self._on_length_conflict == MergeSpectrums.RAISE_ERROR_EXCEPT_EMPTY:
                while i < len(data) and data[i].IsEmpty():
                    i += 1
            resolution = data[i % len(data)].GetResolution()
            for d in data[i + 1:]:
                if d.GetResolution() != resolution:
                    if self._on_length_conflict != MergeSpectrums.RAISE_ERROR_EXCEPT_EMPTY or not d.IsEmpty():
                        raise RuntimeError("The Spectrums in the merger do not all have the same resolution")
            channels, labels = self._GetChannelsAndLabels()
            return sumpf.Spectrum(channels=channels, resolution=resolution, labels=labels)

    @sumpf.MultiInput(data_type=sumpf.Spectrum, remove_method="RemoveInput", observers=["GetOutput", "GetNumberOfOutputChannels"], replace_method="ReplaceInput")
    def AddInput(self, spectrum):
        """
        Adds a Spectrum to the merger
        @param spectrum: a Spectrum that shall be merged into the output Spectrum
        @retval : an id under which the Spectrum is stored
        """
        return self._AddInput(spectrum)

    def ReplaceInput(self, data_id, data):
        """
        Replaces the Spectrum, which is stored under the given id with the new data.
        @param data_id: the id under which the Spectrum is stored, which shall be replaced
        @param data: the new Spectrum that shall be stored under that id
        """
        self._data.Replace(data_id=data_id, data=data)

    @staticmethod
    def FIRST_SPECTRUM_FIRST(datasets):
        """
        A merge strategy for merging Spectrums
        This strategy puts the channels of the Spectrums that have been added first at the beginning

        example:
        ((1.1,), (1.2,)) and ((2.1,), (2.2,)) are merged to ((1.1,), (1.2,), (2.1,), (2.2,))
        """
        return MergeChannelData._FIRST_DATASET_FIRST(datasets)

