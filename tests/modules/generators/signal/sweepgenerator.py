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

import sys
import math
import unittest
import sumpf
import _common as common

if sys.version_info.major > 2:  # bring back the cmp function, when not on Python2
    def cmp(a, b):
        return (a > b) - (a < b)


class TestSweepGenerator(unittest.TestCase):
    def setUp(self):
        self.f0 = 10.0
        self.fT = 25.0
        self.sr = 100.0
        self.gen = sumpf.modules.SweepGenerator(start_frequency=self.f0,
                                                stop_frequency=self.fT,
                                                function=sumpf.modules.SweepGenerator.EXPONENTIAL,
                                                samplingrate=self.sr,
                                                length=100)

    def test_initialization(self):
        signal = self.gen.GetSignal()
        self.assertEqual(len(signal), 100)                  # the length should be as set in the constructor
        self.assertEqual(signal.GetSamplingRate(), self.sr) # the sampling rate should be as set in the constructor
        self.assertEqual(signal.GetLabels(), ("Sweep",))    # the label of the channel should be as expected

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_start_frequency(self):
        """
        Tests if the start frequency is being calculated correctly.
        """
        sr = 48000.0
        self.gen.SetStopFrequency(1000.0)
        self.gen.SetSamplingRate(sr)
        self.gen.SetLength(2 ** 16)
        for f in (sumpf.modules.SweepGenerator.LINEAR, sumpf.modules.SweepGenerator.EXPONENTIAL, sumpf.modules.SweepGenerator.SYNCHRONIZED):
            self.gen.SetSweepFunction(f)
            signal = self.gen.GetSignal()
            s1 = signal.GetChannels()[0][0]
            self.assertEqual(s1, 0.0)                   # the first sample should be 0.0
            s2 = signal.GetChannels()[0][1]
            d = math.sin(2.0 * math.pi * self.f0 / sr)
            self.assertAlmostEqual(s2, d, 5)            # the second sample should be very close to the second sample of a sine wave with the start frequency
            self.assertGreater(s2, d)                   # since the frequency is increasing, the sweep's second sample has to be greater than the one of the pure sine wave

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_stop_frequency(self):
        """
        Tests if the stop frequency of the generated sweep is correct.
        """
        fT = 923.08
        sr = 48000.0
        self.gen.SetStopFrequency(fT)
        self.gen.SetSamplingRate(sr)
        self.gen.SetLength(2 ** 16)
        for f in (sumpf.modules.SweepGenerator.LINEAR, sumpf.modules.SweepGenerator.EXPONENTIAL, sumpf.modules.SweepGenerator.SYNCHRONIZED):
            self.gen.SetSweepFunction(f)
            channel = self.gen.GetSignal().GetChannels()[0]
            i = len(channel) - 1
            while cmp(channel[i] - channel[i - 1], 0.0) == cmp(channel[i - 1] - channel[i - 2], 0.0):
                i -= 1
            first_extreme = i - 1
            i -= 2
            while cmp(channel[i] - channel[i - 1], 0.0) == cmp(channel[i - 1] - channel[i - 2], 0.0):
                i -= 1
            second_extreme = i - 1
            frequency = sr / 2.0 / (first_extreme - second_extreme)
            self.assertAlmostEqual(frequency, fT, 1)

    def test_compare_with_other_formula(self):
        """
        Compares if the generated exponential sweep is identical to one, which
        has been created with the formula, that is often found in the literature.
        """
        # test the exponential sweep
        sweep = self.gen.GetSignal()
        T = sweep.GetDuration()
        L = 1.0 / self.f0 * (T * self.f0 / math.log(self.fT / self.f0))
        a = 2.0 * math.pi * self.f0 * L
        reference = [math.sin(a * (math.exp(float(i) / self.sr / L) - 1.0)) for i in range(len(sweep))]
        for s, r in zip(sweep.GetChannels()[0], reference):
            self.assertAlmostEqual(s, r, 13)
        # test the synchronized sweep
        self.gen.SetSweepFunction(sumpf.modules.SweepGenerator.SYNCHRONIZED)
        sweep = self.gen.GetSignal()
        T = sweep.GetDuration()
        L = 1.0 / self.f0 * round(T * self.f0 / math.log(self.fT / self.f0))
        a = 2.0 * math.pi * self.f0 * L
        reference = [math.sin(a * (math.exp(float(i) / self.sr / L) - 1.0)) for i in range(len(sweep))]
        for s, r in zip(sweep.GetChannels()[0], reference):
            self.assertAlmostEqual(s, r, 13)

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_synchronization(self):
        """
        Tests if the synchronized sweep has the desired property.
        """
        start = 25.0
        stop = 100.0
        samplingrate = 50000.0
        duration = 1.0
        L = sumpf.modules.SweepGenerator.SYNCHRONIZED.precompute_values(f0=start, fT=stop, T=duration)[0]
        gen = sumpf.modules.SweepGenerator(start_frequency=start, stop_frequency=stop, function=sumpf.modules.SweepGenerator.SYNCHRONIZED, samplingrate=samplingrate, length=int(round(duration * samplingrate)))
        sweep1 = gen.GetSignal()
        for factor in (2, 3):
            shift = L * math.log(factor)
            samples = int(round(shift * sweep1.GetSamplingRate()))
            gen.SetStartFrequency(factor * start)
            gen.SetStopFrequency(factor * stop)
            sweep2 = gen.GetSignal()
            spectrum2 = sumpf.modules.FourierTransform(signal=sweep2).GetSpectrum()
            delay = sumpf.modules.DelayFilterGenerator(delay=shift, resolution=spectrum2.GetResolution(), length=len(spectrum2)).GetSpectrum()
            shifted = sumpf.modules.InverseFourierTransform(spectrum=delay * spectrum2).GetSignal()
            for s1, s2 in zip(sweep1.GetChannels()[0][samples + 1900:], shifted.GetChannels()[0][samples + 1900:]):
                self.assertAlmostEqual(s1, s2, 4)

    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_interval(self):
        """
        Tests if the interval feature works as expected.
        """
        # test negative interval values
        self.gen.SetInterval((10, 90))
        tmp = self.gen.GetSignal()
        self.gen.SetInterval((-90, -10))
        swp = self.gen.GetSignal()
        self.assertEqual(swp, tmp)                                      # the interval must be possible with both positive and negative values
        # test group delay
        self.gen.SetInterval((10, 90))
        self.gen.SetSweepFunction(sumpf.modules.SweepGenerator.LINEAR)
        spk = sumpf.modules.FourierTransform(signal=self.gen.GetSignal()).GetSpectrum()
        res = spk.GetResolution()
        self.assertAlmostEqual(spk.GetGroupDelay()[0][int(round(self.f0 / res))], 10.0 / self.sr, 1)
        self.assertAlmostEqual(spk.GetGroupDelay()[0][int(round(self.fT / res))], 90.0 / self.sr, 1)
        self.gen.SetSweepFunction(sumpf.modules.SweepGenerator.EXPONENTIAL)
        spk = sumpf.modules.FourierTransform(signal=self.gen.GetSignal()).GetSpectrum()
        self.assertAlmostEqual(spk.GetGroupDelay()[0][int(round(self.f0 / res))], 10.0 / self.sr, 1)
        self.assertAlmostEqual(spk.GetGroupDelay()[0][int(round(self.fT / res))], 90.0 / self.sr, 1)
        self.gen.SetSweepFunction(sumpf.modules.SweepGenerator.SYNCHRONIZED)
        spk = sumpf.modules.FourierTransform(signal=self.gen.GetSignal()).GetSpectrum()
        self.assertAlmostEqual(spk.GetGroupDelay()[0][int(round(self.f0 / res))], 10.0 / self.sr, 1)
        self.assertAlmostEqual(spk.GetGroupDelay()[0][int(round(self.fT / res))], 90.0 / self.sr, 1)

    def test_errors(self):
        """
        Tests if errors are raised as expected.
        """
        self.gen.SetInterval((-3, -4))
        self.assertRaises(ValueError, self.gen.GetSignal)   # intervals with negative length should raise an error
        self.gen.SetInterval((50, 50))
        self.assertRaises(ValueError, self.gen.GetSignal)   # intervals with zero length should raise an error

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.SweepGenerator()
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetSamplingRate.GetType(), float)
        self.assertEqual(gen.SetStartFrequency.GetType(), float)
        self.assertEqual(gen.SetStopFrequency.GetType(), float)
        self.assertEqual(gen.SetSweepFunction.GetType(), sumpf.internal.SweepFunction)
        self.assertEqual(gen.SetInterval.GetType(), tuple)
        self.assertEqual(gen.GetSignal.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetLength, gen.SetSamplingRate, gen.SetStartFrequency, gen.SetStopFrequency, gen.SetSweepFunction, gen.SetInterval],
                                         noinputs=[],
                                         output=gen.GetSignal)

