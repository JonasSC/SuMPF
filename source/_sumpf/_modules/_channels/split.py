# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2017 Jonas Schulte-Coerne
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
    # flags for the channels parameter
    ALL = None  # select all channels
    # flags for the on_invalid_index parameter
    ERROR = 0   # raise an IndexError
    SKIP = 1    # skip that channel
    ZEROS = 2   # add a channel with zeros

    def __init__(self, data, channels, on_invalid_index):
        """
        @param data: the input data, from which the channels shall be taken
        @param channels: the indexes of the selected channels that shall be in the output data set
        """
        self._input = data
        self.__channels = channels
        self.__on_invalid_index = on_invalid_index

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

    @sumpf.Output(int)
    def GetNumberOfOutputChannels(self):
        """
        Returns the number of channels of the output data set.
        @retval : the number of channels of the output data set as an integer
        """
        length = len(self._input.GetChannels())
        result = 0
        for i in self.__channels:
            if i < length or self.__on_invalid_index == SplitChannelData.ZEROS:
                result += 1
        return max(result, 1)

    @sumpf.Input(tuple, ("GetOutput", "GetNumberOfOutputChannels"))
    def SetOutputChannels(self, channels):
        """
        Sets the channels of the input data set that shall be copied to the output.
        @param channels: a flag like ALL or an integer or a tuple of integers that are the indexes of the selected input data set's channels
        """
        self.__channels = channels

    @sumpf.Input(int, ("GetOutput", "GetNumberOfOutputChannels"))
    def SetOnInvalidIndex(self, on_invalid_index):
        self.__on_invalid_index = on_invalid_index

    @sumpf.Trigger("GetOutput")
    def DropChannels(self):
        """
        Removes channel indices from the set output channels, that are higher than
        the maximum channel number of the input data set.
        """
        if self.__channels != SplitChannelData.ALL:
            self.__channels = [i for i in self.__channels if i < len(self._input.GetChannels())]

    def _GetChannelsAndLabels(self):
        """
        Creates the channels and labels for the split ChannelData instance and
        returns them as a tuple.
        @retval : a tuple (a, b), where a is a tuple of channels and b is a tuple of labels
        """
        if self.__channels == SplitChannelData.ALL:
            return (self._input.GetChannels(), self._input.GetLabels())
        else:
            if isinstance(self.__channels, int):
                selected = [self.__channels]
            else:
                selected = self.__channels
            channels = []
            labels = []
            length = len(self._input.GetChannels())
            for i in selected:
                if i < length:
                    channels.append(self._input.GetChannels()[i])
                    labels.append(self._input.GetLabels()[i])
                elif self.__on_invalid_index == SplitChannelData.ERROR:
                    raise IndexError("The channel index %s is higher than the input data's number of channels (%s)." % (i, length))
                elif self.__on_invalid_index == SplitChannelData.SKIP:
                    pass
                elif self.__on_invalid_index == SplitChannelData.ZEROS:
                    channels.append((0.0,) * len(self._input))
                    labels.append(None)
                else:
                    raise ValueError("Unknown flag for reacting to invalid indices")
            if len(channels) == 0:  # if no valid channels are selected, return an empty data set
                return ((0.0, 0.0),), (None,)
            else:
                return channels, labels



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
    def __init__(self, data=None, channels=SplitChannelData.ALL, on_invalid_index=SplitChannelData.ERROR):
        """
        @param data: the input Signal, from which the channels shall be taken
        @param channels: the indexes of the selected channels that shall be in the output Signal
        """
        if data is None:
            data = sumpf.Signal()
        SplitChannelData.__init__(self, data, channels, on_invalid_index)

    @sumpf.Input(sumpf.Signal, ("GetOutput", "GetNumberOfOutputChannels"))
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
        if channels == ():
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
    def __init__(self, data=None, channels=SplitChannelData.ALL, on_invalid_index=SplitChannelData.ERROR):
        """
        @param data: the input Spectrum, from which the channels shall be taken
        @param channels: the indexes of the selected channels that shall be in the output Spectrum
        """
        if data is None:
            data = sumpf.Spectrum()
        SplitChannelData.__init__(self, data, channels, on_invalid_index)

    @sumpf.Input(sumpf.Spectrum, ("GetOutput", "GetNumberOfOutputChannels"))
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
        if channels == ():
            result = sumpf.Spectrum(resolution=self._input.GetResolution())
        else:
            result = sumpf.Spectrum(channels=channels, resolution=self._input.GetResolution(), labels=labels)
        return result

