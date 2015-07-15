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

import collections
import sumpf
from .signalgenerator import SignalGenerator

def NOP(t):
    """
    A function that always returns zero. This function is used as the default
    function for the ArbitrarySignalGenerator class.
    """
    return 0.0



class ArbitrarySignalGenerator(SignalGenerator):
    """
    A class for generating a Signal from an arbitrary time function. The given
    function must accept a time value as a parameter and return the sample of the
    Signal's channel at that point in time.
    Furthermore, a label can be specified for the generated Signal's channel.
    There can be only one function specified per instance of this class. Consequently,
    the generated Signal will have only one channel.
    """
    def __init__(self, function=NOP, label="Arbitrary", samplingrate=None, length=None):
        """
        @param function: the time function that returns a sample value for the given point in time
        @param label: the label for the generated Signal's channel as a string
        @param samplingrate: the sampling rate in Hz as a float
        @param length: the number of samples of the signal as an integer
        """
        SignalGenerator.__init__(self, samplingrate=samplingrate, length=length)
        self.__function = function
        self.__label = label

    def _GetSample(self, t):
        """
        Calculates and returns the value of the sample at time t.
        @param t: the time from the beginning of the signal in seconds
        @retval : the value of the impulse function at the given time
        """
        return self.__function(t)

    def _GetLabel(self):
        """
        Returns the label for the generated channel.
        @retval : the string label
        """
        return self.__label

    @sumpf.Input(collections.Callable, "GetSignal")
    def SetFunction(self, function):
        """
        Sets the function that shall be sampled.
        The given function must accept a time value as a parameter and return the
        sample of the Signal's channel at that point in time.
        @param function: the time function that returns a sample value for the given point in time
        """
        self.__function = function

    @sumpf.Input(str, "GetSignal")
    def SetLabel(self, label):
        """
        Sets the label for the generated channel.
        @param label: the label for the generated Signal's channel as a string
        """
        self.__label = label

