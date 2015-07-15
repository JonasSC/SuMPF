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


class ReverseSignal(object):
    """
    Reverses a Signal's channels, so they begin with their last sample and end
    with the first one.
    Use this to look for secret satanic messages in the recordings of your early
    80s Heavy Metal LPs.
    """
    def __init__(self, signal=None):
        """
        @param data: the Signal that shall be reversed
        """
        self.__signal = signal
        if self.__signal is None:
            self.__signal = sumpf.Signal

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Returns the reversed Signal.
        @retval : the reversed Signal
        """
        channels = []
        for c in self.__signal.GetChannels():
            channel = list(c)
            channel.reverse()
            channels.append(tuple(channel))
        return sumpf.Signal(channels=channels, samplingrate=self.__signal.GetSamplingRate(), labels=self.__signal.GetLabels())

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        """
        Sets the Signal that shall be reversed.
        @param data: a Signal instance
        """
        self.__signal = signal

