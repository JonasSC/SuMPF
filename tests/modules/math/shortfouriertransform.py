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

import math
import unittest
import sumpf
import _common as common

@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestShortFourierTransform(unittest.TestCase):
    """
    A test case for the ShortFourierTransform.
    """
    def test_default_values(self):
        """
        Tests the default signal and default window length.
        """
        fft = sumpf.modules.ShortFourierTransform()
        self.assertEqual(fft.GetSpectrum().GetChannels(), ((0.0j,) * 4097,))

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_shorten_impulse_response(self):
        """
        Tests if downsampling an impulse works as expected.
        """
        impulse = sumpf.modules.ImpulseGenerator().GetSignal()
        spectrum = sumpf.modules.ShortFourierTransform(signal=impulse).GetSpectrum()
        short_impulse = sumpf.modules.InverseFourierTransform(spectrum=spectrum).GetSignal()
        reference = impulse[0:len(short_impulse)]
        common.compare_signals_almost_equal(testcase=self, signal1=short_impulse, signal2=reference)

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_sine_waves(self):
        """
        Tests the fourier transformation of sine waves.
        """
        length = 12448
        samplingrate = 10000.0
        f1 = 1548.0
        f2 = 133.7
        sine1 = sumpf.modules.SineWaveGenerator(frequency=f1, phase=0.0, samplingrate=samplingrate, length=length).GetSignal()
        sine2 = sumpf.modules.SineWaveGenerator(frequency=f2, phase=math.pi, samplingrate=samplingrate, length=length).GetSignal()
        merger = sumpf.modules.MergeSignals()
        merger.AddInput(sine1)
        merger.AddInput(sine2)
        signal = merger.GetOutput()
        window = sumpf.modules.WindowGenerator(raise_interval=(0, 2048), fall_interval=(2048, 4096), function=sumpf.modules.WindowGenerator.Hanning(), samplingrate=samplingrate, length=4096).GetSignal()
        fft = sumpf.modules.ShortFourierTransform()
        fft.SetSignal(signal)
        fft.SetWindow(window)
        fft.SetOverlap(2048)
        spectrum = fft.GetSpectrum()
        index1 = int(round(f1 / spectrum.GetResolution()))
        index2 = int(round(f2 / spectrum.GetResolution()))
        # test phase
        phase1 = spectrum.GetPhase()[0]
        self.assertEqual(phase1[0], 0.0)
        self.assertAlmostEqual(phase1[-1], 0.0)
#       self.assertAlmostEqual(phase1[index1], 0.0, 1)
        phase2 = spectrum.GetPhase()[1]
        self.assertEqual(phase2[0], math.pi)
        self.assertAlmostEqual(phase2[-1], 0.0)
#       self.assertAlmostEqual(abs(phase2[index2]), math.pi, 1)
        # test magnitude
        magnitude1 = spectrum.GetMagnitude()[0]
        maximum1 = max(magnitude1)
        self.assertGreater(maximum1 / magnitude1[0], 10.0 ** (40.0 / 20.0))
        self.assertGreater(maximum1 / magnitude1[-1], 10.0 ** (40.0 / 20.0))
        self.assertEqual(magnitude1.index(max(magnitude1)), index1)
        magnitude2 = spectrum.GetMagnitude()[-1]
        maximum2 = max(magnitude2)
        self.assertGreater(maximum2 / magnitude2[0], 10.0 ** (35.0 / 20.0))
        self.assertGreater(maximum2 / magnitude2[-1], 10.0 ** (40.0 / 20.0))
        self.assertEqual(magnitude2.index(max(magnitude2)), index2)

    def test_errors(self):
        """
        Tests if all errors are raised as expected.
        """
        fft = sumpf.modules.ShortFourierTransform()
        # test wrong overlaps
        self.assertRaises(ValueError, fft.SetOverlap, 1.1)
        self.assertRaises(ValueError, fft.SetOverlap, -0.1)
        self.assertRaises(ValueError, sumpf.modules.ShortFourierTransform, overlap=1.1)
        fft.SetOverlap(9000)
        self.assertRaises(ValueError, fft.GetSpectrum)
        fft.SetOverlap(0.5)
        # test wrong sampling rates
        signal = sumpf.modules.SilenceGenerator(length=18, samplingrate=33).GetSignal()
        window = sumpf.modules.SilenceGenerator(length=20, samplingrate=34).GetSignal()
        fft.SetSignal(signal)
        fft.GetSpectrum()
        fft.SetWindow(window)
        self.assertRaises(ValueError, fft.GetSpectrum)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        fft = sumpf.modules.ShortFourierTransform()
        self.assertEqual(fft.SetSignal.GetType(), sumpf.Signal)
        self.assertEqual(fft.SetWindow.GetType(), sumpf.Signal)
        self.assertEqual(fft.SetOverlap.GetType(), (int, float))
        self.assertEqual(fft.GetSpectrum.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[fft.SetSignal, fft.SetWindow, fft.SetOverlap],
                                         noinputs=[],
                                         output=fft.GetSpectrum)

