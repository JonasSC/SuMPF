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
import os
import unittest
import sumpf
import _common as common

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy


class TestSpectrum(unittest.TestCase):
    def setUp(self):
        samples1 = []
        samples2 = []
        for i in range(1, 11):
            samples1.append(i + 1.0j * i)
            samples2.append(2 * i)
        self.samples1 = tuple(samples1)
        self.samples2 = tuple(samples2)
        self.channels = (self.samples1, self.samples2)
        self.spectrum = sumpf.Spectrum(channels=self.channels, resolution=4800.0, labels=("1", "2"))

    def test_spectrum_initialization(self):
        """
        Tests if all data is stored in the Spectrum correctly
        """
        self.assertEqual(self.spectrum.GetChannels(), self.channels)    # test if channels are set correctly
        self.assertEqual(self.spectrum.GetResolution(), 4800.0)         # test if resolution is set correctly
        self.assertEqual(len(self.spectrum), len(self.samples1))        # test if length is computed correctly
        magnitude = (tuple([abs(i) for i in self.samples1]), self.samples2)
        if os.name == "nt":
            spk_magnitude = self.spectrum.GetMagnitude()
            for c in range(len(spk_magnitude)):
                for s in range(len(spk_magnitude[c])):
                    self.assertAlmostEqual(spk_magnitude[c][s], magnitude[c][s])    # perform a windows specific test, because the calculations do not seem not run as precise as expected here
        else:
            self.assertEqual(self.spectrum.GetMagnitude(), magnitude)   # test if magnitude is computed correctly
        phase = ((math.pi / 4.0,) * len(self.spectrum), (0.0,) * len(self.spectrum))
        self.assertEqual(self.spectrum.GetPhase(), phase)               # test if phase is computed correctly
        self.assertEqual(self.spectrum.GetLabels(), ("1", "2"))         # test if labels are set correctly
        spk = sumpf.Spectrum(channels=self.channels, resolution=4800.0, labels=("1",))
        self.assertEqual(spk.GetLabels(), ("1", None))                  # test if labels are set correctly, if the given tuple of labels is shorter than the tuple of channels
        spk = sumpf.Spectrum(channels=self.channels, resolution=4800.0, labels=("1", "2", "3"))
        self.assertEqual(spk.GetLabels(), ("1", "2"))                   # test if labels are set correctly, if the given tuple of labels is longer than the tuple of channels
        spk = sumpf.Spectrum(channels=self.channels, resolution=4800.0, labels=(None, "2"))
        self.assertEqual(spk.GetLabels(), (None, "2"))                  # test if labels are set correctly, if a label is None
        spk = sumpf.Spectrum()
        self.assertTrue(spk.IsEmpty())                                  # creating a Spectrum without passing constructor arguments should create an empty Spectrum
        self.assertEqual(spk.GetChannels(), ((0.0, 0.0),))              # an empty Spectrum should have one channel with two 0.0 samples

    def test_invalid_spectrum_initialization(self):
        """
        Tests if all errors are raised as expected
        """
        def createSpectrumWithoutChannels():
            sumpf.Spectrum(channels=())
        def createSpectrumWithEmptyChannels():
            sumpf.Spectrum(channels=((), ()))
        def createSpectrumWithTooShortChannels():
            sumpf.Spectrum(channels=((1,), (2,)))
        def createSpectrumWithUnEqualChannels():
            sumpf.Spectrum(channels=(self.samples1, self.samples2[1:-1]))
        def createSpectrumWithWrongLabels():
            sumpf.Spectrum(channels=self.channels, labels=("1", 2))
        self.assertRaises(ValueError, createSpectrumWithoutChannels)        # creating a Spectrum without channels should fail
        self.assertRaises(ValueError, createSpectrumWithEmptyChannels)      # creating a Spectrum with empty channels should fail
        self.assertRaises(ValueError, createSpectrumWithTooShortChannels)   # creating a Spectrum with channels shorter than 2 samples should fail
        self.assertRaises(ValueError, createSpectrumWithUnEqualChannels)    # creating a Spectrum with channels of different length should fail
        self.assertRaises(TypeError, createSpectrumWithWrongLabels)         # creating a Spectrum with non-string labels should fail

    def test_comparison(self):
        """
        Tests if the comparison methods work as expected.
        """
        cmpspectrum_equal = sumpf.Spectrum(channels=[self.samples1, self.samples2], resolution=4800, labels=["1", "2"])
        cmpspectrum_channels1 = sumpf.Spectrum(channels=(self.samples2, self.samples1), resolution=4800.0, labels=("1", "2"))
        cmpspectrum_channels2 = sumpf.Spectrum(channels=(self.samples1, self.samples1), resolution=4800.0, labels=("1", "2"))
        cmpspectrum_channels3 = sumpf.Spectrum(channels=(self.samples1,), resolution=4800.0, labels=("1", "2"))
        cmpspectrum_channels4 = sumpf.Spectrum(channels=(self.samples2, self.samples2), resolution=4800.0, labels=("1", "2"))
        cmpspectrum_resolution = sumpf.Spectrum(channels=(self.samples1, self.samples2), resolution=4801.0, labels=("1", "2"))
        cmpspectrum_labels = sumpf.Spectrum(channels=(self.samples1, self.samples2), resolution=4800.0, labels=("1", "3"))
        self.assertEqual(self.spectrum, self.spectrum)                  # same Spectrums should be recognized as equal
        self.assertEqual(self.spectrum, cmpspectrum_equal)              # equal Spectrums should be recognized as equal
        self.assertNotEqual(self.spectrum, cmpspectrum_channels1)       # Spectrums with different channels should not be recognized as equal
        self.assertNotEqual(self.spectrum, cmpspectrum_channels2)       #   "
        self.assertNotEqual(self.spectrum, cmpspectrum_channels3)       #   "
        self.assertNotEqual(self.spectrum, cmpspectrum_channels4)       #   "
        self.assertNotEqual(self.spectrum, cmpspectrum_resolution)      # Spectrums with different resolution should not be recognized as equal
        self.assertNotEqual(self.spectrum, cmpspectrum_labels)          # Spectrums with different labels should not be recognized as equal

    def test_types(self):
        """
        Tests if the data is stored in the correct types
        """
        spectrum = sumpf.Spectrum(channels=[[1, 2]], resolution=42.0, labels=["As list"])
        self.assertIsInstance(spectrum.GetChannels(), tuple)        # the channels should be stored in a tuple
        self.assertIsInstance(spectrum.GetChannels()[0], tuple)     # the channels should be tuples
        self.assertIsInstance(spectrum.GetResolution(), float)      # the resolution should be a float
        self.assertIsInstance(spectrum.GetLabels(), tuple)          # the labels should be stored in a tuple
        self.assertIsInstance(spectrum.GetLabels()[0], str)         # the labels can be either ascii or unicode strings

    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_group_delay(self):
        """
        Tests if the method for calculating the group delay works as expected
        """
        gen = sumpf.modules.ImpulseGenerator(delay=0.03, samplingrate=400, length=400)
        fft = sumpf.modules.FourierTransform()
        sumpf.connect(gen.GetSignal, fft.SetSignal)
        spk = fft.GetSpectrum()
        self.assertAlmostEqual(min(spk.GetGroupDelay()[0]), max(spk.GetGroupDelay()[0]))    # the group delay should be constant
        self.assertAlmostEqual(min(spk.GetGroupDelay()[0]), 0.03)                           # the group delay should be the same as the delay for the impulse

    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_continuous_phase(self):
        """
        Tests the calculation of the continuous phase of a spectrum.
        """
        swp = sumpf.modules.SweepGenerator(length=1024).GetSignal()
        spk = sumpf.modules.FourierTransform(signal=swp).GetSpectrum()
        continuous_phase = spk.GetContinuousPhase()[0]
        group_delay = spk.GetGroupDelay()[0]
        self.assertEqual(continuous_phase[0], 0.0)
        integral = 0.0
        for i in range(1, len(continuous_phase) - 1):
            self.assertLess(continuous_phase[i], continuous_phase[i - 1])
            integral -= 2.0 * math.pi * group_delay[i]
            self.assertEqual(continuous_phase[i], integral)

    def test_overloaded_operators(self):
        """
        Tests the overloaded operators of the Signal class.
        The comparison operators are tested in test_comparison.
        The length getter is tested in test_signal_initialization
        """
        # __repr__
        newlocals = {}
        exec("newspectrum = sumpf." + repr(self.spectrum), globals(), newlocals)
        self.assertEqual(newlocals["newspectrum"], self.spectrum)
        # __str__
        self.assertEqual(str(self.spectrum), "<_sumpf._data.spectrum.Spectrum object (length: 10, resolution: 4800.00, channel count: 2) at 0x%x>" % id(self.spectrum))
        # algebra
        spectrum1 = sumpf.Spectrum(channels=(self.samples2, self.samples1), resolution=4800.0, labels=("1", "2"))
        spectrum2 = sumpf.Spectrum(channels=(self.samples1,), resolution=4800.0, labels=("3", "4"))
        spectrum3 = sumpf.Spectrum(channels=((1.0 + 4.2j,) * 12, (2.0,) * 12), resolution=4800.0, labels=("5", "6"))
        spectrum4 = sumpf.Spectrum(channels=((1.0,) * 10, (2.0 + 2.3j,) * 10), resolution=4410.0, labels=("7", "8"))
        spectrum5 = sumpf.Spectrum(channels=((0.0,) * 10, (0.0,) * 10), resolution=4800.0, labels=("9", "0"))
        # __add__
        self.assertEqual(self.spectrum + spectrum1,
                         sumpf.Spectrum(channels=(numpy.add(self.samples1, self.samples2),
                                                  numpy.add(self.samples2, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Sum 1", "Sum 2")))
        self.assertRaises(ValueError, self.spectrum.__add__, spectrum3) # adding a Spectrum with a different length should fail
        self.assertRaises(ValueError, self.spectrum.__add__, spectrum4) # adding a Spectrum with a different sampling rate should fail
        self.assertRaises(ValueError, self.spectrum.__add__, spectrum2) # adding a Spectrum with less channels should fail
        self.assertRaises(ValueError, spectrum2.__add__, self.spectrum) # adding a Spectrum with more channels should fail
        # __sub__
        self.assertEqual(self.spectrum - spectrum1,
                         sumpf.Spectrum(channels=(numpy.subtract(self.samples1, self.samples2),
                                                  numpy.subtract(self.samples2, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Difference 1", "Difference 2")))
        self.assertRaises(ValueError, self.spectrum.__sub__, spectrum3) # subtracting a Spectrum with a different length should fail
        self.assertRaises(ValueError, self.spectrum.__sub__, spectrum4) # subtracting a Spectrum with a different sampling rate should fail
        self.assertRaises(ValueError, self.spectrum.__sub__, spectrum2) # subtracting a Spectrum with less channels should fail
        self.assertRaises(ValueError, spectrum2.__sub__, self.spectrum) # subtracting a Spectrum with more channels should fail
        # __mul__
        self.assertEqual(self.spectrum * spectrum1,
                         sumpf.Spectrum(channels=(numpy.multiply(self.samples1, self.samples2),
                                                  numpy.multiply(self.samples2, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Product 1", "Product 2")))
        self.assertEqual(self.spectrum * 5.2, sumpf.modules.AmplifySpectrum(input=self.spectrum, factor=5.2).GetOutput())
        self.assertEqual(4 * self.spectrum, sumpf.modules.AmplifySpectrum(input=self.spectrum, factor=4.0).GetOutput())
        self.assertRaises(ValueError, self.spectrum.__mul__, spectrum3) # multiplying with a Spectrum with a different length should fail
        self.assertRaises(ValueError, self.spectrum.__mul__, spectrum4) # multiplying with a Spectrum with a different sampling rate should fail
        self.assertRaises(ValueError, self.spectrum.__mul__, spectrum2) # multiplying with a Spectrum with less channels should fail
        self.assertRaises(ValueError, spectrum2.__mul__, self.spectrum) # multiplying with a Spectrum with more channels should fail
        # __truediv__
        self.assertEqual(self.spectrum / spectrum1,
                         sumpf.Spectrum(channels=(numpy.divide(self.samples1, self.samples2),
                                                  numpy.divide(self.samples2, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Quotient 1", "Quotient 2")))
        self.assertEqual(self.spectrum / 2.0, sumpf.modules.AmplifySpectrum(input=self.spectrum, factor=0.5).GetOutput())
        self.assertRaises(ValueError, self.spectrum.__truediv__, spectrum3)         # dividing by a Spectrum with a different length should fail
        self.assertRaises(ValueError, self.spectrum.__truediv__, spectrum4)         # dividing by a Spectrum with a different sampling rate should fail
        self.assertRaises(ValueError, self.spectrum.__truediv__, spectrum2)         # dividing by a Spectrum with less channels should fail
        self.assertRaises(ValueError, spectrum2.__truediv__, self.spectrum)         # dividing by a Spectrum with more channels should fail
        self.assertRaises(ZeroDivisionError, self.spectrum.__truediv__, spectrum5)  # dividing by a Spectrum with a channel with only zero values should fail
        self.assertRaises(ZeroDivisionError, self.spectrum.__truediv__, 0.0)        # dividing by zero should fail

