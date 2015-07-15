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



class IntegrateSignal(object):
    """
    A module for calculating the integral of a Signal.
    This is done by summing up the areas of the rectangles that are defined by
    the samples and the sampling rate. This method uses no interpolation between
    the samples.
    """
    NO_DC = None

    def __init__(self, signal=None, offset=0.0):
        """
        @param signal: the input Signal
        @param offset: an float offset that shall be added to the integrated signal, or NO_DC to avoid a dc-offset in the output Signal
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
        self.__offset = offset

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        """
        Sets the input Signal.
        @param signal: the input Signal
        """
        self.__signal = signal

    @sumpf.Input(float, "GetOutput")
    def SetOffset(self, offset):
        """
        Specifies an offset that shall be added to the output Signal's samples.
        This offset can either be given as a float or it can be set to NO_DC in
        which case, the offset of each channel will be chosen so that the average
        of all the channel's samples is zero (this means that the channel has no
        dc-offset).
        @param offset: a float or NO_DC
        """
        self.__offset = offset

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Returns the output Signal, which is the integral of the input Signal.
        @retval : a Signal which is the integral of the input Signal
        """
        result = []
        offset = self.__offset
        for c in self.__signal.GetChannels():
            sample_sum = 0.0
            integrated = []
            for s in c:
                sample_sum += s
                integrated.append(sample_sum)
            scaled = numpy.divide(integrated, self.__signal.GetSamplingRate())
            if self.__offset == IntegrateSignal.NO_DC:
                offset = -sum(scaled) / len(scaled)
            shifted = numpy.add(scaled, offset)
            result.append(tuple(shifted))
        return sumpf.Signal(channels=result, samplingrate=self.__signal.GetSamplingRate(), labels=self.__signal.GetLabels())

