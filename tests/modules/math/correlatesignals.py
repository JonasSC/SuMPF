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
class TestCorrelateSignals(unittest.TestCase):
    """
    A test case for the CorrelateSignals module.
    """
    def test_crosscorrelation(self):
        """
        Tests if the correlation is calculated correctly.
        """
        expected_results = {((1.0, 0.0), (0.0, 0.5, 0.0)): {sumpf.modules.CorrelateSignals.FULL: (0.0, 0.0, 0.0, 0.5),
                                                            sumpf.modules.CorrelateSignals.SAME: (0.0, 0.0, 0.5),
                                                            sumpf.modules.CorrelateSignals.VALID: (0.5, 0.0)},
                            ((1.0, 0.0, 0.0, 0.0), (0.0, 0.5, 0.0, 0.0)): {sumpf.modules.CorrelateSignals.SPECTRUM: (0.0, 0.0, 0.0, 0.5)},
                            ((0.0, 1.0, 0.0, 0.0), (0.0, 7.0)): {sumpf.modules.CorrelateSignals.FULL: (7.0, 0.0, 0.0, 0.0, 0.0),
                                                                 sumpf.modules.CorrelateSignals.SAME: (7.0, 0.0, 0.0, 0.0),
                                                                 sumpf.modules.CorrelateSignals.VALID: (7.0, 0.0, 0.0)},
                            ((0.0, 1.0, 0.0, 0.0), (0.0, 7.0, 0.0, 0.0)): {sumpf.modules.CorrelateSignals.SPECTRUM: (7.0, 0.0, 0.0, 0.0)},
                            ((2.0, 0.0, 0.0, 3.0), (5.0, 0.0, 0.0)): {sumpf.modules.CorrelateSignals.FULL: (10.0, 0.0, 0.0, 15.0, 0.0, 0.0),
                                                                      sumpf.modules.CorrelateSignals.SAME: (10.0, 0.0, 0.0, 0.0),
                                                                      sumpf.modules.CorrelateSignals.VALID: (10.0, 0.0)},
                            ((2.0, 0.0, 0.0, 3.0), (5.0, 0.0, 0.0, 0.0)): {sumpf.modules.CorrelateSignals.SPECTRUM: (10.0, 0.0, 0.0, 15.0)},
                            ((2.0, 0.0, 0.0, 3.0), (0.0, 0.0, 5.0)): {sumpf.modules.CorrelateSignals.FULL: (0.0, 15.0, 0.0, 0.0, 10.0, 0.0),
                                                                      sumpf.modules.CorrelateSignals.SAME: (0.0, 15.0, 0.0, 0.0),
                                                                      sumpf.modules.CorrelateSignals.VALID: (0.0, 15.0)},
                            ((2.0, 0.0, 0.0, 3.0), (0.0, 0.0, 5.0, 0.0)): {sumpf.modules.CorrelateSignals.SPECTRUM: (0.0, 15.0, 10.0, 0.0)},
                           }
        cor = sumpf.modules.CorrelateSignals()
        self.assertEqual(cor.GetOutput().GetChannels(), ((0.0, 0.0, 0.0,),))                                # the constructor defaults should define a cross correlation of two empty Signals
        for channels in expected_results:
            cor.SetInput1(sumpf.Signal(channels=(channels[0],), samplingrate=55.2))
            cor.SetInput2(sumpf.Signal(channels=(channels[1],), samplingrate=55.2))
            for mode in expected_results[channels]:
                cor.SetCorrelationMode(mode)
                if True:#mode in [sumpf.modules.CorrelateSignals.FULL, sumpf.modules.CorrelateSignals.SPECTRUM, sumpf.modules.CorrelateSignals.SAME]:
                    self.assertEqual(cor.GetOutput().GetChannels(), (expected_results[channels][mode],))    # check correlation result
                    self.assertEqual(cor.GetOutput().GetSamplingRate(), 55.2)                               # check if the sampling rate has been set as expected
                    self.assertEqual(cor.GetOutput().GetLabels(), ("Cross Correlation 1",))                 # check if the label has been set as expected

    def test_autocorrelation(self):
        """
        Test the computation of an autocorrelation.
        """
        impulse = sumpf.Signal(channels=((1.0, 0.0),), samplingrate=44100)
        cor = sumpf.modules.CorrelateSignals(signal1=impulse, signal2=impulse, mode=sumpf.modules.CorrelateSignals.FULL, shift=False)
        self.assertEqual(cor.GetOutput().GetChannels(), ((1.0, 0.0, 0.0),))
        self.assertEqual(cor.GetOutput().GetLabels(), ("Auto Correlation 1",))      # check if the label has been set to "Auto Correlation", when both input signals are the same
        cor.SetShift(True)
        self.assertEqual(cor.GetOutput().GetChannels(), ((0.0, 1.0, 0.0),))         # check if shifting the outputSignal works as expected

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_shifted_sweep(self):
        """
        Test the correlation between a sweep and a shifted version of that sweep
        """
        sweep = sumpf.modules.SweepGenerator(length=2 ** 12).GetSignal()
        shifted_sweep = sumpf.modules.ShiftSignal(signal=sweep, shift=100, circular=False).GetOutput()
        correlation = sumpf.modules.CorrelateSignals(signal1=shifted_sweep, signal2=sweep, mode=sumpf.modules.CorrelateSignals.SPECTRUM)
        # SPECTRUM mode
        channel = correlation.GetOutput().GetChannels()[0]
        self.assertEqual(channel.index(max(channel)), 100)
        # FULL mode
        correlation.SetCorrelationMode(sumpf.modules.CorrelateSignals.FULL)
        channel = correlation.GetOutput().GetChannels()[0]
        self.assertEqual(channel.index(max(channel)), 100)
        # SAME mode
        correlation.SetCorrelationMode(sumpf.modules.CorrelateSignals.SAME)
        channel = correlation.GetOutput().GetChannels()[0]
        self.assertEqual(channel.index(max(channel)), 100)
        # shift == True
        correlation.SetShift(True)
        same_channel = correlation.GetOutput().GetChannels()[0]
        correlation.SetCorrelationMode(sumpf.modules.CorrelateSignals.FULL)
        full_channel = correlation.GetOutput().GetChannels()[0]
        correlation.SetCorrelationMode(sumpf.modules.CorrelateSignals.SPECTRUM)
        spectrum_channel = correlation.GetOutput().GetChannels()[0]
        self.assertEqual(full_channel.index(max(full_channel)), len(full_channel) // 2 + 100)
        self.assertEqual(same_channel.index(max(same_channel)), len(same_channel) // 2 + 100)
        self.assertEqual(spectrum_channel.index(max(spectrum_channel)), len(spectrum_channel) // 2 + 100)

    @unittest.skipUnless(sumpf.config.get("run_incomplete_tests"), "Incomplete tests are skipped")
    def test_convolution(self):
        """
        Tests if the convolution with a reversed Signal is the same as a correlation.
        """
        generator1 = sumpf.modules.ImpulseGenerator(delay=0.06, samplingrate=44100, length=2 ** 14)
        generator2 = sumpf.modules.TriangleWaveGenerator(raising=0.0, frequency=3.0, phase=0.3, samplingrate=44100, length=2 ** 12)
        correlation = sumpf.modules.CorrelateSignals(shift=True)
        sumpf.connect(generator1.GetSignal, correlation.SetInput1)
        sumpf.connect(generator2.GetSignal, correlation.SetInput2)
        reverse1 = sumpf.modules.ReverseSignal()
        sumpf.connect(generator1.GetSignal, reverse1.SetInput)
        convolution = sumpf.modules.ConvolveSignals()
        sumpf.connect(reverse1.GetOutput, convolution.SetInput1)
        sumpf.connect(generator2.GetSignal, convolution.SetInput2)
        reversec = sumpf.modules.ReverseSignal()
        sumpf.connect(convolution.GetOutput, reversec.SetInput)
        for mode in (sumpf.modules.CorrelateSignals.FULL, sumpf.modules.CorrelateSignals.SAME, sumpf.modules.CorrelateSignals.VALID):
            convolution.SetConvolutionMode(mode)
            correlation.SetCorrelationMode(mode)
            self.assertEqual(reversec.GetOutput().GetChannels()[0], correlation.GetOutput().GetChannels()[0])

    def test_errors(self):
        """
        Tests if the correlation module raises errors correctly.
        """
        signal1 = sumpf.Signal(channels=((1.0, 0.0),), samplingrate=48000)
        signal2 = sumpf.Signal(channels=((0.0, 0.5, 0.0),), samplingrate=48000)
        cor = sumpf.modules.CorrelateSignals(signal1=signal2, mode=sumpf.modules.CorrelateSignals.SAME)
        self.assertRaises(ValueError, cor.SetCorrelationMode, "Invalid")                        # shall fail if mode is not supported by numpy
        cor.SetInput2(sumpf.Signal(channels=((0.0, 0.0),), samplingrate=44100))
        self.assertRaises(ValueError, cor.GetOutput)                                            # shall fail because input Signals do not have the same sampling rate
        cor.SetInput2(sumpf.Signal(channels=((1.0, 0.0), (5.0, 5.0)), samplingrate=48000))
        self.assertRaises(ValueError, cor.GetOutput)                                            # shall fail because input Signals do not have the same number of channels
        cor.SetInput2(signal=signal1)
        cor.SetCorrelationMode(sumpf.modules.ConvolveSignals.SPECTRUM)
        self.assertRaises(ValueError, cor.GetOutput)                                            # shall fail because in SPECTRUM mode, the input Signals must have the same length, which these signals haven't

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        cnv = sumpf.modules.CorrelateSignals()
        self.assertEqual(cnv.SetInput1.GetType(), sumpf.Signal)
        self.assertEqual(cnv.SetInput2.GetType(), sumpf.Signal)
        self.assertEqual(cnv.SetCorrelationMode.GetType(), type(sumpf.modules.CorrelateSignals.VALID))
        self.assertEqual(cnv.SetShift.GetType(), bool)
        self.assertEqual(cnv.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[cnv.SetInput1, cnv.SetInput2, cnv.SetCorrelationMode, cnv.SetShift],
                                         noinputs=[],
                                         output=cnv.GetOutput)

