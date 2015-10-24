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
import math
import sumpf
import _common as common


class TestFilterGenerator(unittest.TestCase):
    """
    A TestCase for the FilterGenerator module.
    """
    def test_lowpass_highpass(self):
        """
        Tests the IIR filters, namely Butterworth-, Bessel- and Chebychev-filters
        for both the lowpass and the highpass application.
        """
        gen = sumpf.modules.FilterGenerator(transform=False, resolution=200.0, length=100)
        # lowpasses
        filters = []
        filters.append((100.0, sumpf.modules.FilterGenerator.BUTTERWORTH(order=4)))
        filters.append((92.0, sumpf.modules.FilterGenerator.BESSEL(order=4)))
        filters.append((100.0, sumpf.modules.FilterGenerator.CHEBYCHEV1(order=4, ripple=3.0)))
        for frequency, function in filters:
            gen.SetFilterFunction(function)
            gen.SetFrequency(frequency)
            channel = gen.GetSpectrum().GetMagnitude()[0]
            self.assertAlmostEqual(channel[0], 1.0)                     # a lowpass should have a gain of 1 at low frequencies
            self.assertAlmostEqual(channel[-1], 0.0)                    # a lowpass should have a gain of 0 at high frequencies
        # highpasses
        gen.SetTransform(True)
        gen.SetFrequency(100.0)
        for frequency, function in filters:
            gen.SetFilterFunction(function)
            channel = gen.GetSpectrum().GetMagnitude()[0]
            self.assertAlmostEqual(channel[0], 0.0)                     # a highpass should have a gain of 0 at low frequencies
            self.assertAlmostEqual(channel[-1], 1.0, 3)                 # a highpass should have a gain of 1 at high frequencies

    def test_bandpass_bandstop(self):
        """
        Tests the bandpass and bandstop filters.
        """
        gen = sumpf.modules.FilterGenerator(resolution=10.0, length=100)
        gen.SetFrequency(500.0)
        # bandpass
        gen.SetFilterFunction(sumpf.modules.FilterGenerator.BANDPASS(q_factor=5.0))
        channel = gen.GetSpectrum().GetMagnitude()[0]
        self.assertAlmostEqual(channel[50], 1.0)                            # gain at resonant frequency should be 1
        self.assertAlmostEqual(channel[45], 1.0 / math.sqrt(2.0), 1)        # gain at lower cutoff frequency should be sqrt(2)
        self.assertAlmostEqual(channel[55], 1.0 / math.sqrt(2.0), 1)        # gain at upper cutoff frequency should be sqrt(2)
        # bandstop
        gen.SetFilterFunction(sumpf.modules.FilterGenerator.BANDSTOP(q_factor=5.0))
        channel = gen.GetSpectrum().GetMagnitude()[0]
        self.assertAlmostEqual(channel[50], 0.0)                            # gain at resonant frequency should be almost 0
        self.assertAlmostEqual(channel[45], 1.0 / math.sqrt(2.0), 1)        # gain at lower cutoff frequency should be sqrt(2)
        self.assertAlmostEqual(channel[55], 1.0 / math.sqrt(2.0), 1)        # gain at upper cutoff frequency should be sqrt(2)

    def test_transferfunction(self):
        """
        Tests the generation of a filter by its laplace transfer function.
        """
        for f in [sumpf.modules.FilterGenerator.BUTTERWORTH, sumpf.modules.FilterGenerator.BESSEL, sumpf.modules.FilterGenerator.CHEBYCHEV1, sumpf.modules.FilterGenerator.BANDPASS, sumpf.modules.FilterGenerator.BANDSTOP]:
            filterfunction = f()
            numerator, denominator = filterfunction.GetCoefficients()[0]
            transferfunction = sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator, denominator)
            for cutoff in (1.0, 1000.0):
                resolution = cutoff / 10.0
                length = 20
                for highpass in (False, True):
                    f_filter = sumpf.modules.FilterGenerator(filterfunction=filterfunction, frequency=cutoff, transform=highpass, resolution=resolution, length=length).GetSpectrum()
                    tf_filter = sumpf.modules.FilterGenerator(filterfunction=transferfunction, frequency=cutoff, transform=highpass, resolution=resolution, length=length).GetSpectrum()
                    self.assertEqual(f_filter.GetChannels(), tf_filter.GetChannels())

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.FilterGenerator()
        self.assertEqual(gen.SetFrequency.GetType(), float)
        self.assertEqual(gen.SetTransform.GetType(), bool)
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetResolution.GetType(), float)
        self.assertEqual(gen.SetMaximumFrequency.GetType(), float)
        self.assertEqual(gen.GetSpectrum.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetFilterFunction, gen.SetFrequency, gen.SetTransform, gen.SetLength, gen.SetResolution, gen.SetMaximumFrequency],
                                         noinputs=[],
                                         output=gen.GetSpectrum)

