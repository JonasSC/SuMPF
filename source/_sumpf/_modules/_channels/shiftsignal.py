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


class ShiftSignal(object):
    """
    A Module for shifting the samples of a Signal.
    A positive shift will delay the Signal, while a negative shift will shift the
    Signal towards its beginning.
    The Signal can be either shifted circularly or it can be filled with zeros.
    The output Signal will have the same length as the input Signal.
    """
    def __init__(self, signal=None, shift=0, circular=True):
        """
        @param signal: the Signal that shall be shifted
        @param shift: the number of samples by which the Signal shall be shifted. Negative numbers will shift the Signal backwards
        @param circular: True if the Signal shall be shifted circularly, False if the shifted Signal shall be filled with 0.0s.
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
        self.__shift = shift
        self.__circular = circular

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        """
        Sets the input Signal.
        @param signal: a Signal instance
        """
        self.__signal = signal

    @sumpf.Input(int, "GetOutput")
    def SetShift(self, shift):
        """
        Sets the number of samples by which the Signal shall be shifted.
        A positive shift will delay the Signal, while a negative shift will shift
        the Signal towards its beginning.
        @param shift: the number of samples by which the Signal shall be shifted
        """
        self.__shift = shift

    @sumpf.Input(bool, "GetOutput")
    def SetCircular(self, circular):
        """
        @param circular: True if the Signal shall be shifted circularly, False if the shifted Signal shall be filled with 0.0s.
        """
        self.__circular = circular

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Creates and returns the shifted Signal.
        @retval : the shifted Signal
        """
        result = self.__signal
        if self.__shift < 0:
            if self.__circular:
                shift = (-self.__shift) % len(self.__signal)
                kept = tuple(c[shift:] for c in self.__signal.GetChannels())
                wrapped = tuple(c[0:shift] for c in self.__signal.GetChannels())
                channels = tuple(k + w for k, w in zip(kept, wrapped))
            else:
                kept = tuple(c[-self.__shift:] for c in self.__signal.GetChannels())
                wrapped = (0.0,) * min(-self.__shift, len(self.__signal))
                channels = tuple(k + wrapped for k in kept)
            result = sumpf.Signal(channels=tuple(channels), samplingrate=self.__signal.GetSamplingRate(), labels=self.__signal.GetLabels())
        elif self.__shift > 0:
            if self.__circular:
                shift = self.__shift % len(self.__signal)
                kept = tuple(c[0:-shift] for c in self.__signal.GetChannels())
                wrapped = tuple(c[-shift:] for c in self.__signal.GetChannels())
                channels = tuple(w + k for k, w in zip(kept, wrapped))
            else:
                kept = tuple(c[0:-self.__shift] for c in self.__signal.GetChannels())
                wrapped = (0.0,) * min(self.__shift, len(self.__signal))
                channels = tuple(wrapped + k for k in kept)
            result = sumpf.Signal(channels=tuple(channels), samplingrate=self.__signal.GetSamplingRate(), labels=self.__signal.GetLabels())
        return result

