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

import collections
import math
import unittest
import sumpf
import _common as common


class TestDifferentiateSignal(unittest.TestCase):
    """
    A test case for the DifferentiateSignal module.
    """
    def test_linear(self):
        """
        Tests the derivative of a linearly raising Signal.
        """
        length = 100
        samples = []
        for i in range(length):
            samples.append(float(i) / float(length))
        signal = sumpf.Signal(channels=(tuple(samples),), samplingrate=length / 2.0)
        drv = sumpf.modules.DifferentiateSignal(signal=signal)
        self.assertAlmostEqual(max(drv.GetOutput().GetChannels()[0]), 0.5)
        self.assertAlmostEqual(min(drv.GetOutput().GetChannels()[0]), 0.5)

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_sine(self):
        """
        Tests the derivative of a sine wave Signal.
        """
        frequency = 1.9
        samplingrate = 48000
        length = 5 * samplingrate
        sin = sumpf.modules.SineWaveGenerator(frequency=frequency,
                                              phase=0.0,
                                              samplingrate=samplingrate,
                                              length=length)
        cos = sumpf.modules.SineWaveGenerator(frequency=frequency,
                                              phase=math.pi / 2.0,
                                              samplingrate=samplingrate,
                                              length=length)
        drv = sumpf.modules.DifferentiateSignal()
        places = 2
        if common.lib_available("numpy"):
            drv.SetFunction(lambda sequence: sumpf.helper.differentiate_spline(sequence=sequence, degree=2))
            places = 6
        self.assertEqual(drv.GetOutput(), sumpf.Signal())
        drv.SetInput(sin.GetSignal())
        common.compare_signals_almost_equal(self, drv.GetOutput(), cos.GetSignal() * (2.0 * math.pi * frequency), places)

    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_function(self):
        """
        Tests if setting the differentiation function works.
        """
        signal = sumpf.Signal(channels=((1.0, 0.0, 1.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0, 0.0)), samplingrate=1.0, labels=("One", "Zero"))
        result1 = sumpf.Signal(channels=((-1.0, 0.0, 0.0, 0.0, 1.0), (1.0, 0.0, 0.0, 0.0, -1.0)), samplingrate=1.0, labels=("One", "Zero"))
        result2 = sumpf.Signal(channels=((-1.0, -1.0, 1.0, -1.0, 1.0), (1.0, 1.0, -1.0, 1.0, -1.0)), samplingrate=1.0, labels=("One", "Zero"))
        drv = sumpf.modules.DifferentiateSignal(signal=signal, function=sumpf.helper.differentiate_spline)
        self.assertEqual(drv.GetOutput(), result1)
        drv.SetFunction(sumpf.helper.differentiate)
        self.assertEqual(drv.GetOutput(), result2)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        drv = sumpf.modules.DifferentiateSignal()
        self.assertEqual(drv.SetInput.GetType(), sumpf.Signal)
        self.assertEqual(drv.SetFunction.GetType(), collections.Callable)
        self.assertEqual(drv.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[drv.SetInput, drv.SetFunction],
                                         noinputs=[],
                                         output=drv.GetOutput)

