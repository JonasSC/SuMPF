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


class SignalAlgebra(object):
    """
    A base class for calculations with two Signal instances.
    """
    def __init__(self, signal1=None, signal2=None):
        """
        All parameters are optional
        @param signal1: the first Signal-instance for the calculation
        @param signal2: the second Signal-instance for the calculation
        """
        if signal1 is None:
            self.__signal1 = sumpf.Signal()
        else:
            self.__signal1 = signal1
        if signal2 is None:
            self.__signal2 = sumpf.Signal()
        else:
            self.__signal2 = signal2

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput1(self, signal):
        """
        Sets the first Signal for the calculation.
        @param signal: the first Signal-instance for the calculation
        """
        self.__signal1 = signal

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput2(self, signal):
        """
        Sets the second Signal for the calculation.
        @param signal: the second Signal-instance for the calculation
        """
        self.__signal2 = signal

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Calculates and returns the Signal resulting from the calculation.
        Before the calculation, the input Signals are checked for compatibility.
        If the Signals are incompatible and both not empty, a ValueError is raised.
        If the Signals are incompatible and one Signal is empty, an empty Signal
        is returned.
        @retval : a Signal whose channels are the result of the calculation
        """
        signal1 = self.__signal1
        signal2 = self.__signal2
        if signal1.GetSamplingRate() != signal2.GetSamplingRate():
            if signal1.IsEmpty() or signal2.IsEmpty():
                return sumpf.Signal()
            else:
                raise ValueError("The Signals do not have the same sampling rate (Signal1: %f, Signal2: %f)" % (signal1.GetSamplingRate(), signal2.GetSamplingRate()))
        elif len(signal1.GetChannels()) != len(signal2.GetChannels()):
            if signal1.IsEmpty() or signal2.IsEmpty():
                return sumpf.Signal(samplingrate=signal1.GetSamplingRate())
            else:
                raise ValueError("The Signals do not have the same number of channels (Signal1: %i, Signal2: %i)" % (len(signal1.GetChannels()), len(signal2.GetChannels())))
        elif len(signal1) != len(signal2):
            if signal1.IsEmpty() or signal2.IsEmpty():
                return sumpf.Signal(channels=((0.0, 0.0),) * len(signal1.GetChannels()), samplingrate=signal1.GetSamplingRate())
            else:
                raise ValueError("The Signals do not have the same length (Signal1: %i, Signal2: %i)" % (len(signal1), len(signal2)))
        else:
            return self._Calculate(signal1, signal2)

    def _Calculate(self, signal1, signal2):
        """
        Abstract method that shall be overwritten with the actual calculation.
        @param signal1: the first Signal for the calculation
        @param signal2: the second Signal for the calculation
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

