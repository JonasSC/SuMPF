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
try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy



class SignalMinimum(object):
    """
    A class for finding the minimum value(s) of a Signal. It is possible to
    retrieve the minima for each channel individually or to find the one global
    minimum.
    """
    def __init__(self, signal=None):
        """
        @param signal: the Signal, in which shall be looked for the minimum value(s)
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal

    @sumpf.Output(tuple)
    def GetMinima(self):
        """
        Returns the minimum values for each channel individually as a tuple.
        @retval : a tuple of floats
        """
        return tuple(min(c) for c in self.__signal.GetChannels())

    @sumpf.Output(float)
    def GetGlobalMinimum(self):
        """
        Returns the minimum sample of the whole signal.
        @retval : a float
        """
        return numpy.min(self.__signal.GetChannels())

    @sumpf.Input(sumpf.Signal, ("GetMinima", "GetGlobalMinimum"))
    def SetSignal(self, signal):
        """
        Sets the Signal, in which shall be looked for the minimum value(s).
        @param signal: a Signal instance
        """
        self.__signal = signal



class SignalMaximum(object):
    """
    A class for finding the maximum value(s) of a Signal. It is possible to
    retrieve the maxima for each channel individually or to find the one global
    maximum.
    """
    def __init__(self, signal=None):
        """
        @param signal: the Signal, in which shall be looked for the maximum value(s)
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal

    @sumpf.Output(tuple)
    def GetMaxima(self):
        """
        Returns the maximum values for each channel individually as a tuple.
        @retval : a tuple of floats
        """
        return tuple(max(c) for c in self.__signal.GetChannels())

    @sumpf.Output(float)
    def GetGlobalMaximum(self):
        """
        Returns the maximum sample of the whole signal.
        @retval : a float
        """
        return numpy.max(self.__signal.GetChannels())

    @sumpf.Input(sumpf.Signal, ("GetMaxima", "GetGlobalMaximum"))
    def SetSignal(self, signal):
        """
        Sets the Signal, in which shall be looked for the maximum value(s).
        @param signal: a Signal instance
        """
        self.__signal = signal

