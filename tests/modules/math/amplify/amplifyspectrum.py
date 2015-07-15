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
from .connectiontester import ConnectionTester


class TestAmplifySpectrum(unittest.TestCase):
    """
    A TestCase for the AmplifySpectrum module.
    """
    def test_get_set(self):
        """
        Tests if the getter and setter methods work as expected.
        """
        spectrum = sumpf.Spectrum(channels=((1.0, 2.0, 3.0),), resolution=17.0, labels=("label",))
        amp = sumpf.modules.AmplifySpectrum()
        self.assertIsNone(amp._input)                               # the object initialized without arguments should be empty
        amp.SetInput(spectrum)
        amp.SetAmplificationFactor(1.5)
        output = amp.GetOutput()
        self.assertEqual(output.GetResolution(), 17.0)              # the resolution should have been taken from input Spectrums
        self.assertEqual(output.GetChannels(), ((1.5, 3.0, 4.5),))  # the amplification should have worked as expected
        self.assertEqual(output.GetLabels(), ("label",))            # the amplified Spectrum should have the same label as the input Spectrum

    def test_constructor(self):
        """
        Tests if setting the data via the constructor works.
        """
        spectrum = sumpf.Spectrum(channels=((1.0, 2.0, 3.0),), resolution=9.0)
        amp = sumpf.modules.AmplifySpectrum(spectrum)
        amp.SetAmplificationFactor(2.5)
        output = amp.GetOutput()
        self.assertEqual(output.GetResolution(), 9.0)
        self.assertEqual(output.GetChannels(), ((2.5, 5.0, 7.5),))

    def test_phase(self):
        """
        Tests if the phase is not altered by the amplification.
        """
        spectrum = sumpf.Spectrum(channels=((1.0 + 1.0j, 2.0 + 1.2j, 3.0 + 1.5j),), resolution=17.0, labels=("label",))
        amp = sumpf.modules.AmplifySpectrum()
        amp.SetInput(spectrum)
        amp.SetAmplificationFactor(4.3)
        output = amp.GetOutput()
        self.assertEqual(output.GetPhase(), spectrum.GetPhase())    # the phase must not be changed by the amplification

    def test_connections(self):
        """
        tests if calculating the amplified Spectrum through connections is possible.
        """
        con = ConnectionTester()
        amp = sumpf.modules.AmplifySpectrum()
        sumpf.connect(amp.GetOutput, con.Trigger)
        sumpf.connect(con.GetSpectrum, amp.SetInput)
        self.assertTrue(con.triggered)  # setting the input should have triggered the trigger
        con.triggered = False
        sumpf.connect(con.GetScalarFactor, amp.SetAmplificationFactor)
        self.assertTrue(con.triggered)  # setting the amplification should have triggered the trigger
        output = amp.GetOutput()
        self.assertEqual(output.GetResolution(), 42.0)
        self.assertEqual(output.GetChannels(), ((2.0, 4.0, 6.0),))

    def test_vectorial_factor(self):
        """
        tests if a vectorial amplification factor works as expected.
        """
        con = ConnectionTester()
        amp = sumpf.modules.AmplifySpectrum()
        channels = len(con.GetVectorialFactor())
        cpy = sumpf.modules.CopySpectrumChannels(channelcount=channels)
        sumpf.connect(con.GetSpectrum, cpy.SetInput)
        sumpf.connect(cpy.GetOutput, amp.SetInput)
        sumpf.connect(con.GetVectorialFactor, amp.SetAmplificationFactor)
        self.assertEqual(amp.GetOutput().GetChannels(), ((1.0, 2.0, 3.0), (2.0, 4.0, 6.0), (3.0, 6.0, 9.0)))
        cpy.SetChannelCount(channels - 1)
        self.assertEqual(amp.GetOutput().GetChannels(), ((1.0, 2.0, 3.0), (2.0, 4.0, 6.0)))
        cpy.SetChannelCount(channels + 1)
        self.assertEqual(amp.GetOutput().GetChannels(), ((1.0, 2.0, 3.0), (1.0, 2.0, 3.0), (1.0, 2.0, 3.0), (1.0, 2.0, 3.0)))

