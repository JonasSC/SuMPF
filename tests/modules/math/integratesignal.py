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

class TestIntegrateSignal(unittest.TestCase):
    """
    A test case for the IntegrateSignal module.
    """
    def test_cosine2sine(self):
        """
        Tests, if a cosine can be transformed to a sine wave with the
        IntegrateSignal class.
        """
        frequency = 200.0
        cosine = sumpf.modules.SineWaveGenerator(frequency=frequency, phase=math.pi / 2.0, length=1000).GetSignal()
        integral = sumpf.modules.IntegrateSignal(signal=cosine, offset=sumpf.modules.IntegrateSignal.NO_DC).GetOutput()
        scaled = 2.0 * math.pi * frequency * integral
        sine = sumpf.modules.SineWaveGenerator(frequency=frequency, phase=0.0, length=1000).GetSignal()
        common.compare_signals_almost_equal(testcase=self, signal1=scaled, signal2=sine, places=1)

    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_derivative(self):
        """
        Compares the derivative of the integral with the original Signal.
        """
        noise = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.RedNoise(), length=900, samplingrate=1000.0)
        noise.Seed(13)
        cache = sumpf.modules.AmplifySignal()   # avoid regeneration of the random noise Signal even if caching is turned off
        sumpf.connect(noise.GetSignal, cache.SetInput)
        integral = sumpf.modules.IntegrateSignal()
        sumpf.connect(cache.GetOutput, integral.SetInput)
        derivative = sumpf.modules.DifferentiateSignal()
        sumpf.connect(integral.GetOutput, derivative.SetInput)
        common.compare_signals_almost_equal(testcase=self, signal1=cache.GetOutput(), signal2=derivative.GetOutput(), places=2)
        integral.SetOffset(129.874)
        common.compare_signals_almost_equal(testcase=self, signal1=cache.GetOutput(), signal2=derivative.GetOutput(), places=2)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        # FourierTransform
        ins = sumpf.modules.IntegrateSignal()
        self.assertEqual(ins.SetInput.GetType(), sumpf.Signal)
        self.assertEqual(ins.SetOffset.GetType(), float)
        self.assertEqual(ins.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[ins.SetInput, ins.SetOffset],
                                         noinputs=[],
                                         output=ins.GetOutput)

