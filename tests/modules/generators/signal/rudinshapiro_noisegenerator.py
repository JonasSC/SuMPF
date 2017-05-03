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

import math
import unittest
import sumpf
import _common as common


@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestRudinShapiroNoiseGenerator(unittest.TestCase):
    """
    A TestCase for the RudinShapiroNoiseGenerator class.
    """
    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_function(self):
        """
        Tests the functionality of the RudinShapiroNoiseGenerator.
        """
        for start_frequency in(0.0, 70.0):
            for stop_frequency in (None, 5512.5):
                for length in (257, 2 ** 14):
                    for samplingrate in (22050.0, 44100.0):
                        # precompute some values
                        gen = sumpf.modules.RudinShapiroNoiseGenerator(start_frequency, stop_frequency, samplingrate, length)
                        noise = gen.GetSignal()
                        if length % 2 == 0:
                            spectrum = sumpf.modules.FourierTransform(signal=noise).GetSpectrum()
                        else:
                            spectrum = sumpf.modules.FourierTransform(signal=noise[0:-1]).GetSpectrum()
                            self.assertEqual(noise.GetChannels()[0][-1], 0.0)
                        start_index = int(round(start_frequency / spectrum.GetResolution()))
                        if stop_frequency is None:
                            stop_index = len(spectrum)
                        else:
                            stop_index = int(round(stop_frequency / spectrum.GetResolution())) + 1
                        # check the basic properties of the Signal
                        self.assertEqual(len(noise), length)
                        self.assertEqual(noise.GetSamplingRate(), samplingrate)
                        self.assertEqual(noise.GetLabels(), ("Noise",))
                        # check the "whiteness" and the bandwidth of the noise
                        for s in spectrum.GetChannels()[0][0:start_index]:
                            self.assertLess(abs(s), 2e-15)
                        for s in spectrum.GetChannels()[0][start_index:stop_index]:
                            self.assertLess(abs(abs(s) - 1.0), 2e-15)
                        for s in spectrum.GetChannels()[0][stop_index:]:
                            self.assertLess(abs(s), 2e-15)
                        # check the crest factor
                        rms = sumpf.modules.Level(signal=noise).GetLevel()[0]
                        peak = max(sumpf.modules.RectifySignal(signal=noise).GetOutput().GetChannels()[0])
                        self.assertLess(20.0 * math.log10(peak / rms), 6.8)
                        # test the computation of the Rudin-Shapiro sequence length
                        self.assertEqual(gen.GetRudinShapiroSequenceLength(), stop_index - start_index)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.RudinShapiroNoiseGenerator()
        self.assertEqual(gen.SetStartFrequency.GetType(), float)
        self.assertEqual(gen.SetStopFrequency.GetType(), (float, type(None)))
        self.assertEqual(gen.SetSamplingRate.GetType(), float)
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.GetSignal.GetType(), sumpf.Signal)
        self.assertEqual(gen.GetRudinShapiroSequenceLength.GetType(), int)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetStartFrequency, gen.SetStopFrequency, gen.SetSamplingRate, gen.SetLength],
                                         noinputs=[],
                                         output=gen.GetSignal)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetStartFrequency, gen.SetStopFrequency, gen.SetSamplingRate, gen.SetLength],
                                         noinputs=[],
                                         output=gen.GetRudinShapiroSequenceLength)

