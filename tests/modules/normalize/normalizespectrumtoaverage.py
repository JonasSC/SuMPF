# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2018 Jonas Schulte-Coerne
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

import collections
import unittest
import sumpf
import _common as common


class TestNormalizeSpectrumToAverage(unittest.TestCase):
    """
    A TestCase for the NormalizeSpectrumToAverage module.
    """
    def setUp(self):
        self.spectrum = sumpf.Spectrum(channels=((1.0, 2.0, 3.0), (1.0, 1.0, 1.0)), resolution=17.0, labels=("one", "two"))
        self.amp = sumpf.modules.Multiply(value1=self.spectrum)

    def test_get_set(self):
        """
        Tests if the getter and setter methods work as expected.
        """
        nrm = sumpf.modules.NormalizeSpectrumToAverage()
        self.assertEqual(nrm.GetOutput(), sumpf.Spectrum())                                         # ... and the output shall be an empty Spectrum
        nrm.SetSpectrum(self.spectrum)
        self.assertEqual(nrm.GetOutput().GetLabels(), self.spectrum.GetLabels())                    # the output's labels should have been copied from the input
        nrm.SetOrder(1)
        self.amp.SetValue2(6.0 / 9.0)
        self.assertEqual(nrm.GetOutput().GetResolution(), 17.0)                                     # the resolution should have been taken from input Spectrums
        self.assertEqual(nrm.GetOutput().GetChannels(), self.amp.GetResult().GetChannels())         # the normalization should have been done correctly
        nrm.SetIndividual(True)
        self.amp.SetValue2(0.5)
        self.assertEqual(nrm.GetOutput().GetChannels()[0], self.amp.GetResult().GetChannels()[0])   # individual normalization should have been done correctly for the first channel
        self.assertEqual(nrm.GetOutput().GetChannels()[1], self.spectrum.GetChannels()[1])          # individual normalization should have been done correctly for the first channel
        nrm.SetIndividual(False)
        nrm.SetOrder(2)
        self.amp.SetValue2(1.0 / ((17.0 / 6.0) ** 0.5))
        self.assertEqual(nrm.GetOutput().GetChannels(), self.amp.GetResult().GetChannels())         # the normalization of order 2 should have been done correctly

    def test_constructor(self):
        """
        Tests if setting the data via the constructor works.
        """
        nrm = sumpf.modules.NormalizeSpectrumToAverage(spectrum=self.spectrum, order=2, individual=True)
        self.amp.SetValue2(1.0 / ((14.0 / 3.0) ** 0.5))
        self.assertEqual(nrm.GetOutput().GetChannels()[0], self.amp.GetResult().GetChannels()[0])   # individual normalization should have been done correctly for the first channel
        self.assertEqual(nrm.GetOutput().GetChannels()[1], self.spectrum.GetChannels()[1])          # individual normalization should have been done correctly for the first channel

    def test_frequency_range(self):
        """
        Tests if limiting the averaging to a given frequency range works as expected.
        """
        nrm = sumpf.modules.NormalizeSpectrumToAverage(spectrum=self.spectrum, order=2, frequency_range=(16.0, 18.0), individual=False)
        self.amp.SetValue2(1.0 / ((5.0 / 2.0) ** 0.5))
        self.assertEqual(nrm.GetOutput().GetChannels(), self.amp.GetResult().GetChannels())
        nrm.SetFrequencyRange((0.0, 18.0))
        self.amp.SetValue2(1.0 / ((7.0 / 4.0) ** 0.5))
        self.assertEqual(nrm.GetOutput().GetChannels(), self.amp.GetResult().GetChannels())
        nrm.SetFrequencyRange(None)
        self.amp.SetValue2(1.0 / ((17.0 / 6.0) ** 0.5))
        self.assertEqual(nrm.GetOutput().GetChannels(), self.amp.GetResult().GetChannels())

    def test_special_cases(self):
        """
        Tests special cases for the normalization
        """
        nrm = sumpf.modules.NormalizeSpectrumToAverage(spectrum=sumpf.Spectrum(channels=((0.0, 0.0, 0.0),)))
        self.assertEqual(nrm.GetOutput().GetChannels()[0], (0.0, 0.0, 0.0))             # Spectrums with only 0.0 samples should be normalized to [0.0, 0.0, ...]
        nrm = sumpf.modules.NormalizeSpectrumToAverage(spectrum=sumpf.Spectrum(channels=((1.0, 0.5, -1.5),)), order=1)
        self.assertEqual(nrm.GetOutput().GetChannels()[0], (1.0, 0.5, -1.5))            # Spectrums with an average of 0.0 should not be normalized (the factor should be 1.0)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        nrm = sumpf.modules.NormalizeSpectrumToAverage()
        self.assertEqual(nrm.SetSpectrum.GetType(), sumpf.Spectrum)
        self.assertEqual(nrm.SetOrder.GetType(), float)
        self.assertEqual(nrm.SetFrequencyRange.GetType(), collections.Iterable)
        self.assertEqual(nrm.SetIndividual.GetType(), bool)
        self.assertEqual(nrm.GetOutput.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[nrm.SetSpectrum, nrm.SetOrder, nrm.SetFrequencyRange, nrm.SetIndividual],
                                         noinputs=[],
                                         output=nrm.GetOutput)

