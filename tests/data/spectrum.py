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
            samples1.append((i * ((-0.9) ** i)) + i * 0.3j)
            samples2.append(0.2 * i)
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
        phase = (tuple(math.acos(c.real / ((c.real ** 2 + c.imag ** 2) ** 0.5)) for c in self.spectrum.GetChannels()[0]), (0.0,) * len(self.spectrum))
        self.assertLess(numpy.sum(numpy.subtract(self.spectrum.GetPhase(), phase)), 1e-15)  # test if phase is computed correctly
        real = (tuple(i * ((-0.9) ** i) for i in range(1, 11)), self.samples2)
        self.assertEqual(self.spectrum.GetReal(), real)
        imag = (tuple(i * 0.3 for i in range(1, 11)), (0.0,) * len(self.spectrum))
        self.assertEqual(self.spectrum.GetImaginary(), imag)
        self.assertEqual(self.spectrum.GetLabels(), ("1", "2"))         # test if labels are set correctly
        spk = sumpf.Spectrum(channels=self.channels, resolution=4800.0, labels=("1",))
        self.assertEqual(spk.GetLabels(), ("1", None))                  # test if labels are set correctly, if the given tuple of labels is shorter than the tuple of channels
        spk = sumpf.Spectrum(channels=self.channels, resolution=4800.0, labels=("1", "2", "3"))
        self.assertEqual(spk.GetLabels(), ("1", "2"))                   # test if labels are set correctly, if the given tuple of labels is longer than the tuple of channels
        spk = sumpf.Spectrum(channels=self.channels, resolution=4800.0, labels=(None, "2"))
        self.assertEqual(spk.GetLabels(), (None, "2"))                  # test if labels are set correctly, if a label is None
        spk = sumpf.Spectrum()
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
        # test spectrums
        spectrum1 = sumpf.Spectrum(channels=(self.samples2, self.samples1), resolution=4800.0, labels=("1", "2"))
        spectrum2 = sumpf.Spectrum(channels=(self.samples1,), resolution=4800.0, labels=("3", "4"))
        spectrum3 = sumpf.Spectrum(channels=(self.samples1, self.samples2, self.samples1), resolution=4800.0, labels=("5", "6"))
        spectrum4 = sumpf.Spectrum(channels=((1.0 + 4.2j,) * 12, (2.0,) * 12), resolution=4800.0, labels=("7", "8"))
        spectrum5 = sumpf.Spectrum(channels=((1.0,) * 10, (2.0 + 2.3j,) * 10), resolution=4410.0, labels=("9", "10"))
        spectrum6 = sumpf.Spectrum(channels=((0.0,) * 10, (0.0,) * 10), resolution=4800.0, labels=("11", "12"))
        spectrum7 = sumpf.Spectrum(channels=((0.0, 0.0),) * 3, resolution=4800.0)
        # __repr__
        newlocals = {}
        exec("newspectrum = sumpf." + repr(self.spectrum), globals(), newlocals)
        self.assertEqual(newlocals["newspectrum"], self.spectrum)
        # __str__
        self.assertEqual(str(self.spectrum), "<_sumpf._data.spectrum.Spectrum object (length: 10, resolution: 4800.00, channel count: 2) at 0x%x>" % id(self.spectrum))
        # __add__
        self.assertEqual(self.spectrum + spectrum1,
                         sumpf.Spectrum(channels=(numpy.add(self.samples1, self.samples2), numpy.add(self.samples2, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Sum 1", "Sum 2"))) # adding spectrums with the same number of channels
        self.assertEqual(self.spectrum + spectrum2,
                         sumpf.Spectrum(channels=(numpy.add(self.samples1, self.samples1), numpy.add(self.samples2, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Sum 1", "Sum 2"))) # adding with a spectrum, that has only one channel
        self.assertEqual(spectrum2 + spectrum1,
                         sumpf.Spectrum(channels=(numpy.add(self.samples2, self.samples1), numpy.add(self.samples1, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Sum 1", "Sum 2"))) # adding with a spectrum, that has only one channel
        for number in (-2.0, -2.7 + 4.1j, 3, 5 - 1j):
            self.assertEqual(self.spectrum + number,
                             sumpf.Spectrum(channels=(numpy.add(self.samples1, number), numpy.add(self.samples2, number)),
                                            resolution=4800.0,
                                            labels=self.spectrum.GetLabels()))  # adding with a number
            self.assertEqual(number + self.spectrum,
                             sumpf.Spectrum(channels=(numpy.add(self.samples1, number), numpy.add(self.samples2, number)),
                                            resolution=4800.0,
                                            labels=self.spectrum.GetLabels()))  # adding with a number
        self.assertEqual(self.spectrum + [12.3, 9],
                         sumpf.Spectrum(channels=(numpy.add(self.samples1, 12.3), numpy.add(self.samples2, 9)),
                                        resolution=4800.0,
                                        labels=self.spectrum.GetLabels()))  # adding a list
        self.assertEqual((12.3, 9) + self.spectrum,
                         sumpf.Spectrum(channels=(numpy.add(12.3, self.samples1), numpy.add(9, self.samples2)),
                                        resolution=4800.0,
                                        labels=self.spectrum.GetLabels()))  # adding a tuple
        def add(a, b):
            return a + b
        self.assertRaises(ValueError, add, *(self.spectrum, spectrum3))         # adding a Spectrum with a different number of channels should fail, if none of the channel counts is one
        self.assertRaises(ValueError, add, *(self.spectrum, spectrum4))         # adding a Spectrum with a different length should fail
        self.assertRaises(ValueError, add, *(self.spectrum, spectrum5))         # adding a Spectrum with a different sampling rate should fail
        self.assertRaises(ValueError, add, *(self.spectrum, (1.0, -2.0, 3.0)))  # adding a Spectrum with a tuple of wrong length should fail
        self.assertRaises(ValueError, add, *((-2.0,), self.spectrum))           # adding a Spectrum with a tuple of wrong length should fail
        # __sub__
        self.assertEqual(self.spectrum - spectrum1,
                         sumpf.Spectrum(channels=(numpy.subtract(self.samples1, self.samples2), numpy.subtract(self.samples2, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Difference 1", "Difference 2")))   # subtracting spectrums with the same number of channels
        self.assertEqual(self.spectrum - spectrum2,
                         sumpf.Spectrum(channels=(numpy.subtract(self.samples1, self.samples1), numpy.subtract(self.samples2, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Difference 1", "Difference 2")))   # subtracting a spectrum, that has only one channel
        self.assertEqual(spectrum2 - spectrum1,
                         sumpf.Spectrum(channels=(numpy.subtract(self.samples1, self.samples2), numpy.subtract(self.samples1, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Difference 1", "Difference 2")))   # subtracting from a spectrum, that has only one channel
        for number in (-2.0, -2.7 + 4.1j, 3, 5 - 1j):
            self.assertEqual(self.spectrum - number,
                             sumpf.Spectrum(channels=(numpy.subtract(self.samples1, number), numpy.subtract(self.samples2, number)),
                                            resolution=4800.0,
                                            labels=self.spectrum.GetLabels()))  # subtracting a number
            self.assertEqual(number - self.spectrum,
                             sumpf.Spectrum(channels=(numpy.subtract(number, self.samples1), numpy.subtract(number, self.samples2)),
                                            resolution=4800.0,
                                            labels=self.spectrum.GetLabels()))  # subtracting from a number
        self.assertEqual(self.spectrum - [12.3, 9],
                         sumpf.Spectrum(channels=(numpy.subtract(self.samples1, 12.3), numpy.subtract(self.samples2, 9)),
                                        resolution=4800.0,
                                        labels=self.spectrum.GetLabels()))  # subtracting a list
        self.assertEqual((12.3, 9) - self.spectrum,
                         sumpf.Spectrum(channels=(numpy.subtract(12.3, self.samples1), numpy.subtract(9, self.samples2)),
                                        resolution=4800.0,
                                        labels=self.spectrum.GetLabels()))  # subtracting from a tuple
        def sub(a, b):
            return a - b
        self.assertRaises(ValueError, sub, *(self.spectrum, spectrum3))         # subtracting a Spectrum with a different number of channels should fail, if none of the channel counts is one
        self.assertRaises(ValueError, sub, *(self.spectrum, spectrum4))         # subtracting a Spectrum with a different length should fail
        self.assertRaises(ValueError, sub, *(self.spectrum, spectrum5))         # subtracting a Spectrum with a different sampling rate should fail
        self.assertRaises(ValueError, sub, *(self.spectrum, (1.0, -2.0, 3.0)))  # subtracting a tuple of wrong length from a Spectrum should fail
        self.assertRaises(ValueError, sub, *((-2.0,), self.spectrum))           # subtracting a Spectrum from a tuple of wrong length should fail
        # __mul__
        self.assertEqual(self.spectrum * spectrum1,
                         sumpf.Spectrum(channels=(numpy.multiply(self.samples1, self.samples2), numpy.multiply(self.samples2, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Product 1", "Product 2"))) # multiplying spectrums with the same number of channels
        self.assertEqual(self.spectrum * spectrum2,
                         sumpf.Spectrum(channels=(numpy.multiply(self.samples1, self.samples1), numpy.multiply(self.samples2, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Product 1", "Product 2"))) # multiplying with a spectrum, that has only one channel
        self.assertEqual(spectrum2 * spectrum1,
                         sumpf.Spectrum(channels=(numpy.multiply(self.samples2, self.samples1), numpy.multiply(self.samples1, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Product 1", "Product 2"))) # multiplying with a spectrum, that has only one channel
        for number in (-2.0, -2.7 + 4.1j, 3, 5 - 1j):
            self.assertEqual(self.spectrum * number,
                             sumpf.Spectrum(channels=(numpy.multiply(self.samples1, number), numpy.multiply(self.samples2, number)),
                                            resolution=4800.0,
                                            labels=self.spectrum.GetLabels()))  # multiplying with a number
            self.assertEqual(number * self.spectrum,
                             sumpf.Spectrum(channels=(numpy.multiply(self.samples1, number), numpy.multiply(self.samples2, number)),
                                            resolution=4800.0,
                                            labels=self.spectrum.GetLabels()))  # multiplying with a number
        self.assertEqual(self.spectrum * [12.3, 9],
                         sumpf.Spectrum(channels=(numpy.multiply(self.samples1, 12.3), numpy.multiply(self.samples2, 9)),
                                        resolution=4800.0,
                                        labels=self.spectrum.GetLabels()))  # multiplying with a list
        self.assertEqual((12.3, 9) * self.spectrum,
                         sumpf.Spectrum(channels=(numpy.multiply(12.3, self.samples1), numpy.multiply(9, self.samples2)),
                                        resolution=4800.0,
                                        labels=self.spectrum.GetLabels()))  # multiplying with a tuple
        def mul(a, b):
            return a * b
        self.assertRaises(ValueError, mul, *(self.spectrum, spectrum3))         # multiplying a Spectrum with a different number of channels should fail, if none of the channel counts is one
        self.assertRaises(ValueError, mul, *(self.spectrum, spectrum4))         # multiplying a Spectrum with a different length should fail
        self.assertRaises(ValueError, mul, *(self.spectrum, spectrum5))         # multiplying a Spectrum with a different sampling rate should fail
        self.assertRaises(ValueError, mul, *(self.spectrum, (1.0, -2.0, 3.0)))  # multiplying a Spectrum with a tuple of wrong length should fail
        self.assertRaises(ValueError, mul, *((-2.0,), self.spectrum))           # multiplying a Spectrum with a tuple of wrong length should fail
        # __truediv__
        self.assertEqual(self.spectrum / spectrum1,
                         sumpf.Spectrum(channels=(numpy.true_divide(self.samples1, self.samples2), numpy.true_divide(self.samples2, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Quotient 1", "Quotient 2")))   # dividing spectrums with the same number of channels
        self.assertEqual(self.spectrum / spectrum2,
                         sumpf.Spectrum(channels=(numpy.true_divide(self.samples1, self.samples1), numpy.true_divide(self.samples2, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Quotient 1", "Quotient 2")))   # dividing by a spectrum, that has only one channel
        self.assertEqual(spectrum2 / spectrum1,
                         sumpf.Spectrum(channels=(numpy.true_divide(self.samples1, self.samples2), numpy.true_divide(self.samples1, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Quotient 1", "Quotient 2")))   # dividing a spectrum, that has only one channel
        for number in (-2.0, -2.7 + 4.1j, 3, 5 - 1j):
            self.assertEqual(self.spectrum / number,
                             sumpf.Spectrum(channels=numpy.true_divide((self.samples1, self.samples2), number),
                                            resolution=4800.0,
                                            labels=self.spectrum.GetLabels()))  # dividing by a number
            self.assertEqual(number / self.spectrum,
                             sumpf.Spectrum(channels=numpy.true_divide(number, (self.samples1, self.samples2)),
                                            resolution=4800.0,
                                            labels=self.spectrum.GetLabels()))  # dividing a number
        self.assertEqual(self.spectrum / [12.3, 9],
                         sumpf.Spectrum(channels=(numpy.true_divide(self.samples1, 12.3), numpy.true_divide(self.samples2, 9)),
                                        resolution=4800.0,
                                        labels=self.spectrum.GetLabels()))  # dividing by a list
        self.assertEqual((12.3, 9) / self.spectrum,
                         sumpf.Spectrum(channels=(numpy.true_divide(12.3, self.samples1), numpy.true_divide(9, self.samples2)),
                                        resolution=4800.0,
                                        labels=self.spectrum.GetLabels()))  # dividing a tuple
        def div(a, b):
            return a / b
        self.assertRaises(ValueError, div, *(self.spectrum, spectrum3))         # dividing by a Spectrum with a different number of channels should fail, if none of the channel counts is one
        self.assertRaises(ValueError, div, *(self.spectrum, spectrum4))         # dividing by a Spectrum with a different length should fail
        self.assertRaises(ValueError, div, *(self.spectrum, spectrum5))         # dividing by a Spectrum with a different sampling rate should fail
        self.assertRaises(ValueError, div, *(self.spectrum, (1.0, -2.0, 3.0)))  # dividing a Spectrum by a tuple of wrong length should fail
        self.assertRaises(ValueError, div, *((-2.0,), self.spectrum))           # dividing a tuple of wrong length by a Spectrum should fail
        self.assertRaises(ZeroDivisionError, div, *(self.spectrum, spectrum6))  # dividing a Spectrum by a Spectrum with a channel with only zero values should fail
        self.assertRaises(ZeroDivisionError, div, *(9.5 + 4.6j, spectrum7))     # dividing a scalar by a Spectrum with a channel with only zero values should fail
        self.assertRaises(ZeroDivisionError, div, *(self.spectrum, 0.0))        # dividing by zero should fail
        self.assertRaises(ZeroDivisionError, div, *(self.spectrum, (4.2, 0.0))) # dividing by a tuple with a zero should fail
        # __pow__
        self.assertEqual(self.spectrum ** spectrum1,
                         sumpf.Spectrum(channels=(numpy.power(self.samples1, self.samples2), numpy.power(self.samples2, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Power 1", "Power 2")))   # power of two spectrums with the same number of channels
        self.assertEqual(self.spectrum ** spectrum2,
                         sumpf.Spectrum(channels=(numpy.power(self.samples1, self.samples1), numpy.power(self.samples2, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Power 1", "Power 2")))   # power of two spectrums, where the exponent has only one channel
        self.assertEqual(spectrum2 ** spectrum1,
                         sumpf.Spectrum(channels=(numpy.power(self.samples1, self.samples2), numpy.power(self.samples1, self.samples1)),
                                        resolution=4800.0,
                                        labels=("Power 1", "Power 2")))   # power of two spectrums, where the base has only one channel
        for number in (-2.0, -2.7 + 4.1j, 3, 5 - 1j):
            self.assertEqual(self.spectrum ** number,
                             sumpf.Spectrum(channels=numpy.power((self.samples1, self.samples2), number),
                                            resolution=4800.0,
                                            labels=self.spectrum.GetLabels()))  # a number as exponent
            self.assertEqual(number ** self.spectrum,
                             sumpf.Spectrum(channels=numpy.power(complex(number), (self.samples1, self.samples2)),
                                            resolution=4800.0,
                                            labels=self.spectrum.GetLabels()))  # a number as base
        if common.lib_available("numpy"):
            self.assertEqual(self.spectrum ** [12.3, 9],
                             sumpf.Spectrum(channels=(numpy.power(self.samples1, 12.3), numpy.power(numpy.complex_(self.samples2), 9.0)),
                                            resolution=4800.0,
                                            labels=self.spectrum.GetLabels()))  # a list as exponent
        else:
            self.assertEqual(self.spectrum ** [12.3, 9],
                             sumpf.Spectrum(channels=(numpy.power(self.samples1, 12.3), numpy.power(self.samples2, 9)),
                                            resolution=4800.0,
                                            labels=self.spectrum.GetLabels()))  # a list as exponent
        self.assertEqual((12.3, 9) ** self.spectrum,
                         sumpf.Spectrum(channels=(numpy.power(12.3, self.samples1), numpy.power(9, self.samples2)),
                                        resolution=4800.0,
                                        labels=self.spectrum.GetLabels()))  # a list as base
        def pow(a, b):
            return a ** b
        self.assertRaises(ValueError, pow, *(self.spectrum, spectrum3))             # computing the power of a Spectrum with a different number of channels should fail, if none of the channel counts is one
        self.assertRaises(ValueError, pow, *(self.spectrum, spectrum4))             # computing the power of a Spectrum with a different length should fail
        self.assertRaises(ValueError, pow, *(self.spectrum, spectrum5))             # computing the power of a Spectrum with a different resolution should fail
        self.assertRaises(ValueError, pow, *(self.spectrum, (1.0, -2.0, 3.0)))      # computing the power of a tuple of wrong length by a Spectrum should fail
        self.assertRaises(ValueError, pow, *((-2.0,), self.spectrum))               # computing the power of a Spectrum by a tuple of wrong length should fail
        self.assertRaises(ZeroDivisionError, pow, *(spectrum6, self.spectrum))      # computing the power of a zero Spectrum to a complex exponent should fail
        self.assertRaises(ZeroDivisionError, pow, *(spectrum6, 1.0 + 4.1j))         # computing the power of a zero Spectrum to a complex exponent should fail
        self.assertRaises(ZeroDivisionError, pow, *(spectrum6, (1.0 + 4.1j, 3.2)))  # computing the power of a zero Spectrum to a complex exponent should fail
        self.assertRaises(ZeroDivisionError, pow, *(0.0, self.spectrum))            # computing the power of zero to a complex exponent should fail
        self.assertRaises(ZeroDivisionError, pow, *((0.0, 0.0), self.spectrum))     # computing the power of a zero tuple to a complex exponent should fail
        float_spectrum = sumpf.Spectrum(channels=numpy.real(self.channels))
        complex_spectrum = sumpf.Spectrum(channels=numpy.complex_(numpy.real(self.channels)))
        self.assertEqual(float_spectrum ** float_spectrum, complex_spectrum ** complex_spectrum)
        self.assertEqual((-3.9) ** float_spectrum, (-3.9) ** complex_spectrum)
        self.assertEqual((-3.9, 7.8) ** float_spectrum, (-3.9, 7.8) ** complex_spectrum)
        self.assertEqual(float_spectrum ** (-3.9), complex_spectrum ** (-3.9))
        self.assertEqual(float_spectrum ** (-3.9, 7.8), complex_spectrum ** (-3.9, 7.8))

