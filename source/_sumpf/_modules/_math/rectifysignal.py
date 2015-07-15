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



class RectifySignal(object):
    """
    Rectifies a Signal by calculating the absolute value for each sample.
    Output Signals of instances of this class will only have positive samples.
    If you intend to play them back with the sound card, please note they have
    a significant dc offset that needs to be removed first.
    """
    def __init__(self, signal=None):
        """
        @param signal: the input Signal
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        """
        Sets the input Signal.
        @param signal: the input Signal
        """
        self.__signal = signal

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Returns the output Signal, which is the sample wise logarithm of the input
        Signal.
        @retval : the logarithm Signal
        """
        result = []
        for c in self.__signal.GetChannels():
            result.append(tuple(numpy.abs(c)))
        return sumpf.Signal(channels=result, samplingrate=self.__signal.GetSamplingRate(), labels=self.__signal.GetLabels())

