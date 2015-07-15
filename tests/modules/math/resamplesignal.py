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
import _common as common


@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestResampleSignal(unittest.TestCase):
    """
    A test case for the ResampleSignal module.
    """
    def test_algorithm_availability(self):
        """
        Tests if the flag for the SINC algorithm is only available, when the
        scikits.samplerate library is available as well.
        """
        if common.lib_available("scikits.samplerate"):
            self.assertIn("SINC", vars(sumpf.modules.ResampleSignal))
        else:
            self.assertNotIn("SINC", vars(sumpf.modules.ResampleSignal))

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(common.lib_available("scikits.samplerate"), "This test requires the library 'scikits.samplerate'")
    def test_resampling_scikits_samplerate(self):
        """
        Tests if the resampling with the algorithm of scikits.samplerate yields
        the correct results.
        """
        samplingrate_original = 32000.0
        samplingrate_high = 35734.0
        samplingrate_low = 30442.0
        self.assertNotEqual((samplingrate_high / samplingrate_original) % 1, 0.0)   # samplingrate_high must not be an integer multiple of samplingrate_original
        self.assertNotEqual((samplingrate_original / samplingrate_low) % 1, 0.0)    # samplingrate_low must not be an integer fraction of samplingrate_original
        # generate original signal and ideally resampled signals
        prp = sumpf.modules.ChannelDataProperties(samplingrate=samplingrate_original)
        dur = sumpf.modules.DurationToLength(duration=1.0)
        sumpf.connect(prp.GetSamplingRate, dur.SetSamplingRate)
        sumpf.connect(dur.GetLength, prp.SetSignalLength)
        gen1 = sumpf.modules.SineWaveGenerator(frequency=samplingrate_low / 2.1)
        sumpf.connect(prp.GetSignalLength, gen1.SetLength)
        sumpf.connect(prp.GetSamplingRate, gen1.SetSamplingRate)
        gen2 = sumpf.modules.TriangleWaveGenerator(raising=0.2, frequency=samplingrate_low / 17.3)
        sumpf.connect(prp.GetSignalLength, gen2.SetLength)
        sumpf.connect(prp.GetSamplingRate, gen2.SetSamplingRate)
        mrg = sumpf.modules.MergeSignals()
        sumpf.connect(gen1.GetSignal, mrg.AddInput)
        sumpf.connect(gen2.GetSignal, mrg.AddInput)
        signal = mrg.GetOutput()
        prp.SetSamplingRate(samplingrate_high)
        ideal_up = mrg.GetOutput()
        prp.SetSamplingRate(samplingrate_low)
        ideal_down = mrg.GetOutput()
        self.assertEqual(signal.GetDuration(), ideal_up.GetDuration())      # the duration of the ideally upsampled Signal has to be the same as the duration of the original Signal
        self.assertEqual(signal.GetDuration(), ideal_down.GetDuration())    # the duration of the ideally downsampled Signal has to be the same as the duration of the original Signal
        # resample the Signal with the ResampleSignal module
        resampled_up = sumpf.modules.ResampleSignal(signal=signal, samplingrate=samplingrate_high, algorithm=sumpf.modules.ResampleSignal.SINC).GetOutput()
        res = sumpf.modules.ResampleSignal()
        res.SetAlgorithm(sumpf.modules.ResampleSignal.SINC)
        res.SetInput(signal)
        res.SetSamplingRate(samplingrate_low)
        resampled_down = res.GetOutput()
        # compare the ideally resampled Signals with those from the ResampleSignal module
        for ideal, resampled in [(ideal_up, resampled_up), (ideal_down, resampled_down)]:
            self.assertEqual(resampled.GetSamplingRate(), ideal.GetSamplingRate())
            self.assertLessEqual(abs(len(ideal) - len(resampled)), 1)       # the length of the resampled Signal must not differ from the length of the ideally resampled Signal by more than one sample
            if len(ideal) > len(resampled):
                ideal = ideal[0:len(resampled)]
            elif len(ideal) < len(resampled):
                resampled = resampled[0:len(ideal)]
            margin = sumpf.modules.DurationToLength(duration=0.005, samplingrate=ideal.GetSamplingRate()).GetLength()
            error = ideal[margin:-margin] - resampled[margin:-margin]
            errorrms = sumpf.modules.RootMeanSquare(signal=error, integration_time=sumpf.modules.RootMeanSquare.FULL).GetOutput()
            signalrms = sumpf.modules.RootMeanSquare(signal=ideal[margin:-margin], integration_time=sumpf.modules.RootMeanSquare.FULL).GetOutput()
            for c in range(len(errorrms.GetChannels())):
                snr = signalrms.GetChannels()[c][0] / errorrms.GetChannels()[c][0]
#               self.assertGreaterEqual(snr, 10 ** (140.0 / 20.0))  # The signal to noise ratio of the sampling rate conversion must be at least 140dB
                self.assertGreaterEqual(snr, 10 ** (23.0 / 20.0))   # The signal to noise ratio of the sampling rate conversion must be at least 23dB
            self.assertEqual(resampled.GetLabels(), ideal.GetLabels())

    def test_resampling_fft(self):
        """
        Tests if resampling by cropping or extending the spectrum behaves as expected.
        """
        # create a test Signal
        sweep = sumpf.modules.SweepGenerator(start_frequency=10.0,
                                             stop_frequency=1000.0,
                                             function=sumpf.modules.SweepGenerator.Exponential,
                                             interval=None,
                                             samplingrate=2500.0,
                                             length=1000).GetSignal()
        triangle = sumpf.modules.TriangleWaveGenerator(raising=0.3,
                                                       frequency=200.0,
                                                       phase=1.4,
                                                       samplingrate=2500.0,
                                                       length=1000).GetSignal()
        merger = sumpf.modules.MergeSignals()
        merger.AddInput(sweep)
        merger.AddInput(triangle)
        input_signal = merger.GetOutput()
        input_spectrum = sumpf.modules.FourierTransform(signal=input_signal).GetSpectrum()
        # create resampled Signals
        upsampled_signal = sumpf.modules.ResampleSignal(signal=input_signal,
                                                        samplingrate=3000.0,
                                                        algorithm=sumpf.modules.ResampleSignal.SPECTRUM).GetOutput()
        upsampled_spectrum = sumpf.modules.FourierTransform(signal=upsampled_signal).GetSpectrum()
        downsampled_signal = sumpf.modules.ResampleSignal(signal=input_signal,
                                                          samplingrate=2000.0,
                                                          algorithm=sumpf.modules.ResampleSignal.SPECTRUM).GetOutput()
        downsampled_spectrum = sumpf.modules.FourierTransform(signal=downsampled_signal).GetSpectrum()
        # test basic Signal properties
        self.assertEqual(len(upsampled_signal), 1200)
        self.assertEqual(len(downsampled_signal), 800)
        self.assertEqual(len(upsampled_signal.GetChannels()), 2)
        self.assertEqual(len(downsampled_signal.GetChannels()), 2)
        self.assertEqual(upsampled_signal.GetSamplingRate(), 3000.0)
        self.assertEqual(downsampled_signal.GetSamplingRate(), 2000.0)
        # test the upsampled Signal
        for c in range(len(upsampled_spectrum.GetChannels())):
            for i in range(len(input_spectrum)):
                self.assertAlmostEqual(upsampled_spectrum.GetChannels()[c][i], upsampled_signal.GetSamplingRate() / input_signal.GetSamplingRate() * input_spectrum.GetChannels()[c][i])
            for i in range(len(input_spectrum), len(upsampled_spectrum)):
                self.assertAlmostEqual(upsampled_spectrum.GetChannels()[c][i], 0.0)
        # test the downsampled Signal
        for c in range(len(downsampled_spectrum.GetChannels())):
            for i in range(len(downsampled_spectrum) - 1):
                self.assertAlmostEqual(downsampled_spectrum.GetChannels()[c][i], downsampled_signal.GetSamplingRate() / input_signal.GetSamplingRate() * input_spectrum.GetChannels()[c][i])
        # compare amplitudes of the original and the resampled Signals
        rms_original = sumpf.modules.RootMeanSquare(signal=input_signal, integration_time=sumpf.modules.RootMeanSquare.FULL).GetOutput()
        rms_upsampled = sumpf.modules.RootMeanSquare(signal=upsampled_signal, integration_time=sumpf.modules.RootMeanSquare.FULL).GetOutput()
        rms_downsampled = sumpf.modules.RootMeanSquare(signal=downsampled_signal, integration_time=sumpf.modules.RootMeanSquare.FULL).GetOutput()
        self.assertAlmostEqual(rms_upsampled.GetChannels()[0][0], rms_original.GetChannels()[0][0], 5)
        self.assertAlmostEqual(rms_upsampled.GetChannels()[1][0], rms_original.GetChannels()[1][0], 5)
        self.assertAlmostEqual(rms_downsampled.GetChannels()[0][0], rms_original.GetChannels()[0][0], 2)
        self.assertAlmostEqual(rms_downsampled.GetChannels()[1][0], rms_original.GetChannels()[1][0], 2)

    def test_errors(self):
        """
        Tests if errors are raised as expected.
        """
        res = sumpf.modules.ResampleSignal()
        res.SetAlgorithm(-1)
        res.GetOutput() # this should not raise an error, since no resampling is done, because the input and output sampling rates are the same
        res.SetSamplingRate(sumpf.config.get("default_samplingrate") + 4.7)
        self.assertRaises(ValueError, res.GetOutput)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        res = sumpf.modules.ResampleSignal()
        self.assertEqual(res.SetInput.GetType(), sumpf.Signal)
        self.assertEqual(res.SetSamplingRate.GetType(), float)
        self.assertEqual(res.SetAlgorithm.GetType(), int)
        self.assertEqual(res.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[res.SetInput, res.SetSamplingRate, res.SetAlgorithm],
                                         noinputs=[],
                                         output=res.GetOutput)

