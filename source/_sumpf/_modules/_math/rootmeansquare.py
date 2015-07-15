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

import numpy
import sumpf


class RootMeanSquare(object):
    """
    A module for calculating the RMS value for a given Signal.
    The output will be a Signal with the same length as the input Signal.
    Each sample of the output Signal sits in the middle of the integration
    interval over which the respective RMS value is calculated.

    When the input Signal does not overlap the integration interval completely,
    the not overlapped samples are assumed to be 0.0. This leads to an attack
    time at the beginning of the output Signal and a decay time at its end.
    These times have a length of integration_time/2.

    The integration time can be given as a value in seconds or as one of the
    following flags:
    RootMeanSquare.FAST for an integration time of 125ms
    RootMeanSquare.SLOW for an integration time of 1s
    RootMeanSquare.FULL for an integration over the whole signal

    There is a difference between an integration time which is as long as the
    input Signal and RootMeanSquare.FULL.
    FULL means that the output Signal has no dynamic at all. All samples are set
    to the RMS value of the respective channel.
    An integration time which is as long as the signal leads to some ripple at
    the beginning and at the end of the output Signal, as the integration
    interval does not only span parts of the input Signal but also samples
    outside the Signal which are assumed to be 0.0.
    """

    # These flags can be given as integration times
    FAST = 0.125    # an integration time of 125ms
    SLOW = 1.0      # an integration time of 1s
    FULL = None     # integrate over the full signal

    def __init__(self, signal=None, integration_time=None):
        """
        @param signal: the input Signal
        @param integration_time: the length of the integration interval in seconds or a flag like RootMeanSquare.FAST/.SLOW/.FULL
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
        if integration_time is None:
            self.__integration_time = RootMeanSquare.FULL
        else:
            self.__integration_time = float(integration_time)

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        """
        Sets the input Signal
        @param signal: the input Signal
        """
        self.__signal = signal

    @sumpf.Input(float, "GetOutput")
    def SetIntegrationTime(self, integration_time):
        """
        Sets the time over which shall be integrated.
        The integration time can be given as a value in seconds or as one of the
        following flags:
        RootMeanSquare.FAST for an integration time of 125ms
        RootMeanSquare.SLOW for an integration time of 1s
        RootMeanSquare.FULL for an integration over the whole signal
        Please note that there is a difference between the FULL flag and an
        integration time which is as long as the Signal. This is explained in
        the documentation of the RootMeanSquare class.
        @param integration_time: the length of the integration interval in seconds or a flag like RootMeanSquare.FAST/.SLOW/.FULL
        """
        self.__integration_time = float(integration_time)

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Returns the output Signal.
        That output Signal has the same length as the input Signal. Each sample
        gives the RMS value of the Signal at the respective point in time.
        @retval : a Signal containing the RMS values
        """
        result = []
        if self.__integration_time is RootMeanSquare.FULL:
            for c in self.__signal.GetChannels():
                result.append(self.__Full(c))
        else:
            for c in self.__signal.GetChannels():
                result.append(self.__GetRMS(c))
        return sumpf.Signal(channels=result, samplingrate=self.__signal.GetSamplingRate(), labels=self.__signal.GetLabels())

    def __Full(self, channel):
        """
        A private helper method to calculate the RMS value of the full channel
        of the input Signal.
        @param channel: a channel of the input Signal (a tuple of samples)
        @retval : the respective channel of the output Signal (also a tuple of samples)
        """
        squaresum = 0.0
        for s in channel:
            squaresum += s * s
        mean = squaresum / len(channel)
        root = mean ** 0.5
        return [root] * len(channel)

    def __GetRMS(self, channel):
        """
        A private helper method to calculate the dynamic RMS values of the given
        channel from the input Signal.
        @param channel: a channel of the input Signal (a tuple of samples)
        @retval : the respective channel of the output Signal (also a tuple of samples)
        """
        fcount = self.__signal.GetSamplingRate() * self.__integration_time
        count = int(fcount)
        boundary_weight = (fcount - count) / 2.0
        if boundary_weight != 0.0:
            count += 2
        func = [1.0 / fcount] * count
        if boundary_weight != 0.0:
            func[0] = boundary_weight / fcount
            func[-1] = boundary_weight / fcount
        square = numpy.multiply(channel, channel)
        mean = numpy.convolve(a=square, v=func, mode="same")
        result = []
        for i in range(len(channel)):
            result.append(mean[i] ** 0.5)
        return result

