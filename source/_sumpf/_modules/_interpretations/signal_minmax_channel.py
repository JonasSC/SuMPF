# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2018 Jonas Schulte-Coerne
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


class SignalMinimumChannel(object):
    def __init__(self, signal=None):
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal

    @sumpf.Output(sumpf.Signal)
    def GetMinimum(self):
        return sumpf.Signal(channels=(numpy.min(self.__signal.GetChannels(), axis=0),),
                            samplingrate=self.__signal.GetSamplingRate(),
                            labels=self.__signal.GetLabels())

    @sumpf.Input(sumpf.Signal, "GetMinimum")
    def SetSignal(self, signal):
        self.__signal = signal


class SignalMaximumChannel(object):
    def __init__(self, signal=None):
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal

    @sumpf.Output(sumpf.Signal)
    def GetMaximum(self):
        return sumpf.Signal(channels=(numpy.max(self.__signal.GetChannels(), axis=0),),
                            samplingrate=self.__signal.GetSamplingRate(),
                            labels=self.__signal.GetLabels())

    @sumpf.Input(sumpf.Signal, "GetMaximum")
    def SetSignal(self, signal):
        self.__signal = signal

