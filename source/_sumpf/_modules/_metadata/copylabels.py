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

import sumpf


class CopyLabels(object):
    """
    Abstract base class for copying the labels of one ChannelData instance into another one.
    This can be useful to preserve the labels after an operation that merges two
    data sets and drops their labels by doing so.
    """
    def __init__(self, data_input=None, label_input=None):
        """
        @param data_input: an optional data set from which the data shall be taken
        @param label_input: an optional data set from which the labels shall be taken
        """
        self._data_input = data_input
        self._label_input = label_input

    @sumpf.Input(sumpf.internal.ChannelData, "GetOutput")
    def SetLabelInput(self, input):
        """
        Sets the data set from which the labels shall be taken.
        @param labels: the data set from which the labels shall be taken
        """
        self._label_input = input

    def SetDataInput(self, input):
        """
        Virtual method whose overrides shall set the data set from which the data
        shall be taken.
        It is necessary to implement this method in a derived class, so that the
        type of the Input can be set correctly.
        @param input: the data set whose channels shall be relabeled
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def GetOutput(self):
        """
        Virtual method whose overrides shall return the correctly labeled data set.
        It is necessary to implement this method in a derived class, so that the
        type of the output can be set correctly.
        @retval : the data set with relabeled channels
        """
        raise NotImplementedError("This method should have been overridden in a derived class")



class CopyLabelsToSignal(CopyLabels):
    """
    Module for copying the labels of a ChannelData instance into a Signal instance.
    This can be useful to preserve the labels after an operation that merges two
    Signals and drops their labels by doing so.
    """
    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetDataInput(self, input):
        """
        Sets the input Signal from which the data shall be taken.
        @param input: the Signal whose channels shall be relabeled
        """
        self._data_input = input

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Creates a Signal with relabeled channels and returns it.
        @retval : a Signal with relabeled channels
        """
        labels = []
        if self._label_input is not None:
            labels = self._label_input.GetLabels()
        elif self._data_input is not None:
            labels = self._data_input.GetLabels()
        signal = None
        if self._data_input is None:
            signal = sumpf.Signal(labels=labels)
        else:
            try:
                signal = sumpf.Signal(channels=self._data_input.GetChannels(), samplingrate=self._data_input.GetSamplingRate(), labels=labels)
            except ValueError:
                signal = sumpf.Signal(samplingrate=self._data_input.GetSamplingRate(), labels=labels)
        return signal



class CopyLabelsToSpectrum(CopyLabels):
    """
    Module for copying the labels of a ChannelData instance into a Spectrum instance.
    This can be useful to preserve the labels after an operation that merges two
    Spectrums and drops their labels by doing so.
    """
    @sumpf.Input(sumpf.Spectrum, "GetOutput")
    def SetDataInput(self, input):
        """
        Sets the input Spectrum from which the data shall be taken.
        @param input: the Spectrum whose channels shall be relabeled
        """
        self._data_input = input

    @sumpf.Output(sumpf.Spectrum)
    def GetOutput(self):
        """
        Creates a Spectrum with relabeled channels and returns it.
        @retval : a Spectrum with relabeled channels
        """
        labels = []
        if self._label_input is not None:
            labels = self._label_input.GetLabels()
        elif self._data_input is not None:
            labels = self._data_input.GetLabels()
        spectrum = None
        if self._data_input is None:
            spectrum = sumpf.Spectrum(labels=labels)
        else:
            try:
                spectrum = sumpf.Spectrum(channels=self._data_input.GetChannels(), resolution=self._data_input.GetResolution(), labels=labels)
            except ValueError:
                spectrum = sumpf.Spectrum(resolution=self._data_input.GetResolution(), labels=labels)
        return spectrum

