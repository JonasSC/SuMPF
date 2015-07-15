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


class SignalGenerator(object):
    """
    An abstract base class for classes whose instances generate Signals.
    The generated Signals are always Mono.
    Every derived generator must implement either the _GetSample or the
    _GetSamples method.
    """
    def __init__(self, samplingrate=None, length=None):
        """
        @param samplingrate: the sampling rate in Hz
        @param length: the number of samples of the signal
        """
        if samplingrate is None:
            samplingrate = sumpf.config.get("default_samplingrate")
        if length is None:
            length = sumpf.config.get("default_signal_length")
        self._samplingrate = samplingrate
        self._length = int(length)

    @sumpf.Output(sumpf.Signal)
    def GetSignal(self):
        """
        Generates a Signal instance and returns it.
        @retval : the generated Signal
        """
        return sumpf.Signal(channels=(self._GetSamples(),), samplingrate=self._samplingrate, labels=(self._GetLabel(),))

    def _GetSamples(self):
        """
        This method can be overridden in derived classes if the _GetSample-method
        is not versatile enough.
        Generates the samples of a Signal with a maximum amplitude of 1 and
        returns them as a tuple.
        @retval : a tuple of samples
        """
        samples = []
        for i in range(self._length):
            t = float(i) / float(self._samplingrate)
            samples.append(self._GetSample(t))
        return samples

    def _GetSample(self, t):
        """
        This method can be implemented in derived classes to define the Signal generator function.
        This method shall generate a sample at the time t and return it.
        @param t: the time from the beginning of the signal in seconds
        @retval : the value of the generator function at the given time
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def _GetLabel(self):
        """
        Virtual base method whose override shall return a label for the output
        Signal's channel.
        @retval : a string label
        """
        return ""

    @sumpf.Input(float, "GetSignal")
    def SetSamplingRate(self, samplingrate):
        """
        Sets the sampling rate of the output Signal.
        @param samplingrate: the sampling rate in Hz
        """
        self._samplingrate = float(samplingrate)

    @sumpf.Input(int, "GetSignal")
    def SetLength(self, length):
        """
        Sets the length of the output Signal.
        @param length: the number of samples of the signal
        """
        self._length = int(length)

