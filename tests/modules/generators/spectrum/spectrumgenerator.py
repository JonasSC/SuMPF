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


class Generator(sumpf.internal.SpectrumGenerator):
    """
    An example class to test the SpectrumGenerator
    """
    def _GetSample(self, f):
        return 0.1



class SpectrumReceiver(object):
    """
    An example class that indicates, if it has received a Signal in it's SetSpectrum method.
    """
    def __init__(self):
        self.__received = False

    @sumpf.Input(sumpf.Spectrum)
    def SetSpectrum(self, signal):
        self.__received = True

    def Reset(self):
        self.__received = False

    def HasReceived(self):
        return self.__received



class TestSpectrumGenerator(unittest.TestCase):
    def setUp(self):
        self.gen = Generator(resolution=4800.0, length=10)

    def test_setter(self):
        """
        Tests if the setter methods raise no errors and notify the GetSpectrum-connector correctly.
        """
        rec = SpectrumReceiver()
        sumpf.connect(self.gen.GetSpectrum, rec.SetSpectrum)
        self.assertTrue(rec.HasReceived())      # Checks the notification on initial connection
        rec.Reset()
        self.gen.SetResolution(2400)
        self.assertTrue(rec.HasReceived())      # Checks the notification after SetResolution
        rec.Reset()
        self.gen.SetLength(20)
        self.assertTrue(rec.HasReceived())      # Checks the notification after SetLength
        rec.Reset()
        self.gen.SetMaximumFrequency(20000)
        self.assertTrue(rec.HasReceived())      # Checks the notification after SetDuration

    def test_maximumfrequency(self):
        """
        Tests if setting the output Spectrum's length with SetMaximumFrequency
        works correctly.
        """
        self.gen.SetResolution(1)
        self.gen.SetMaximumFrequency(20000)
        self.assertEqual(len(self.gen.GetSpectrum()), 20000)    # Checks if the spectrum has the right number of samples

