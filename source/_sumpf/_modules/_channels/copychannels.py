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


class CopyChannelDataChannels(object):
    """
    Copies the channels of an input data set to create an output data set with a
    given number of channels.
    """
    def __init__(self, input, channelcount):
        """
        @param data: the input data set
        @param channelcount: the integer number of channels of the output data set
        """
        self._input = input
        self.__SetChannelCount(channelcount)

    def GetOutput(self):
        """
        Virtual method whose overrides shall generate and return the output data set.
        @retval : the output data set
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def _GetChannelsAndLabels(self):
        """
        Creates the copied channels and their labels and returns them as a tuple of tuples.
        @retval : a tuple (a, b), where a is a tuple of channels and b is a tuple of labels
        """
        inputchannels = self._input.GetChannels()
        inputlabels = self._input.GetLabels()
        outputchannels = []
        outputlabels = []
        for i in range(self.__channelcount):
            outputchannels.append(inputchannels[i % len(inputchannels)])
            label = inputlabels[i % len(inputchannels)]
            if label is None:
                outputlabels.append(None)
            else:
                outputlabels.append(" ".join([label, str(i // len(inputchannels) + 1)]))
        return (outputchannels, outputlabels)

    def SetInput(self, input):
        """
        Sets the input data set.
        @param data: the input data set
        """
        self._input = input

    @sumpf.Input(int, "GetOutput")
    def SetChannelCount(self, channelcount):
        """
        Sets the number of channels of the output data set.
        If the input data set has multiple channels, all the channels will be
        copied until the channel count is reached.
        An example:
            input channels := A, B, C
            channel count := 8
            output channels := A, B, C, A, B, C, A, B
        @param channelcount: the integer number of channels of the output data set
        """
        self.__SetChannelCount(channelcount)

    def __SetChannelCount(self, channelcount):
        """
        A private helper method to avoid, that the connector SetChannelCount is
        called in the constructor.
        @param channelcount: the integer number of channels of the output data set
        """
        channelcount = int(channelcount)
        if channelcount >= 1:
            self.__channelcount = channelcount
        else:
            raise ValueError("A channel count smaller than one is not possible")



class CopySignalChannels(CopyChannelDataChannels):
    """
    Copies the channels of an input Signal to create an output Signal with a
    given number of channels.

    If the Signal has multiple channels, all these channels will be copied in
    the correct order. This order will be repeated if necessary until the desired
    channel count is reached.
    This means that an output Signal with less channels than the input Signal
    is possible. Although it is recommended to use a SplitSignal instance for
    this purpose.

    For example:
    input channels = c1, c2, c3; desired number of output channels = 5
    => output channels = c1, c2, c3, c1, c2
    input channels = c1, c2, c3; desired number of output channels = 2
    => output channels = c1, c2
    """
    def __init__(self, input=None, channelcount=1):
        """
        @param data: the input Signal
        @param channelcount: the integer number of channels of the output Signal
        """
        if input is None:
            input = sumpf.Signal()
        CopyChannelDataChannels.__init__(self, input, channelcount)

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Generates and returns the output Signal.
        @retval : the output Signal
        """
        channels, labels = self._GetChannelsAndLabels()
        return sumpf.Signal(channels=channels, samplingrate=self._input.GetSamplingRate(), labels=labels)

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, input):
        """
        Sets the input Signal.
        @param data: the input Signal
        """
        CopyChannelDataChannels.SetInput(self, input)



class CopySpectrumChannels(CopyChannelDataChannels):
    """
    Copies the channels of an input Spectrum to create an output Spectrum with a
    given number of channels.

    If the Spectrum has multiple channels, all these channels will be copied in
    the correct order. This order will be repeated if necessary until the desired
    channel count is reached.
    This means that an output Spectrum with less channels than the input Spectrum
    is possible. Although it is recommended to use a SplitSpectrum instance for
    this purpose.

    For example:
    input channels = c1, c2, c3; desired number of output channels = 5
    => output channels = c1, c2, c3, c1, c2
    input channels = c1, c2, c3; desired number of output channels = 2
    => output channels = c1, c2
    """
    def __init__(self, input=None, channelcount=1):
        """
        All parameters are optional.
        @param data: the input Spectrum
        @param channelcount: the integer number of channels of the output Spectrum
        """
        if input is None:
            input = sumpf.Spectrum()
        CopyChannelDataChannels.__init__(self, input, channelcount)

    @sumpf.Output(sumpf.Spectrum)
    def GetOutput(self):
        """
        Generates and returns the output Spectrum.
        @retval : the output Spectrum
        """
        channels, labels = self._GetChannelsAndLabels()
        return sumpf.Spectrum(channels=channels, resolution=self._input.GetResolution(), labels=labels)

    @sumpf.Input(sumpf.Spectrum, "GetOutput")
    def SetInput(self, input):
        """
        Sets the input Spectrum.
        @param data: the input Spectrum
        """
        CopyChannelDataChannels.SetInput(self, input)

