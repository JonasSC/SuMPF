# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2016 Jonas Schulte-Coerne
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
import _common as common


class TestCopyChannels(unittest.TestCase):
    """
    Tests the CopySignalChannels and CopySpectrumChannels modules.
    """
    def test_copy_signal_channels(self):
        """
        Tests the CopySignalChannels module.
        """
        channels = ((1.1, 2.1, 3.1), (1.2, 2.2, 3.2))
        signal = sumpf.Signal(channels=channels, samplingrate=42.0, labels=("ch 1", None))
        copysignal = sumpf.modules.CopySignalChannels()
        copysignal.SetSignal(signal)
        # test setting the channel count to an integer
        copysignal.SetChannelCount(3)
        output = copysignal.GetOutput()
        self.assertEqual(output.GetSamplingRate(), 42)                                              # the sampling rate should have been copied from the input Signal
        self.assertEqual(output.GetChannels(), ((1.1, 2.1, 3.1), (1.2, 2.2, 3.2), (1.1, 2.1, 3.1))) # the channels should have been copied as expected
        self.assertEqual(output.GetLabels(), ("ch 1 1", None, "ch 1 2"))                            # the labels should have been copied as expected
        copysignal.SetChannelCount(1)
        self.assertEqual(copysignal.GetOutput().GetChannels(), ((1.1, 2.1, 3.1),))                  # reducing the number of output channels should also work
        # test getting the channel count from a ChannelData instance
        copysignal.SetChannelCount(sumpf.Signal(channels=((0.0, 0.0), (1.0, 1.0), (2.0, 2.0))))
        self.assertEqual(copysignal.GetOutput().GetChannels(), channels + channels[0:1])
        copysignal.SetChannelCount(sumpf.Spectrum(channels=((0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0))))
        self.assertEqual(copysignal.GetOutput().GetChannels(), channels + channels)

    def test_copy_spectrum_channels(self):
        """
        Tests the CopySpectrumChannels module.
        """
        channels = ((1.1, 2.1, 3.1), (1.2, 2.2, 3.2))
        spectrum = sumpf.Spectrum(channels=channels, resolution=42.0, labels=("ch 1", "ch 2"))
        copyspectrum = sumpf.modules.CopySpectrumChannels()
        copyspectrum.SetSpectrum(spectrum)
        copyspectrum.SetChannelCount(3)
        output = copyspectrum.GetOutput()
        self.assertEqual(output.GetResolution(), 42)                                                # the sampling rate should have been copied from the input Spectrum
        self.assertEqual(output.GetChannels(), ((1.1, 2.1, 3.1), (1.2, 2.2, 3.2), (1.1, 2.1, 3.1))) # the channels should have been copied as expected
        self.assertEqual(output.GetLabels(), ("ch 1 1", "ch 2 1", "ch 1 2"))                        # the labels should have been copied as expected
        copyspectrum.SetChannelCount(1)
        self.assertEqual(copyspectrum.GetOutput().GetChannels(), ((1.1, 2.1, 3.1),))                # reducing the number of output channels should also work
        # test getting the channel count from a ChannelData instance
        copyspectrum.SetChannelCount(sumpf.Signal(channels=((0.0, 0.0), (1.0, 1.0), (2.0, 2.0))))
        self.assertEqual(copyspectrum.GetOutput().GetChannels(), channels + channels[0:1])
        copyspectrum.SetChannelCount(sumpf.Spectrum(channels=((0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0))))
        self.assertEqual(copyspectrum.GetOutput().GetChannels(), channels + channels)

    def test_errors(self):
        """
        Tests if errors are raised as expected.
        """
        copysignal = sumpf.modules.CopySignalChannels()
        self.assertRaises(ValueError, copysignal.SetChannelCount, 0)    # a channel count of 0 should be forbidden
        copyspectrum = sumpf.modules.CopySpectrumChannels()
        self.assertRaises(ValueError, copyspectrum.SetChannelCount, -1) # a negative channel count should be forbidden

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        # CopySignalChannels
        copysignal = sumpf.modules.CopySignalChannels()
        self.assertEqual(copysignal.SetSignal.GetType(), sumpf.Signal)
        self.assertEqual(copysignal.SetChannelCount.GetType(), (int, sumpf.internal.ChannelData))
        self.assertEqual(copysignal.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[copysignal.SetSignal, copysignal.SetChannelCount],
                                         noinputs=[],
                                         output=copysignal.GetOutput)
        # CopySpectrumChannels
        copyspectrum = sumpf.modules.CopySpectrumChannels()
        self.assertEqual(copyspectrum.SetSpectrum.GetType(), sumpf.Spectrum)
        self.assertEqual(copyspectrum.SetChannelCount.GetType(), (int, sumpf.internal.ChannelData))
        self.assertEqual(copyspectrum.GetOutput.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[copyspectrum.SetSpectrum, copyspectrum.SetChannelCount],
                                         noinputs=[],
                                         output=copyspectrum.GetOutput)

