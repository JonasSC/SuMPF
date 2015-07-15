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

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy



class NormalizeSignal(object):
    """
    Scales a Signal so that all its samples are between -1.0 and 1.0.
    Small Signals are amplified until either the maximum sample is 1.0 or the
    minimum sample is -1.0, which ever needs the smaller amplification.
    Large Signals are damped accordingly.
    There will not be an offset, which is added to the Signal to achieve that
    both the maximum and the minimum achieve their respective limits.

    If all samples of a channel are 0.0 that channel will not be normalized to
    avoid divisions by zero.

    Note that this works differently compared to the NormalizeSpectrum module. A
    normalized Signal, which is then fourier transformed does not necessarily
    result in a normalized Spectrum.
    """
    def __init__(self, input=None, individual=False):
        """
        All parameters are optional
        @param input: the Signal which shall be normalized
        @param individual: If True, the channels will be normalized individually. If False the proportion between the channels remains the same
        """
        if input is None:
            input = sumpf.Signal()
        self.__signal = input
        self.__individual = individual

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Generates the normalized Signal and returns it.
        @retval : the normalized Signal
        """
        outputchannels = []
        inputchannels = self.__signal.GetChannels()
        if self.__individual:
            for c in inputchannels:
                outputchannels.append(tuple(numpy.multiply(c, self.__GetFactor(channel=c))))
        else:
            factor = None
            for c in inputchannels:
                factor = self.__GetFactor(channel=c, factor=factor)
            for c in inputchannels:
                outputchannels.append(tuple(numpy.multiply(c, factor)))
        return sumpf.Signal(channels=outputchannels, samplingrate=self.__signal.GetSamplingRate(), labels=self.__signal.GetLabels())

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        """
        Method for setting the Signal which shall be normalized.
        @param signal: the Signal which shall be normalized
        """
        self.__signal = signal

    @sumpf.Input(bool, "GetOutput")
    def SetIndividual(self, individual):
        """
        Sets if the channels shall be normalized individually.
        If True each channel is scaled independently of the other channels of the
        Signal. The proportion between the channels will change.
        If False the global maximum or minimum of all channels will be taken to
        scale the channels. The proportion between the channels will remain the
        same.
        @param individual: the boolean value if the channels shall be normalized individually.
        """
        self.__individual = individual

    def __GetFactor(self, channel, factor=None):
        """
        Calculates and returns the normalization factor for the given channel.
        If the optional parameter factor is not None, the calculated factor is
        only returned if the given factor is larger than the calculated one.
        Otherwise the given factor is returned.
        @param channel: the channel (a tuple of float samples) for which the normalization factor shall be calculated
        @param factor: an optional normalization factor from previous calculations
        @retval : a normalization factor as float
        """
        maximum = max(numpy.abs(channel))
        if factor is None:
            if maximum == 0.0:
                return 1.0
            else:
                return 1.0 / maximum
        else:
            if maximum == 0.0:
                return factor
            else:
                return min(1.0 / maximum, factor)

