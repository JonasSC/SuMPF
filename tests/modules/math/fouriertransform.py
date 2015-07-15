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
import unittest
import sumpf
import _common as common

@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestFourierTransform(unittest.TestCase):
    """
    A test case for the FourierTransform and the InverseFourierTransform module.
    """
    def setUp(self):
        self.frequency = 1000.0
        self.samplingrate = 4800.0
        self.length = self.samplingrate
        self.gen = sumpf.modules.SineWaveGenerator(frequency=self.frequency,
                                                   phase=0.0,
                                                   samplingrate=self.samplingrate,
                                                   length=self.length)
        self.fft = sumpf.modules.FourierTransform()
        sumpf.connect(self.gen.GetSignal, self.fft.SetSignal)

    @unittest.skipUnless(sumpf.config.get("run_incomplete_tests"), "Incomplete tests are skipped")
    def test_phase(self):
        """
        Tests, if the phase is transformed correctly.
        """
        spk = self.fft.GetSpectrum()
        index = int(round(self.frequency / spk.GetResolution()))
        self.assertAlmostEqual(spk.GetPhase()[0][index], 0.0)       # test if spectrum has no phase shift
        self.gen.SetPhase(math.pi)
        spk = self.fft.GetSpectrum()
        self.assertAlmostEqual(spk.GetPhase()[0][index], math.pi)   # test if spectrum has the right phase shift

    def test_compare_with_inversion(self):
        """
        Creates a Signal, transforms it, inverses the transformation and tests, if it resembles the original Signal.
        """
        ifft = sumpf.modules.InverseFourierTransform()
        sumpf.connect(self.fft.GetSpectrum, ifft.SetSpectrum)
        insignal = self.gen.GetSignal()
        outsignal = ifft.GetSignal()
        common.compare_signals_almost_equal(testcase=self, signal1=insignal, signal2=outsignal)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        # FourierTransform
        fft = sumpf.modules.FourierTransform()
        self.assertEqual(fft.SetSignal.GetType(), sumpf.Signal)
        self.assertEqual(fft.GetSpectrum.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[fft.SetSignal],
                                         noinputs=[],
                                         output=fft.GetSpectrum)
        # InverseFourierTransform
        ifft = sumpf.modules.InverseFourierTransform()
        self.assertEqual(ifft.SetSpectrum.GetType(), sumpf.Spectrum)
        self.assertEqual(ifft.GetSignal.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[ifft.SetSpectrum],
                                         noinputs=[],
                                         output=ifft.GetSignal)

