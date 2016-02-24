# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2016 Jonas Schulte-Coerne
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

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy


class TestSignal(unittest.TestCase):
    def setUp(self):
        samples1 = []
        samples2 = []
        for i in range(1, 11):
            samples1.append(float(i))
            samples2.append(2.0 * i)
        self.samples1 = tuple(samples1)
        self.samples2 = tuple(samples2)
        self.channels = (self.samples1, self.samples2)
        self.signal = sumpf.Signal(channels=self.channels, samplingrate=4410.0, labels=("1", "2"))

    def test_signal_initialization(self):
        """
        Tests if all data is stored in the Signal correctly
        """
        self.assertEqual(self.signal.GetChannels(), self.channels)      # test if the channels are set correctly
        self.assertEqual(self.signal.GetSamplingRate(), 4410.0)         # test if the sampling rate is set correctly
        self.assertEqual(len(self.signal), len(self.samples1))          # test if the length is computed correctly
        self.assertEqual(self.signal.GetDuration(), 10.0 / 4410.0)      # test if the duration is computed correctly
        self.assertEqual(self.signal.GetLabels(), ("1", "2"))           # test if labels are set correctly
        sig = sumpf.Signal(channels=self.channels, samplingrate=4410.0, labels=("1",))
        self.assertEqual(sig.GetLabels(), ("1", None))                  # test if the labels are set correctly, if the given tuple of labels is shorter than the tuple of channels
        sig = sumpf.Signal(channels=self.channels, samplingrate=4410.0, labels=("1", "2", "3"))
        self.assertEqual(sig.GetLabels(), ("1", "2"))                   # test if the labels are set correctly, if the given tuple of labels is longer than the tuple of channels
        sig = sumpf.Signal(channels=self.channels, samplingrate=4410.0, labels=(None, "2"))
        self.assertEqual(sig.GetLabels(), (None, "2"))                  # test if the labels are set correctly, if a label is None
        sig = sumpf.Signal()
        self.assertTrue(sig.IsEmpty())                                  # creating a Signal without passing constructor arguments should create an empty Signal
        self.assertEqual(sig.GetChannels(), ((0.0, 0.0),))              # an empty Signal should have one channel with two 0.0 samples

    def test_invalid_signal_initialization(self):
        """
        Tests if all errors are raised as expected
        """
        def createSignalWithoutChannels():
            sumpf.Signal(channels=())
        def createSignalWithEmptyChannels():
            sumpf.Signal(channels=((), ()))
        def createSignalWithTooShortChannels():
            sumpf.Signal(channels=((1,), (2,)))
        def createSignalWithUnEqualChannels():
            sumpf.Signal(channels=(self.samples1, self.samples2[1:-1]))
        def createSignalWithWrongLabels():
            sumpf.Signal(channels=self.channels, labels=("1", 2))
        self.assertRaises(ValueError, createSignalWithoutChannels)      # creating a Signal without channels should fail
        self.assertRaises(ValueError, createSignalWithEmptyChannels)    # creating a Signal with empty channels should fail
        self.assertRaises(ValueError, createSignalWithTooShortChannels) # creating a Signal with channels shorter than 2 samples should fail
        self.assertRaises(ValueError, createSignalWithUnEqualChannels)  # creating a Signal with channels of different length should fail
        self.assertRaises(TypeError, createSignalWithWrongLabels)       # creating a Signal with non-string labels should fail

    def test_comparison(self):
        """
        Tests if the comparison methods work as expected.
        """
        cmpsignal_equal = sumpf.Signal(channels=[self.samples1, self.samples2], samplingrate=4410, labels=["1", "2"])
        cmpsignal_channels1 = sumpf.Signal(channels=(self.samples2, self.samples1), samplingrate=4410.0, labels=("1", "2"))
        cmpsignal_channels2 = sumpf.Signal(channels=(self.samples1, self.samples1), samplingrate=4410.0, labels=("1", "2"))
        cmpsignal_channels3 = sumpf.Signal(channels=(self.samples1,), samplingrate=4410.0, labels=("1", "2"))
        cmpsignal_channels4 = sumpf.Signal(channels=(self.samples2, self.samples2), samplingrate=4410.0, labels=("1", "2"))
        cmpsignal_samplingrate = sumpf.Signal(channels=(self.samples1, self.samples2), samplingrate=4411.0, labels=("1", "2"))
        cmpsignal_labels = sumpf.Signal(channels=(self.samples1, self.samples2), samplingrate=4410.0, labels=("1", "3"))
        self.assertEqual(self.signal, self.signal)                  # same Signals should be recognized as equal
        self.assertEqual(self.signal, cmpsignal_equal)              # equal Signals should be recognized as equal
        self.assertNotEqual(self.signal, cmpsignal_channels1)       # Signals with different channels should not be recognized as equal
        self.assertNotEqual(self.signal, cmpsignal_channels2)       #   "
        self.assertNotEqual(self.signal, cmpsignal_channels3)       #   "
        self.assertNotEqual(self.signal, cmpsignal_channels4)       #   "
        self.assertNotEqual(self.signal, cmpsignal_samplingrate)    # Signals with different sampling rates should not be recognized as equal
        self.assertNotEqual(self.signal, cmpsignal_labels)          # Signals with different labels should not be recognized as equal

    def test_types(self):
        """
        Tests if the data is stored in the correct types
        """
        signal = sumpf.Signal(channels=[[1, 2]], samplingrate=48000, labels=["As list"])
        self.assertIsInstance(signal.GetChannels(), tuple)          # the channels should be stored in a tuple
        self.assertIsInstance(signal.GetChannels()[0], tuple)       # the channels should be tuples
        self.assertIsInstance(signal.GetSamplingRate(), float)      # the sampling rate should be a float
        self.assertIsInstance(signal.GetLabels(), tuple)            # the labels should be stored in a tuple
        self.assertIsInstance(signal.GetLabels()[0], str)           # the labels can be either ascii or unicode strings

    def test_overloaded_operators(self):
        """
        Tests the overloaded operators of the Signal class.
        The comparison operators are tested in test_comparison.
        The length getter is tested in test_signal_initialization
        """
        # __repr__
        newlocals = {}
        exec("newsignal = sumpf." + repr(self.signal), globals(), newlocals)
        self.assertEqual(newlocals["newsignal"], self.signal)
        # __str__
        self.assertEqual(str(self.signal), "<_sumpf._data.signal.Signal object (length: 10, sampling rate: 4410.00, channel count: 2) at 0x%x>" % id(self.signal))
        # __getitem__
        self.assertEqual(self.signal[2:8], sumpf.Signal(channels=(self.samples1[2:8], self.samples2[2:8]), samplingrate=self.signal.GetSamplingRate(), labels=self.signal.GetLabels()))
        self.assertEqual(self.signal[3:], sumpf.Signal(channels=(self.samples1[3:], self.samples2[3:]), samplingrate=self.signal.GetSamplingRate(), labels=self.signal.GetLabels()))
        self.assertEqual(self.signal[4:-2], sumpf.Signal(channels=(self.samples1[4:-2], self.samples2[4:-2]), samplingrate=self.signal.GetSamplingRate(), labels=self.signal.GetLabels()))
        self.assertRaises(ValueError, self.signal.__getitem__, 5)
        self.assertRaises(ValueError, self.signal.__getitem__, slice(5, 6))
        self.assertRaises(ValueError, self.signal.__getitem__, slice(5, 8, 2))
        self.assertRaises(ValueError, self.signal.__getitem__, slice(6, 3))
        # algebra
        signal1 = sumpf.Signal(channels=(self.samples2, self.samples1), samplingrate=4410.0, labels=("1", "2"))
        signal2 = sumpf.Signal(channels=(self.samples1,), samplingrate=4410.0, labels=("3", "4"))
        signal3 = sumpf.Signal(channels=(self.samples1, self.samples2, self.samples1), samplingrate=4410.0, labels=("5", "6"))
        signal4 = sumpf.Signal(channels=((1.0,) * 12, (2.0,) * 12), samplingrate=4410.0, labels=("7", "8"))
        signal5 = sumpf.Signal(channels=((1.0,) * 10, (2.0,) * 10), samplingrate=4800.0, labels=("9", "10"))
        signal6 = sumpf.Signal(channels=((1.0,) * 10, (0.0,) * 10), samplingrate=4410.0, labels=("11", "12"))
        signal7 = sumpf.Signal(channels=((0.0, 0.0),) * 2, samplingrate=4410.0)
        signal8 = sumpf.Signal(channels=((0.0, 0.0),) * 3, samplingrate=4410.0)
        signal9 = sumpf.Signal(channels=((0.0, 0.0),) * 2, samplingrate=4800.0)
        # __add__
        self.assertEqual(self.signal + signal1,
                         sumpf.Signal(channels=(numpy.add(self.samples1, self.samples2), numpy.add(self.samples2, self.samples1)),
                                      samplingrate=4410.0,
                                      labels=("Sum 1", "Sum 2")))   # adding signals with the same number of channels
        self.assertEqual(self.signal + signal2,
                         sumpf.Signal(channels=(numpy.add(self.samples1, self.samples1), numpy.add(self.samples2, self.samples1)),
                                      samplingrate=4410.0,
                                      labels=("Sum 1", "Sum 2")))   # adding with a signal, that has only one channel
        self.assertEqual(signal2 + signal1,
                         sumpf.Signal(channels=(numpy.add(self.samples2, self.samples1), numpy.add(self.samples1, self.samples1)),
                                      samplingrate=4410.0,
                                      labels=("Sum 1", "Sum 2")))   # adding with a signal, that has only one channel
        self.assertEqual(self.signal + signal7,
                         sumpf.Signal(channels=self.signal.GetChannels(),
                                      samplingrate=4410.0,
                                      labels=("Sum 1", "Sum 2")))   # adding with an empty signal, that has more than one channels and the wrong length
        for number in (2.0, -2.7, 3):
            self.assertEqual(self.signal + number,
                             sumpf.Signal(channels=(numpy.add(self.samples1, number), numpy.add(self.samples2, number)),
                                          samplingrate=4410.0,
                                          labels=self.signal.GetLabels()))  # adding with a number
            self.assertEqual(number + self.signal,
                             sumpf.Signal(channels=(numpy.add(self.samples1, number), numpy.add(self.samples2, number)),
                                          samplingrate=4410.0,
                                          labels=self.signal.GetLabels()))  # adding with a number
        def add(a, b):
            return a + b
        self.assertRaises(ValueError, add, *(self.signal, signal3)) # adding a Signal with a different number of channels should fail, if none of the channel counts is one
        self.assertRaises(ValueError, add, *(self.signal, signal4)) # adding a Signal with a different length should fail
        self.assertRaises(ValueError, add, *(self.signal, signal5)) # adding a Signal with a different sampling rate should fail
        self.assertRaises(ValueError, add, *(self.signal, signal8)) # adding a Signal with a different number of channels should fail, even if the Signal is empty
        self.assertRaises(ValueError, add, *(self.signal, signal9)) # adding a Signal with a different sampling rate should fail, even if the Signal is empty
        # __sub__
        self.assertEqual(self.signal - signal1,
                         sumpf.Signal(channels=(numpy.subtract(self.samples1, self.samples2), numpy.subtract(self.samples2, self.samples1)),
                                      samplingrate=4410.0,
                                      labels=("Difference 1", "Difference 2"))) # subtracting signals with the same number of channels
        self.assertEqual(self.signal - signal2,
                         sumpf.Signal(channels=(numpy.subtract(self.samples1, self.samples1), numpy.subtract(self.samples2, self.samples1)),
                                      samplingrate=4410.0,
                                      labels=("Difference 1", "Difference 2"))) # subtracting a signal, that has only one channel
        self.assertEqual(signal2 - signal1,
                         sumpf.Signal(channels=(numpy.subtract(self.samples1, self.samples2), numpy.subtract(self.samples1, self.samples1)),
                                      samplingrate=4410.0,
                                      labels=("Difference 1", "Difference 2"))) # subtracting from a signal, that has only one channel
        self.assertEqual(self.signal - signal7,
                         sumpf.Signal(channels=self.signal.GetChannels(),
                                      samplingrate=4410.0,
                                      labels=("Difference 1", "Difference 2")))   # subtracting an empty signal, that has more than one channel and the wrong length
        self.assertEqual(signal7 - self.signal,
                         sumpf.Signal(channels=numpy.subtract(0.0, self.signal.GetChannels()),
                                      samplingrate=4410.0,
                                      labels=("Difference 1", "Difference 2")))   # subtracting from an empty signal, that has more than one channel and the wrong length
        for number in (2.0, -2.7, 3):
            self.assertEqual(self.signal - number,
                             sumpf.Signal(channels=(numpy.subtract(self.samples1, number), numpy.subtract(self.samples2, number)),
                                          samplingrate=4410.0,
                                          labels=self.signal.GetLabels()))  # subtracting a number
            self.assertEqual(number - self.signal,
                             sumpf.Signal(channels=(numpy.subtract(number, self.samples1), numpy.subtract(number, self.samples2)),
                                          samplingrate=4410.0,
                                          labels=self.signal.GetLabels()))  # subtracting from a number
        def sub(a, b):
            return a - b
        self.assertRaises(ValueError, sub, *(self.signal, signal3)) # subtracting a Signal with a different number of channels should fail, if none of the channel counts is one
        self.assertRaises(ValueError, sub, *(self.signal, signal4)) # subtracting a Signal with a different length should fail
        self.assertRaises(ValueError, sub, *(self.signal, signal5)) # subtracting a Signal with a different sampling rate should fail
        self.assertRaises(ValueError, sub, *(self.signal, signal8)) # subtracting a Signal with a different number of channels should fail, even if the Signal is empty
        self.assertRaises(ValueError, sub, *(self.signal, signal9)) # subtracting a Signal with a different sampling rate should fail, even if the Signal is empty
        self.assertRaises(ValueError, sub, *(signal8, self.signal)) # subtracting from a Signal with a different number of channels should fail, even if the Signal is empty
        self.assertRaises(ValueError, sub, *(signal9, self.signal)) # subtracting from a Signal with a different sampling rate should fail, even if the Signal is empty
        # __mul__
        self.assertEqual(self.signal * signal1,
                         sumpf.Signal(channels=(numpy.multiply(self.samples1, self.samples2), numpy.multiply(self.samples2, self.samples1)),
                                      samplingrate=4410.0,
                                      labels=("Product 1", "Product 2")))   # multiplying signals with the same number of channels
        self.assertEqual(self.signal * signal2,
                         sumpf.Signal(channels=(numpy.multiply(self.samples1, self.samples1), numpy.multiply(self.samples2, self.samples1)),
                                      samplingrate=4410.0,
                                      labels=("Product 1", "Product 2")))   # multiplying with a signal, that has only one channel
        self.assertEqual(signal2 * signal1,
                         sumpf.Signal(channels=(numpy.multiply(self.samples2, self.samples1), numpy.multiply(self.samples1, self.samples1)),
                                      samplingrate=4410.0,
                                      labels=("Product 1", "Product 2")))   # multiplying with a signal, that has only one channel
        self.assertEqual(self.signal * signal7,
                         sumpf.Signal(channels=self.signal.GetChannels(),
                                      samplingrate=4410.0,
                                      labels=("Product 1", "Product 2")))   # multiplying with an empty signal, that has more than one channel and the wrong length
        for number in (2.0, -2.7, 3):
            self.assertEqual(self.signal * number,
                             sumpf.Signal(channels=(numpy.multiply(self.samples1, number), numpy.multiply(self.samples2, number)),
                                          samplingrate=4410.0,
                                          labels=self.signal.GetLabels()))  # multiplying with a number
            self.assertEqual(number * self.signal,
                             sumpf.Signal(channels=(numpy.multiply(self.samples1, number), numpy.multiply(self.samples2, number)),
                                          samplingrate=4410.0,
                                          labels=self.signal.GetLabels()))  # multiplying with a number
        def mul(a, b):
            return a * b
        self.assertRaises(ValueError, mul, *(self.signal, signal3)) # multiplying a Signal with a different number of channels should fail, if none of the channel counts is one
        self.assertRaises(ValueError, mul, *(self.signal, signal4)) # multiplying a Signal with a different length should fail
        self.assertRaises(ValueError, mul, *(self.signal, signal5)) # multiplying a Signal with a different sampling rate should fail
        self.assertRaises(ValueError, mul, *(self.signal, signal8)) # multiplying a Signal with a different number of channels should fail, even if the Signal is empty
        self.assertRaises(ValueError, mul, *(self.signal, signal9)) # multiplying a Signal with a different sampling rate should fail, even if the Signal is empty
        # __truediv__
        self.assertEqual(self.signal / signal1,
                         sumpf.Signal(channels=(numpy.true_divide(self.samples1, self.samples2), numpy.true_divide(self.samples2, self.samples1)),
                                      samplingrate=4410.0,
                                      labels=("Quotient 1", "Quotient 2"))) # dividing signals with the same number of channels
        self.assertEqual(self.signal / signal2,
                         sumpf.Signal(channels=(numpy.true_divide(self.samples1, self.samples1), numpy.true_divide(self.samples2, self.samples1)),
                                      samplingrate=4410.0,
                                      labels=("Quotient 1", "Quotient 2"))) # dividing by a signal, that has only one channel
        self.assertEqual(signal2 / signal1,
                         sumpf.Signal(channels=(numpy.true_divide(self.samples1, self.samples2), numpy.true_divide(self.samples1, self.samples1)),
                                      samplingrate=4410.0,
                                      labels=("Quotient 1", "Quotient 2"))) # dividing a signal, that has only one channel
        self.assertEqual(signal7 / self.signal,
                         sumpf.Signal(channels=numpy.true_divide(0.0, self.signal.GetChannels()),
                                      samplingrate=4410.0,
                                      labels=("Quotient 1", "Quotient 2"))) # dividing an empty signal, that has more than one channel and the wrong length
        for number in (2.0, -2.7, 3):
            self.assertEqual(self.signal / number,
                             sumpf.Signal(channels=(numpy.true_divide(self.samples1, number), numpy.true_divide(self.samples2, number)),
                                          samplingrate=4410.0,
                                          labels=self.signal.GetLabels()))  # dividing by a number
            self.assertEqual(number / self.signal,
                             sumpf.Signal(channels=(numpy.true_divide(number, self.samples1), numpy.true_divide(number, self.samples2)),
                                          samplingrate=4410.0,
                                          labels=self.signal.GetLabels()))  # dividing a number
        def div(a, b):
            return a / b
        self.assertRaises(ValueError, div, *(self.signal, signal3)) # dividing by a Signal with a different number of channels should fail, if none of the channel counts is one
        self.assertRaises(ValueError, div, *(self.signal, signal4)) # dividing by a Signal with a different length should fail
        self.assertRaises(ValueError, div, *(self.signal, signal5)) # dividing by a Signal with a different sampling rate should fail
        self.assertRaises(ValueError, div, *(signal8, self.signal)) # dividing a Signal with a different number of channels should fail, even if the Signal is empty
        self.assertRaises(ValueError, div, *(signal9, self.signal)) # dividing a Signal with a different sampling rate should fail, even if the Signal is empty
        self.assertRaises(ZeroDivisionError, div, *(self.signal, signal6))  # dividing a Signal by a Signal with a channel with only zero values should fail
        self.assertRaises(ZeroDivisionError, div, *(4.3, signal9))  # dividing a scalar by a Signal with a channel with only zero values should fail
        self.assertRaises(ZeroDivisionError, div, *(self.signal, 0.0))  # dividing by zero should fail

