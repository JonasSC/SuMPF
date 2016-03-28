# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2016 Jonas Schulte-Coerne
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

import collections
import sumpf


class RelabelChannelData(object):
    """
    Abstract base class for setting the channel labels of ChannelData instances.
    """
    def __init__(self, data, labels):
        """
        @param data: a data set whose channels shall be relabeled
        @param labels: a tuple of labels for the output data set's channels
        """
        self._data = data
        self._labels = tuple(labels)

    @sumpf.Input(collections.Iterable, "GetOutput")
    def SetLabels(self, labels):
        """
        Sets the labels for the output data set's channels.
        @param labels: a tuple of labels for the output data set's channels
        """
        self._labels = tuple(labels)

    def GetOutput(self):
        """
        Virtual method whose overrides shall return the relabeled data set.
        It is necessary to implement this method in a derived class, so that the
        type of the output can be set correctly.
        @retval : the data set with relabeled channels
        """
        raise NotImplementedError("This method should have been overridden in a derived class")



class RelabelSignal(RelabelChannelData):
    """
    Module for setting the channel labels of a Signal.
    """
    def __init__(self, signal=None, labels=()):
        """
        @param signal: a Signal instance whose channels shall be relabeled
        @param labels: a tuple of labels for the output data set's channels
        """
        if signal is None:
            signal = sumpf.Signal()
        RelabelChannelData.__init__(self, data=signal, labels=labels)

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetSignal(self, signal):
        """
        Sets the input Signal whose channels shall be relabeled.
        @param signal: the Signal whose channels shall be relabeled
        """
        self._data = signal

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Creates a Signal with relabeled channels and returns it.
        @retval : a Signal with relabeled channels
        """
        signal = None
        if self._data is None:
            signal = sumpf.Signal(labels=self._labels)
        else:
            labels = self._labels
            if labels == ():
                labels = self._data.GetLabels()
            try:
                signal = sumpf.Signal(channels=self._data.GetChannels(), samplingrate=self._data.GetSamplingRate(), labels=labels)
            except ValueError:
                signal = sumpf.Signal(samplingrate=self._data.GetSamplingRate(), labels=labels)
        return signal



class RelabelSpectrum(RelabelChannelData):
    """
    Module for setting the channel labels of a Spectrum.
    """
    def __init__(self, spectrum=None, labels=()):
        """
        @param spectrum: a Spectrum instance whose channels shall be relabeled
        @param labels: a tuple of labels for the output data set's channels
        """
        if spectrum is None:
            spectrum = sumpf.Spectrum()
        RelabelChannelData.__init__(self, data=spectrum, labels=labels)

    @sumpf.Input(sumpf.Spectrum, "GetOutput")
    def SetSpectrum(self, spectrum):
        """
        Sets the input Spectrum whose channels shall be relabeled.
        @param spectrum: the Spectrum whose channels shall be relabeled
        """
        self._data = spectrum

    @sumpf.Output(sumpf.Spectrum)
    def GetOutput(self):
        """
        Creates a Spectrum with relabeled channels and returns it.
        @retval : a Spectrum with relabeled channels
        """
        spectrum = None
        if self._data is None:
            spectrum = sumpf.Spectrum(labels=self._labels)
        else:
            labels = self._labels
            if labels == ():
                labels = self._data.GetLabels()
            try:
                spectrum = sumpf.Spectrum(channels=self._data.GetChannels(), resolution=self._data.GetResolution(), labels=labels)
            except ValueError:
                spectrum = sumpf.Spectrum(resolution=self._data.GetResolution(), labels=labels)
        return spectrum

