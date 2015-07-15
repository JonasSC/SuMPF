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


class Generator(sumpf.internal.SignalGenerator):
    """
    An example class to test the SignalGenerator
    """
    def _GetSample(self, t):
        return 0.1



class SignalReceiver(object):
    """
    An example class that indicates, if it has received a Signal in it's SetSignal method.
    """
    def __init__(self):
        self.__received = False

    @sumpf.Input(sumpf.Signal)
    def SetSignal(self, signal):
        self.__received = True

    def Reset(self):
        self.__received = False

    def HasReceived(self):
        return self.__received



class TestSignalGenerator(unittest.TestCase):
    def setUp(self):
        self.gen = Generator(samplingrate=48000, length=10)

    def test_setter(self):
        """
        Tests if the setter methods raise no errors and notify the GetSignal-connector correctly.
        """
        rec = SignalReceiver()
        sumpf.connect(self.gen.GetSignal, rec.SetSignal)
        self.assertTrue(rec.HasReceived())      # checks the notification on initial connection
        rec.Reset()
        self.gen.SetSamplingRate(44100)
        self.assertTrue(rec.HasReceived())      # checks the notification after SetSamplingRate
        rec.Reset()
        self.gen.SetLength(20)
        self.assertTrue(rec.HasReceived())      # checks the notification after SetLength
        rec.Reset()

