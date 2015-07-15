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



class SignalVariance(object):
    """
    Calculates the variance for each channel of a Signal instance. The values
    are returned as a tuple of floats.
    """
    def __init__(self, signal=None):
        """
        @param signal: the Signal instance for which the variance values shall be calculated
        """
        if signal is None:
            signal = sumpf.Signal()
        self.__signal = signal

    @sumpf.Input(sumpf.Signal, "GetVariance")
    def SetSignal(self, signal):
        """
        Sets the Signal for which the variance values shall be calculated.
        @param signal: the Signal instance for which the variance values shall be calculated
        """
        self.__signal = signal

    @sumpf.Output(tuple)
    def GetVariance(self):
        """
        Calculates and returns a tuple of variance values. One value for each channel
        of the input Signal.
        @retval : a tuple of variance values
        """
        result = []
        for c in self.__signal.GetChannels():
            result.append(numpy.var(c))
        return tuple(result)

