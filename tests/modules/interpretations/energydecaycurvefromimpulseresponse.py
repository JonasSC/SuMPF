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


class TestEnergyDecayCurveFromImpulseResponse(unittest.TestCase):
    """
    A TestCase for the EnergyDecayCurveFromImpulseResponse module.
    """
    def test_impulse(self):
        """
        Calculates the edc for an impulse.
        """
        imp = sumpf.modules.ImpulseGenerator(length=100).GetSignal()
        edc = sumpf.modules.EnergyDecayCurveFromImpulseResponse(impulseresponse=imp).GetEnergyDecayCurve()
        self.assertEqual(imp, edc)      # the energy decay curve of an impulse should be an impulse again

    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_windowed_sine(self):
        """
        Emulates an impulse response by fading out a sine wave with a window
        function.
        """
        lng = 100
        # setup a processing chain that generates example data
        sin = sumpf.modules.SineWaveGenerator(length=lng)
        win = sumpf.modules.WindowGenerator(fall_interval=(0, lng // 2), length=lng)
        mul = sumpf.modules.MultiplySignals()
        rms = sumpf.modules.RootMeanSquare(integration_time=sumpf.modules.RootMeanSquare.FULL)
        edc = sumpf.modules.EnergyDecayCurveFromImpulseResponse()
        dif = sumpf.modules.DifferentiateSignal()
        sumpf.connect(sin.GetSignal, mul.SetInput1)
        sumpf.connect(win.GetSignal, mul.SetInput2)
        sumpf.connect(mul.GetOutput, rms.SetInput)
        sumpf.connect(mul.GetOutput, edc.SetImpulseResponse)
        sumpf.connect(edc.GetEnergyDecayCurve, dif.SetInput)
        # get the generated example data
        out = edc.GetEnergyDecayCurve().GetChannels()[0]
        der = dif.GetOutput().GetChannels()[0]
        egy = rms.GetOutput().GetChannels()[0][0] ** 2 * lng
        # do the testing
        self.assertEqual(max(out[lng // 2:]), 0.0)      # all samples after the window should be 0.0
        self.assertLessEqual(max(der), 0.0)             # the energy decay curve has to be falling monotonely
        self.assertAlmostEqual(out[0], egy)             # the first sample of the energy decay curve should be the whole energy of the impulse response

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        edc = sumpf.modules.EnergyDecayCurveFromImpulseResponse()
        self.assertEqual(edc.SetImpulseResponse.GetType(), sumpf.Signal)
        self.assertEqual(edc.GetEnergyDecayCurve.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[edc.SetImpulseResponse],
                                         noinputs=[],
                                         output=edc.GetEnergyDecayCurve)

