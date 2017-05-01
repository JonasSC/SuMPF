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


class CopyChannelDataChannels(object):
    """
    Copies the channels of an input data set to create an output data set with a
    given number of channels.
    """
    def __init__(self, data, channelcount):
        """
        @param data: the input data set
        @param channelcount: the integer number of channels of the output data set
        """
        self._data = data
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
        inputchannels = self._data.GetChannels()
        inputlabels = self._data.GetLabels()
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

    @sumpf.Input((int, sumpf.internal.ChannelData), "GetOutput")
    def SetChannelCount(self, channelcount):
        """
        Sets the number of channels of the output data set.
        This can be done either by specifying the integer number of channels or
        by passing a ChannelData instance (e.g. Signal or Spectrum), whose channel
        count will be used.
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
        if isinstance(channelcount, sumpf.internal.ChannelData):
            channelcount = len(channelcount.GetChannels())
        else:
            channelcount = int(channelcount)
        if channelcount >= 1:
            self.__channelcount = channelcount
        else:
            raise ValueError("A channel count smaller than one is not possible")



class CopySignalChannels(CopyChannelDataChannels):
    """
    Copies the channels of an input Signal to create an output Signal with a
    given number of channels.

    The number of channels can either be specified as an integer number or by
    passing a ChannelData instance (e.g. Signal or Spectrum), whose channel count
    will be used.

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
    def __init__(self, signal=None, channelcount=1):
        """
        @param signal: the input Signal
        @param channelcount: the integer number of channels of the output Signal
        """
        if signal is None:
            signal = sumpf.Signal()
        CopyChannelDataChannels.__init__(self, data=signal, channelcount=channelcount)

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Generates and returns the output Signal.
        @retval : the output Signal
        """
        channels, labels = self._GetChannelsAndLabels()
        return sumpf.Signal(channels=channels, samplingrate=self._data.GetSamplingRate(), labels=labels)

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetSignal(self, signal):
        """
        Sets the input Signal.
        @param signal: the input Signal
        """
        self._data = signal



class CopySpectrumChannels(CopyChannelDataChannels):
    """
    Copies the channels of an input Spectrum to create an output Spectrum with a
    given number of channels.

    The number of channels can either be specified as an integer number or by
    passing a ChannelData instance (e.g. Signal or Spectrum), whose channel count
    will be used.

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
    def __init__(self, spectrum=None, channelcount=1):
        """
        All parameters are optional.
        @param spectrum: the input Spectrum
        @param channelcount: the integer number of channels of the output Spectrum
        """
        if spectrum is None:
            spectrum = sumpf.Spectrum()
        CopyChannelDataChannels.__init__(self, data=spectrum, channelcount=channelcount)

    @sumpf.Output(sumpf.Spectrum)
    def GetOutput(self):
        """
        Generates and returns the output Spectrum.
        @retval : the output Spectrum
        """
        channels, labels = self._GetChannelsAndLabels()
        return sumpf.Spectrum(channels=channels, resolution=self._data.GetResolution(), labels=labels)

    @sumpf.Input(sumpf.Spectrum, "GetOutput")
    def SetSpectrum(self, spectrum):
        """
        Sets the input Spectrum.
        @param spectrum: the input Spectrum
        """
        self._data = spectrum

