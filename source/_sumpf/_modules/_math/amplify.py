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
import collections

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy



class AmplifyChannelData(object):
    """
    Abstract base class for amplifying ChannelData instances.
    """
    def __init__(self, input=None, factor=1.0):
        """
        @param input: an optional data set that shall be amplified
        @param factor: the optional amplification factor
        """
        self._input = input
        self.__factor = factor

    @sumpf.Input((float, tuple), "GetOutput")
    def SetAmplificationFactor(self, factor):
        """
        Sets the amplification factor(s).
        The amplification factor can either be a float or a tuple of floats.
        If one float is given, all channels will be amplified by the same factor,
        while a tuple can define a separate factor for each channel.
        If the tuple has less entries than the input data set has channels, the
        first entry in the tuple will be taken as only amplification factor.
        @param factor: the amplification factor as a float or a tuple of floats.
        """
        if not isinstance(factor, collections.Iterable):
            self.__factor = float(factor)
        else:
            self.__factor = factor

    def SetInput(self, input):
        """
        Virtual method whose overrides the input data set.
        It is necessary to implement this method in a derived class, so that the
        type of the Input can be set correctly.
        @param input: the data set that shall be amplified
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def GetOutput(self):
        """
        Virtual method whose overrides shall return the amplified data set.
        @retval : the amplified data set
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def _GetChannels(self):
        """
        Calculates the amplified channels and returns them.
        @retval : a tuple of channels which themselves are a tuple of samples
        """
        def scalar(dataset, factor):
            result = []
            for c in dataset.GetChannels():
                channel = tuple(numpy.multiply(c, factor))
                result.append(channel)
            return result
        def vectorial(dataset, factors):
            result = []
            for i in range(len(dataset.GetChannels())):
                channel = tuple(numpy.multiply(dataset.GetChannels()[i], factors[i]))
                result.append(channel)
            return result
        if isinstance(self.__factor, collections.Iterable):
            if len(self.__factor) >= len(self._input.GetChannels()):
                return vectorial(dataset=self._input, factors=self.__factor)
            else:
                return scalar(dataset=self._input, factor=self.__factor[0])
        else:
            return scalar(dataset=self._input, factor=self.__factor)



class AmplifySignal(AmplifyChannelData):
    """
    Module for amplifying Signal data.
    The resulting Signal is calculated by multiplying each sample of the Signal
    with the amplification factor. The meta data of the Signal is not changed.
    """
    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, input):
        """
        Sets the input Signal that shall be amplified
        @param input: the Signal that shall be amplified
        """
        self._input = input

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Calculates the amplified Signal and returns it.
        @retval : the amplified Signal
        """
        signal = None
        if self._input is None:
            signal = sumpf.Signal()
        else:
            try:
                signal = sumpf.Signal(channels=self._GetChannels(), samplingrate=self._input.GetSamplingRate(), labels=self._input.GetLabels())
            except ValueError:
                signal = sumpf.Signal(samplingrate=self._input.GetSamplingRate())
        return signal



class AmplifySpectrum(AmplifyChannelData):
    """
    Module for amplifying Spectrum data.
    The resulting Spectrum is calculated by multiplying each sample of the Spectrum
    with the amplification factor. The phase or the meta data of the Spectrum is
    not changed.
    """
    @sumpf.Input(sumpf.Spectrum, "GetOutput")
    def SetInput(self, input):
        """
        Sets the input Spectrum that shall be amplified
        @param input: the Spectrum that shall be amplified
        """
        self._input = input

    @sumpf.Output(sumpf.Spectrum)
    def GetOutput(self):
        """
        Calculates the amplified Spectrum and returns it.
        @retval : the amplified Spectrum
        """
        spectrum = None
        if self._input is None:
            spectrum = sumpf.Spectrum()
        else:
            try:
                spectrum = sumpf.Spectrum(channels=self._GetChannels(), resolution=self._input.GetResolution(), labels=self._input.GetLabels())
            except ValueError:
                spectrum = sumpf.Spectrum(resolution=self._input.GetResolution())
        return spectrum

