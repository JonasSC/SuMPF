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
import _common as common

class TestChannelDataProperties(unittest.TestCase):
    """
    A test case for the ChannelDataProperties module.
    """
    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_case(self):
        prp = sumpf.modules.ChannelDataProperties(signal_length=2)
        imp = sumpf.modules.ImpulseGenerator()
        flt = sumpf.modules.FilterGenerator()
        fft = sumpf.modules.FourierTransform()
        ift = sumpf.modules.InverseFourierTransform()
        sumpf.connect(prp.GetSignalLength, imp.SetLength)
        sumpf.connect(prp.GetSamplingRate, imp.SetSamplingRate)
        sumpf.connect(prp.GetSpectrumLength, flt.SetLength)
        sumpf.connect(prp.GetResolution, flt.SetResolution)
        sumpf.connect(imp.GetSignal, fft.SetSignal)
        sumpf.connect(flt.GetSpectrum, ift.SetSpectrum)
        calls = []
        calls.append((str, 3))                      # test initial setup
        calls.append((prp.SetSignalLength, 20))     # test signal length whose half is even
        calls.append((prp.SetSignalLength, 22))     # test signal length whose half is odd
        calls.append((prp.SetSpectrumLength, 16))   # test spectrum length whose half is even
        calls.append((prp.SetSpectrumLength, 18))   # test spectrum length whose half is odd
        calls.append((prp.SetSpectrumLength, 21))   # test odd spectrum length
        calls.append((prp.SetSamplingRate, 42.0))   # test setting the sampling rate
        calls.append((prp.SetResolution, 37.0))     # test setting the resolution
        for c in calls:
            c[0](c[1])
            gen_signal = imp.GetSignal()
            gen_spectrum = flt.GetSpectrum()
            trd_signal = ift.GetSignal()
            trd_spectrum = fft.GetSpectrum()
            self.assertEqual(len(gen_signal), len(trd_signal))                              # The length should be the same due to the connection to a ChannelDataProperties instance
            self.assertEqual(gen_signal.GetSamplingRate(), trd_signal.GetSamplingRate())    # The sampling rate should be the same due to the connection to a ChannelDataProperties instance
            self.assertEqual(len(gen_spectrum), len(trd_spectrum))                          # The length should be the same due to the connection to a ChannelDataProperties instance
            self.assertEqual(gen_spectrum.GetResolution(), trd_spectrum.GetResolution())    # The resolution should be the same due to the connection to a ChannelDataProperties instance
        self.assertRaises(ValueError, prp.SetSignalLength, 21)                              # Odd signal lengths shall be forbidden

    def test_constructor(self):
        """
        Tests all variants of constructor parameters.
        """
        default_signal_length = (sumpf.config.get("default_signal_length") // 2) * 2
        default_samplingrate = sumpf.config.get("default_samplingrate")
        default_resolution = float(sumpf.config.get("default_samplingrate")) / default_signal_length
        default_spectrum_length = default_signal_length // 2 + 1
        # nothing
        prp = sumpf.modules.ChannelDataProperties()
        self.assertEqual(prp.GetSignalLength(), default_signal_length)
        self.assertEqual(prp.GetSamplingRate(), default_samplingrate)
        # signal length
        prp = sumpf.modules.ChannelDataProperties(signal_length=42)
        self.assertEqual(prp.GetSignalLength(), 42)
        self.assertEqual(prp.GetSamplingRate(), default_samplingrate)
        # sampling rate
        prp = sumpf.modules.ChannelDataProperties(samplingrate=27)
        self.assertEqual(prp.GetSignalLength(), default_signal_length)
        self.assertEqual(prp.GetSamplingRate(), 27)
        # spectrum length
        prp = sumpf.modules.ChannelDataProperties(spectrum_length=33)
        self.assertEqual(prp.GetSpectrumLength(), 33)
        self.assertEqual(prp.GetResolution(), default_resolution)
        # resolution
        prp = sumpf.modules.ChannelDataProperties(resolution=12)
        self.assertEqual(prp.GetSpectrumLength(), default_spectrum_length)
        self.assertEqual(prp.GetResolution(), 12)
        # signal length & sampling rate
        prp = sumpf.modules.ChannelDataProperties(signal_length=26, samplingrate=47)
        self.assertEqual(prp.GetSignalLength(), 26)
        self.assertEqual(prp.GetSamplingRate(), 47)
        # signal length & spectrum length
        self.assertRaises(ValueError, sumpf.modules.ChannelDataProperties, **dict(signal_length=12, spectrum_length=13))
        # signal length & resolution
        prp = sumpf.modules.ChannelDataProperties(signal_length=38, resolution=18)
        self.assertEqual(prp.GetSignalLength(), 38)
        self.assertEqual(prp.GetResolution(), 18)
        # sampling rate & spectrum length
        prp = sumpf.modules.ChannelDataProperties(samplingrate=16, spectrum_length=8)
        self.assertEqual(prp.GetSamplingRate(), 16)
        self.assertEqual(prp.GetSpectrumLength(), 8)
        # sampling rate & resolution
        self.assertRaises(ValueError, sumpf.modules.ChannelDataProperties, **dict(samplingrate=14, resolution=3))
        prp = sumpf.modules.ChannelDataProperties(samplingrate=60, resolution=15)
        self.assertEqual(prp.GetSamplingRate(), 60)
        self.assertEqual(prp.GetResolution(), 15)
        # spectrum length & resolution
        prp = sumpf.modules.ChannelDataProperties(spectrum_length=5, resolution=49)
        self.assertEqual(prp.GetSpectrumLength(), 5)
        self.assertEqual(prp.GetResolution(), 49)
        # signal length & sampling rate & spectrum length
        self.assertRaises(ValueError, sumpf.modules.ChannelDataProperties, **dict(signal_length=18, samplingrate=4, spectrum_length=7))
        # signal length & sampling rate & resolution
        self.assertRaises(ValueError, sumpf.modules.ChannelDataProperties, **dict(signal_length=14, samplingrate=38, resolution=23))
        # signal length & spectrum length & resolution
        self.assertRaises(ValueError, sumpf.modules.ChannelDataProperties, **dict(signal_length=30, spectrum_length=77, resolution=95))
        # sampling rate & resolution
        self.assertRaises(ValueError, sumpf.modules.ChannelDataProperties, **dict(samplingrate=33, spectrum_length=46, resolution=43))
        # all
        self.assertRaises(ValueError, sumpf.modules.ChannelDataProperties, **dict(signal_length=90, samplingrate=87, spectrum_length=83, resolution=54))
        prp = sumpf.modules.ChannelDataProperties(signal_length=default_signal_length, samplingrate=default_samplingrate, spectrum_length=default_spectrum_length, resolution=default_resolution)
        self.assertEqual(prp.GetSignalLength(), default_signal_length)
        self.assertEqual(prp.GetSamplingRate(), default_samplingrate)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        prp = sumpf.modules.ChannelDataProperties()
        self.assertEqual(prp.SetSignalLength.GetType(), int)
        self.assertEqual(prp.SetSamplingRate.GetType(), float)
        self.assertEqual(prp.SetSpectrumLength.GetType(), int)
        self.assertEqual(prp.SetResolution.GetType(), float)
        self.assertEqual(prp.GetSignalLength.GetType(), int)
        self.assertEqual(prp.GetSamplingRate.GetType(), float)
        self.assertEqual(prp.GetSpectrumLength.GetType(), int)
        self.assertEqual(prp.GetResolution.GetType(), float)
        common.test_connection_observers(testcase=self,
                                         inputs=[prp.SetSignalLength, prp.SetSpectrumLength],
                                         noinputs=[prp.SetSamplingRate, prp.SetResolution],
                                         output=prp.GetSignalLength)
        common.test_connection_observers(testcase=self,
                                         inputs=[prp.SetSamplingRate, prp.SetSpectrumLength, prp.SetResolution],
                                         noinputs=[prp.SetSignalLength],
                                         output=prp.GetSamplingRate)
        common.test_connection_observers(testcase=self,
                                         inputs=[prp.SetSignalLength, prp.SetSpectrumLength],
                                         noinputs=[prp.SetSamplingRate, prp.SetResolution],
                                         output=prp.GetSpectrumLength)
        common.test_connection_observers(testcase=self,
                                         inputs=[prp.SetSignalLength, prp.SetSamplingRate, prp.SetResolution],
                                         noinputs=[prp.SetSpectrumLength],
                                         output=prp.GetResolution)

