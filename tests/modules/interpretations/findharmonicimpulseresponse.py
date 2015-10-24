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
class TestFindHarmonicImpulseResponse(unittest.TestCase):
    """
    A TestCase for the FindHarmonicImpulseResponse module.
    """
    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_impulse_response_length(self):
        """
        Tests if the cut out impulse responses are resampled correctly.
        """
        # the properties of the sweep that would have been used to determine this impulse response
        f0 = 2.8485
        fT = 17.4
        T = 1.7
        sr = 67.34
        k = (fT / f0) ** (1.0 / T)
        # the involved classes
        impulse = sumpf.modules.ImpulseGenerator(length=sumpf.modules.DurationToLength(duration=T, samplingrate=sr).GetLength(), samplingrate=sr).GetSignal()
        findharmonics = sumpf.modules.FindHarmonicImpulseResponse()
        findharmonics.SetImpulseResponse(impulse)
        findharmonics.SetHarmonicOrder(2)
        findharmonics.SetSweepStartFrequency(f0)
        findharmonics.SetSweepStopFrequency(fT)
        findharmonics.SetSweepDuration(T)
        # check length and sampling rate for a harmonic order of 2
        l = sumpf.modules.DurationToLength(duration=math.log(2.0, k), samplingrate=sr).GetLength()
        if l % 2 != 0:
            l += 1
        harmonic = findharmonics.GetHarmonicImpulseResponse()
        self.assertEqual(len(harmonic), l)
        self.assertEqual(harmonic.GetSamplingRate(), sr / 2.0)
        # check length and sampling rate for higher harmonic orders
        for o in range(3, 6):
            l = sumpf.modules.DurationToLength(duration=math.log(o, k), samplingrate=sr).GetLength() - sumpf.modules.DurationToLength(duration=math.log(o - 1.0, k), samplingrate=sr).GetLength()
            if l % 2 != 0:
                l += 1
            findharmonics.SetHarmonicOrder(o)
            harmonic = findharmonics.GetHarmonicImpulseResponse()
            self.assertEqual(len(harmonic), l)
            self.assertEqual(harmonic.GetSamplingRate(), sr / o)

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_harmonic_frequency_response(self):
        """
        Tests if the frequency response of the cut out harmonics look realistic.
        """
        # the sweep properties
        f0 = 1.0
        fT = 20000.0
        T = 2.0
        # a function that defines a nonlinear system
        fr = 896.5
        def system(signal):
            spectrum = sumpf.modules.FourierTransform(signal).GetSpectrum()
            bandpass = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BANDPASS(q_factor=5), frequency=fr, resolution=spectrum.GetResolution(), length=len(spectrum)).GetSpectrum()
            filtered = sumpf.modules.InverseFourierTransform(bandpass * spectrum).GetSignal()
            s = sumpf.modules.ConvolveSignals(signal1=filtered, signal2=sumpf.Signal(channels=((0.1,) * 8,), samplingrate=44100.0), mode=sumpf.modules.ConvolveSignals.SAME).GetOutput()
            nonlinear = 8.0 * s - 4.0 * s * s + 6.0 * s * s * s - 8.0 * s * s * s * s
            return nonlinear
        # "measure" the system's impulse response
        sweep = sumpf.modules.SweepGenerator(start_frequency=f0,
                                             stop_frequency=fT,
                                             function=sumpf.modules.SweepGenerator.Exponential,
                                             samplingrate=44100.0,
                                             length=T * 44100.0).GetSignal()
        excitation_spectrum = sumpf.modules.FourierTransform(sweep).GetSpectrum()
        response_spectrum = sumpf.modules.FourierTransform(system(sweep)).GetSpectrum()
        inverse = sumpf.modules.RegularizedSpectrumInversion(excitation_spectrum).GetOutput()
        transfer_function = response_spectrum * inverse
        impulse_response = sumpf.modules.InverseFourierTransform(transfer_function).GetSignal()
        # check if the magnitude of the first harmonic transfer functions has its maximum at the right frequency
        reference_maximum = transfer_function.GetMagnitude()[0].index(max(transfer_function.GetMagnitude()[0])) * transfer_function.GetResolution()
        for o in range(2, 5):
            hir = sumpf.modules.FindHarmonicImpulseResponse(impulse_response=impulse_response, harmonic_order=o, sweep_start_frequency=f0, sweep_stop_frequency=fT, sweep_duration=T).GetHarmonicImpulseResponse()
            htf = sumpf.modules.FourierTransform(signal=hir).GetSpectrum()
            maximum = htf.GetMagnitude()[0].index(max(htf.GetMagnitude()[0])) * htf.GetResolution()
            self.assertLess(abs(reference_maximum - maximum), htf.GetResolution())

    def test_none_labels(self):
        impulse_response = sumpf.Signal(channels=((1.0, 0.0, 0.0, 0.0, 1.0),), samplingrate=1.0, labels=(None,))
        hir = sumpf.modules.FindHarmonicImpulseResponse(impulse_response=impulse_response, harmonic_order=2, sweep_start_frequency=100.0, sweep_stop_frequency=200.0).GetHarmonicImpulseResponse()
        self.assertEqual(hir.GetLabels(), ("Impulse Response (2nd harmonic)",))

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_errors(self):
        """
        tests if all errors are raised as expected
        """
        self.assertRaises(ValueError, sumpf.modules.FindHarmonicImpulseResponse, harmonic_order=1)
        fhi = sumpf.modules.FindHarmonicImpulseResponse()
        self.assertRaises(ValueError, fhi.SetHarmonicOrder, 1)

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        fhi = sumpf.modules.FindHarmonicImpulseResponse()
        self.assertEqual(fhi.GetHarmonicImpulseResponse.GetType(), sumpf.Signal)
        self.assertEqual(fhi.SetImpulseResponse.GetType(), sumpf.Signal)
        self.assertEqual(fhi.SetHarmonicOrder.GetType(), int)
        self.assertEqual(fhi.SetSweepStartFrequency.GetType(), float)
        self.assertEqual(fhi.SetSweepStopFrequency.GetType(), float)
        self.assertEqual(fhi.SetSweepDuration.GetType(), float)
        common.test_connection_observers(testcase=self,
                                         inputs=[fhi.SetImpulseResponse, fhi.SetHarmonicOrder, fhi.SetSweepStartFrequency, fhi.SetSweepStopFrequency, fhi.SetSweepDuration],
                                         noinputs=[],
                                         output=fhi.GetHarmonicImpulseResponse)

