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


@unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
class TestSignalEnvelope(unittest.TestCase):
    """
    A TestCase for the SignalEnvelope module.
    """
    def test_defaults(self):
        """
        Tests the default values for SignalEnvelope's constructor.
        """
        env = sumpf.modules.SignalEnvelope()
        self.assertEqual(env.GetEnvelope(), sumpf.Signal())

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_demodulation(self):
        """
        Modulates a sine wave with some Signals and tests if the SignalEnvelope
        module can demodulate them.
        """
        length = 43210
        samplingrate = 43210.0
        margin = 100
        # setup modulation Signals
        modulations = sumpf.modules.MergeSignals()
        modulations.AddInput(1.2 * sumpf.modules.TriangleWaveGenerator(raising=0.3, frequency=1.5, phase=0.3, samplingrate=samplingrate, length=length).GetSignal())
        modulations.AddInput(0.7 * sumpf.modules.SineWaveGenerator(frequency=1.0, phase=-0.1, samplingrate=samplingrate, length=length).GetSignal())
        modulations.AddInput(sumpf.modules.ConstantSignalGenerator(value=0.4, samplingrate=samplingrate, length=length).GetSignal())
        modulations.AddInput(sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.RedNoise(), seed=3886, samplingrate=samplingrate, length=length).GetSignal())
        rectified = sumpf.modules.RectifySignal(signal=modulations.GetOutput()).GetOutput()
        # setup a carrier Signal
        carrier1 = sumpf.modules.SineWaveGenerator(frequency=1234.0, samplingrate=samplingrate, length=length).GetSignal()
        carrier2 = sumpf.modules.TriangleWaveGenerator(raising=0.6, frequency=1243.0, samplingrate=samplingrate, length=length).GetSignal()
        carrier_merger = sumpf.modules.MergeSignals()
        carrier_merger.AddInput(carrier1)
        carrier_merger.AddInput(carrier2)
        multichannel_carrier = sumpf.modules.CopySignalChannels(input=carrier_merger.GetOutput(), channelcount=modulations.GetNumberOfOutputChannels()).GetOutput()
        # setup offset Signals
        zero_offset = sumpf.modules.SilenceGenerator(samplingrate=samplingrate, length=length).GetSignal()
        constant_offset = sumpf.Signal(channels=((0.1,) * length, (-0.2,) * length, (-1.8,) * length), samplingrate=samplingrate)
        low_frequency_offset_merger = sumpf.modules.MergeSignals()
        low_frequency_offset_merger.AddInput(0.2 * sumpf.modules.SineWaveGenerator(frequency=0.21, phase=-1.5, samplingrate=samplingrate, length=length).GetSignal())
        low_frequency_offset_merger.AddInput(-0.4 * sumpf.modules.TriangleWaveGenerator(raising=0.5, frequency=0.12, phase=0.6, samplingrate=samplingrate, length=length).GetSignal())
        low_frequency_offset_merger.AddInput(-0.5 * sumpf.modules.TriangleWaveGenerator(raising=1.0, frequency=0.2 * samplingrate / length, phase=0.0, samplingrate=samplingrate, length=length).GetSignal())
        offsets = [zero_offset, constant_offset, low_frequency_offset_merger.GetOutput()]
        for o in offsets:
            # create a modulated Signal
            offset = sumpf.modules.CopySignalChannels(input=o, channelcount=modulations.GetNumberOfOutputChannels()).GetOutput()
            modulated = multichannel_carrier * rectified + offset
            # setup ideal reference Signals
            ideal_upper = rectified + offset
            ideal_lower = -1.0 * rectified + offset
            ideal_upper_envelope = sumpf.modules.CopyLabelsToSignal(data_input=ideal_upper, label_input=modulated).GetOutput()
            ideal_lower_envelope = sumpf.modules.CopyLabelsToSignal(data_input=ideal_lower, label_input=modulated).GetOutput()
            # calculate the envelopes
            upper_envelope = sumpf.modules.SignalEnvelope(signal=modulated, frequency=42.0, order=32).GetEnvelope() # the default mode is assumed to be UPPER
            lowerenvelope = sumpf.modules.SignalEnvelope(signal=modulated, frequency=42.0)  # the default order is assumed to be 32
            lowerenvelope.SetMode(sumpf.modules.SignalEnvelope.LOWER)
            # compare the calculated envelopes with the reference Signals
            common.compare_signals_almost_equal(testcase=self, signal1=upper_envelope[margin:-margin], signal2=ideal_upper_envelope[margin:-margin], places=2)
            common.compare_signals_almost_equal(testcase=self, signal1=lowerenvelope.GetEnvelope()[margin:-margin], signal2=ideal_lower_envelope[margin:-margin], places=2)

    def test_odd_signallength(self):
        """
        Tests if an odd length of the input Signal does not lead to missing samples
        after when the calculation of the envelope transforms the Signal to the
        frequency domain and back.
        """
        signal = sumpf.Signal(channels=((1, -1, 1, 2, -4),))
        env = sumpf.modules.SignalEnvelope()
        env.SetSignal(signal)
        envelope = env.GetEnvelope()
        self.assertEqual(len(envelope), len(signal))

    def test_sampling_rate_error(self):
        """
        Tests if the calculation of the envelope does not crash, when the transformation
        to the frequency domain and back leads to a wrongly calculated sampling
        rate because of limited floating point precision.
        """
        signal = sumpf.Signal(channels=((-3.8,) * 158,), samplingrate=48000)
        fftd = sumpf.modules.FourierTransform(signal=signal).GetSpectrum()
        ifftd = sumpf.modules.InverseFourierTransform(spectrum=fftd).GetSignal()
        self.assertNotEqual(signal.GetSamplingRate(), ifftd.GetSamplingRate())  # the Signal's length of 23002 should have lead to a wrongly calculated sampling rate
        env = sumpf.modules.SignalEnvelope()
        env.SetSignal(signal)
        env.GetEnvelope()

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        env = sumpf.modules.SignalEnvelope()
        self.assertEqual(env.SetSignal.GetType(), sumpf.Signal)
        self.assertEqual(env.SetMode.GetType(), float)
        self.assertEqual(env.SetFrequency.GetType(), float)
        self.assertEqual(env.SetOrder.GetType(), int)
        common.test_connection_observers(testcase=self,
                                         inputs=[env.SetSignal, env.SetMode, env.SetFrequency, env.SetOrder],
                                         noinputs=[],
                                         output=env.GetEnvelope)

