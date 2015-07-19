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


class SplitChannelData(object):
    """
    This class makes it possible to select certain channels of a ChannelData
    instance and create a new instance from them.
    """
    ALL = None  # For selecting all channels

    def __init__(self, data, channels):
        """
        @param data: the input data, from which the channels shall be taken
        @param channels: the indexes of the selected channels that shall be in the output data set
        """
        self._input = data
        self.__channels = []
        self.__SetOutputChannels(channels)

    def GetOutput(self):
        """
        Virtual base method whose overrides shall create and return an output
        data set which shall only have the selected channels.
        @retval : the output data set with only the selected channels
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def SetInput(self, data):
        """
        Base method that sets the input data from which the channels shall be taken.
        Derived classes can override and then call this method to decorate it
        with "@sumpf.Input(...)".
        @param data: the input data, from which the channels shall be taken
        """
        self._input = data
        length = len(self._input.GetChannels())
        newchannels = []
        for i in self.__channels:
            if i < length:
                newchannels.append(i)
        self.__channels = newchannels

    @sumpf.Output(int)
    def GetNumberOfOutputChannels(self):
        """
        Returns the number of channels of the output data set.
        @retval : the number of channels of the output data set as an integer
        """
        return len(self.__channels)

    @sumpf.Input(tuple, ["GetOutput", "GetNumberOfOutputChannels"])
    def SetOutputChannels(self, channels):
        """
        Sets the channels of the input data set that shall be copied to the output.
        @param channels: a flag like type(self).ALL or an integer or a tuple of integers that are the indexes of the selected input data set's channels
        """
        return self.__SetOutputChannels(channels)

    def _GetChannelsAndLabels(self):
        """
        Creates the channels and labels for the split ChannelData instance and
        returns them as a tuple.
        @retval : a tuple (a, b), where a is a tuple of channels and b is a tuple of labels
        """
        if self.__all:
            return (self._input.GetChannels(), self._input.GetLabels())
        else:
            channels = []
            labels = []
            for i in self.__channels:
                channels.append(self._input.GetChannels()[i])
                labels.append(self._input.GetLabels()[i])
            return channels, labels

    def __SetOutputChannels(self, channels):
        """
        A private helper method to avoid, that the connector SetOutputChannels
        is called in the constructor.
        @param channels: a flag like type(self).ALL or an integer or a tuple of integers that are the indexes of the selected input data set's channels
        """
        if channels == SplitChannelData.ALL:
            self.__all = True
        else:
            self.__all = False
            if isinstance(channels, int):
                channels = (channels,)
            for i in channels:
                if i < 0:
                    raise IndexError("Negative indices are not possible")
            self.__channels = channels



class SplitSignal(SplitChannelData):
    """
    This class makes it possible to select certain channels of a Signal instance
    and create a new Signal from them.

    The selection of the output channels can be specified in three different ways:
     - By passing the flag SplitSignal.ALL to the SetOutputChannels method. This
    way, the output Signal will have the same channels as the input Signal.
     - By passing an integer index to the SetOutputChannels method. This way,
    the output Signal will have only the channel with the given index from the
    input Signal.
     - By passing a list of integer indexes to the SetOutputChannels method. This
    way, the output Signal will have all the channels from the input Signal
    whose index is in the given list. Often that list can be generated with the
    range function (e.g. range(7)[4:6]).
    """
    def __init__(self, data=None, channels=[]):
        """
        @param data: the input Signal, from which the channels shall be taken
        @param channels: the indexes of the selected channels that shall be in the output Signal
        """
        if data is None:
            data = sumpf.Signal()
        SplitChannelData.__init__(self, data, channels)

    @sumpf.Input(sumpf.Signal, ["GetOutput", "GetNumberOfOutputChannels"])
    def SetInput(self, data):
        """
        Sets the Signal from which the channels are taken.
        @param data: the input Signal, from which the channels shall be taken
        """
        SplitChannelData.SetInput(self, data)

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Creates and returns an output Signal which has only the selected channels.
        @retval : the output Signal with only the selected channels
        """
        channels, labels = self._GetChannelsAndLabels()
        if channels == []:
            result = sumpf.Signal(samplingrate=self._input.GetSamplingRate())
        else:
            result = sumpf.Signal(channels=channels, samplingrate=self._input.GetSamplingRate(), labels=labels)
        return result



class SplitSpectrum(SplitChannelData):
    """
    This class makes it possible to select certain channels of a Spectrum
    instance and create a new Spectrum from them.

    The selection of the output channels can be specified in three different ways:
     - By passing the flag SplitSpectrum.ALL to the SetOutputChannels method.
    This way, the output Spectrum will have the same channels as the input Spectrum.
     - By passing an integer index to the SetOutputChannels method. This way,
    the output Spectrum will have only the channel with the given index from the
    input Spectrum.
     - By passing a list of integer indexes to the SetOutputChannels method. This
    way, the output Spectrum will have all the channels from the input Spectrum
    whose index is in the given list. Often that list can be generated with the
    range function (e.g. range(7)[4:6]).
    """
    def __init__(self, data=None, channels=[]):
        """
        @param data: the input Spectrum, from which the channels shall be taken
        @param channels: the indexes of the selected channels that shall be in the output Spectrum
        """
        if data is None:
            data = sumpf.Spectrum()
        SplitChannelData.__init__(self, data, channels)

    @sumpf.Input(sumpf.Spectrum, ["GetOutput", "GetNumberOfOutputChannels"])
    def SetInput(self, data):
        """
        Sets the Spectrum from which the channels are taken.
        @param data: the input Spectrum, from which the channels shall be taken
        """
        SplitChannelData.SetInput(self, data)

    @sumpf.Output(sumpf.Spectrum)
    def GetOutput(self):
        """
        Creates and returns an output Spectrum which has only the selected channels.
        @retval : the output Spectrum with only the selected channels
        """
        channels, labels = self._GetChannelsAndLabels()
        if channels == []:
            result = sumpf.Spectrum(resolution=self._input.GetResolution())
        else:
            result = sumpf.Spectrum(channels=channels, resolution=self._input.GetResolution(), labels=labels)
        return result

