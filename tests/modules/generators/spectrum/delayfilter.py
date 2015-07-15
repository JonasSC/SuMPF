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


class TestDelayFilterGenerator(unittest.TestCase):
    """
    A TestCase for the DelayFilterGenerator module.
    """
    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_function(self):
        """
        Tests the generator's output.
        """
        resolution = 1.0
        length = 6
        gen = sumpf.modules.DelayFilterGenerator(delay=0.0, resolution=resolution, length=length)
        ifft = sumpf.modules.InverseFourierTransform()
        sumpf.connect(gen.GetSpectrum, ifft.SetSpectrum)
        for d in range(1, 10):
            delay = d * 0.1
            gen.SetDelay(delay)
            for i in range(length):
                self.assertAlmostEqual(gen.GetSpectrum().GetMagnitude()[0][i], 1.0)
            impulse_response = ifft.GetSignal()
            channel = impulse_response.GetChannels()[0]
            max_index = channel.index(max(channel))
            index = int(round((delay * impulse_response.GetSamplingRate())))
            self.assertEqual(max_index, index)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.DelayFilterGenerator()
        self.assertEqual(gen.SetDelay.GetType(), float)
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetResolution.GetType(), float)
        self.assertEqual(gen.SetMaximumFrequency.GetType(), float)
        self.assertEqual(gen.GetSpectrum.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetDelay, gen.SetLength, gen.SetResolution, gen.SetMaximumFrequency],
                                         noinputs=[],
                                         output=gen.GetSpectrum)

