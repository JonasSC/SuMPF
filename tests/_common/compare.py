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

def compare_signals_almost_equal(testcase, signal1, signal2, places=7, compare_labels=True):
    """
    Compares two Signals with a TestCase's almostEqual method.
    The sampling rate and the labels are compared to be absolutely equal, while
    the channels' samples are compared to be almost equal.
    @param testcase: the TestCase whose comparison methods shall be used.
    @param signal1: the first Signal that shall be compared
    @param signal2: the second Signal that shall be compared
    @param compare_labels: True if the labels shall also be compared. False, if differing labels shall not lead to a failure
    """
    testcase.assertEqual(signal1.GetSamplingRate(), signal2.GetSamplingRate())
    compare_channeldatas_almost_equal(testcase=testcase, data1=signal1, data2=signal2, places=places, compare_labels=compare_labels)

def compare_spectrums_almost_equal(testcase, spectrum1, spectrum2, places=7, compare_labels=True):
    """
    Compares two Spectrums with a TestCase's almostEqual method.
    The resolution and the labels are compared to be absolutely equal, while
    the channels' samples are compared to be almost equal.
    @param testcase: the TestCase whose comparison methods shall be used.
    @param spectrum1: the first Spectrum that shall be compared
    @param spectrum2: the second Spectrum that shall be compared
    @param compare_labels: True if the labels shall also be compared. False, if differing labels shall not lead to a failure
    """
    testcase.assertEqual(spectrum1.GetResolution(), spectrum2.GetResolution())
    compare_channeldatas_almost_equal(testcase=testcase, data1=spectrum1, data2=spectrum2, places=places, compare_labels=compare_labels)

def compare_channeldatas_almost_equal(testcase, data1, data2, places, compare_labels):
    """
    Compares two ChannelData instances with a TestCase's almostEqual method.
    The labels are compared to be absolutely equal, while the channels' samples
    are compared to be almost equal.
    @param testcase: the TestCase whose comparison methods shall be used.
    @param data1: the first data set that shall be compared
    @param data2: the second data set that shall be compared
    @param compare_labels: True if the labels shall also be compared. False, if differing labels shall not lead to a failure
    """
    testcase.assertEqual(len(data1.GetChannels()), len(data2.GetChannels()))
    testcase.assertEqual(len(data1), len(data2))
    if compare_labels:
        testcase.assertEqual(data1.GetLabels(), data2.GetLabels())
    for c in range(len(data1.GetChannels())):
        for s in range(len(data1)):
            testcase.assertAlmostEqual(data1.GetChannels()[c][s], data2.GetChannels()[c][s], places)

