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

import unittest
import sumpf


class BaseTestCase(unittest.TestCase):
    """
    An abstract base class for the interactive TestCases for the plot panels.
    """
    def setUp(self):
        # properties
        self.properties = sumpf.modules.ChannelDataProperties(samplingrate=195.6, signal_length=500)
        # one input signal
        sweep = sumpf.modules.SweepGenerator(start_frequency=4.0, stop_frequency=80.0)
        sumpf.connect(self.properties.GetSamplingRate, sweep.SetSamplingRate)
        sumpf.connect(self.properties.GetSignalLength, sweep.SetLength)
        # another input signal
        triangle = sumpf.modules.TriangleWaveGenerator(frequency=10.0)
        sumpf.connect(self.properties.GetSamplingRate, triangle.SetSamplingRate)
        sumpf.connect(self.properties.GetSignalLength, triangle.SetLength)
        # a merger for the input signals
        merger = sumpf.modules.MergeSignals()
        sumpf.connect(sweep.GetSignal, merger.AddInput)
        sumpf.connect(triangle.GetSignal, merger.AddInput)
        # a handle for adjusting the output's number of channels
        self.copy = sumpf.modules.CopySignalChannels(channelcount=2)
        sumpf.connect(merger.GetOutput, self.copy.SetInput)
        # a fourier transform for testing with Spectrums
        self.fft = sumpf.modules.FourierTransform()
        sumpf.connect(self.copy.GetOutput, self.fft.SetSignal)

