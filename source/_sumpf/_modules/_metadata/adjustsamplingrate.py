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

import sumpf


class AdjustSamplingRate(object):
    """
    Creates a Signal from an input signal, where the sampling rate is replaced
    with a given value. Contrary to the ResampleSignal class, no resampling of
    the Signal's data is being done.
    """
    def __init__(self, signal=None, samplingrate=None):
        """
        @param signal: a Signal instance
        @param samplingrate: the sampling rate of the output signal as a float
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
        if samplingrate is None:
            self.__samplingrate = sumpf.config.get("default_samplingrate")
        else:
            self.__samplingrate = samplingrate

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetSignal(self, signal):
        """
        Sets the signal, whose data shall be taken for the output Signal.
        @param signal: a Signal instance
        """
        self._label_input = input

    @sumpf.Input(float, "GetOutput")
    def SetSamplingRate(self, samplingrate):
        """
        Specifies the sampling rate of the output Signal
        @param samplingrate: the sampling rate of the output signal as a float
        """
        self.__samplingrate = samplingrate

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Creates and returns the output Signal.
        @retval : a Signal instance
        """
        return sumpf.Signal(channels=self.__signal.GetChannels(),
                            samplingrate=self.__samplingrate,
                            labels=self.__signal.GetLabels())

