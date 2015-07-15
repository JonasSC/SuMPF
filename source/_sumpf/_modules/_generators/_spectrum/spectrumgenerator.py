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


class SpectrumGenerator(object):
    """
    An abstract base class for classes whose instances generate Spectrums.
    The generated Spectrums have always one channel.
    Every derived generator must implement either the _GetSample or the
    _GetSamples method.
    """
    def __init__(self, resolution=None, length=None):
        """
        @param resolution: the resolution of the created spectrum in Hz
        @param length: the number of samples of the spectrum
        """
        if resolution is None:
            self._resolution = sumpf.modules.ChannelDataProperties().GetResolution()
        else:
            self._resolution = resolution
        if length is None:
            self._length = sumpf.modules.ChannelDataProperties().GetSpectrumLength()
        else:
            self._length = int(length)

    @sumpf.Output(sumpf.Spectrum)
    def GetSpectrum(self):
        """
        Generates a Spectrum instance and returns it.
        @retval : the generated Spectrum
        """
        return sumpf.Spectrum(channels=(self._GetSamples(),), resolution=self._resolution, labels=(self._GetLabel(),))

    def _GetSamples(self):
        """
        This method can be overridden in derived classes if the _GetSample-method
        is not versatile enough.
        Generates the samples of a Spectrum with a maximum amplitude of 1 and
        returns them as a tuple.
        @retval : a tuple of samples
        """
        samples = []
        for i in range(self._length):
            f = float(i) * float(self._resolution)
            samples.append(self._GetSample(f))
        return tuple(samples)

    def _GetSample(self, f):
        """
        This method can be implemented in derived classes to define the Spectrum
        generator function.
        This method shall generate a sample at the frequency f and return it.
        @param f: the frequency of the sample in Hz
        @retval : the value of the generator function at the given frequency
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def _GetLabel(self):
        """
        Virtual base method whose override shall return a label for the output
        Spectrum's channel.
        @retval : a string label
        """
        return ""

    @sumpf.Input(float, "GetSpectrum")
    def SetResolution(self, resolution):
        """
        Sets the frequency resolution of the output Spectrum.
        @param resolution: the resolution of the created spectrum in Hz
        """
        self._resolution = float(resolution)

    @sumpf.Input(int, "GetSpectrum")
    def SetLength(self, length):
        """
        Sets the length of the output Spectrum.
        @param length: the number of samples of the Spectrum
        """
        self._length = int(length)

    @sumpf.Input(float, "GetSpectrum")
    def SetMaximumFrequency(self, frequency):
        """
        Convenience method that sets the output spectrum's length according
        to its maximum frequency.
        Make sure that the resolution does not change after calling this method,
        as this changes the maximum frequency as well.
        @param frequency: the maximum frequency of the spectrum
        """
        self._length = int(round(float(frequency) / self._resolution))

