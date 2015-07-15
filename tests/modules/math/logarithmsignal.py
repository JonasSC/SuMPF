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


class TestLogarithmSignal(unittest.TestCase):
    """
    A test case for the LogarithmSignal module.
    """
    def test_constructor(self):
        """
        Tests if the default setup of the LogarithmSignal class is usable.
        """
        signal1 = sumpf.Signal(channels=((10.0, 100.0),), samplingrate=23.0, labels=("1", None))
        signal2 = sumpf.Signal(channels=((32.0, 128.0),), samplingrate=37.0, labels=("2", None))
        log = sumpf.modules.LogarithmSignal()
        self.assertEqual(log.GetOutput(), sumpf.Signal())
        log.SetInput(signal1)
        self.assertEqual(log.GetOutput().GetChannels()[0], (1.0, 2.0))
        self.assertEqual(log.GetOutput(), sumpf.modules.LogarithmSignal(signal=signal1).GetOutput())
        log.SetInput(signal2)
        log.SetBase(2)
        self.assertEqual(log.GetOutput().GetChannels()[0], (5.0, 7.0))
        self.assertEqual(log.GetOutput(), sumpf.modules.LogarithmSignal(signal=signal2, base=2.0).GetOutput())

    def test_calculation(self):
        """
        Tests if the logarithms are calculated correctly.
        """
        signal = sumpf.Signal(channels=((1.0, 4.0, 5.0), (10.0, 100.0, 512.0)), samplingrate=42.0, labels=(None, "3"))
        log = sumpf.modules.LogarithmSignal(signal=signal)
        for base in [2.0, math.e, 5.0, 10.0]:
            log.SetBase(base)
            output = log.GetOutput()
            for ci in range(len(output.GetChannels())):
                for si in range(len(output)):
                    self.assertEqual(output.GetChannels()[ci][si], math.log(signal.GetChannels()[ci][si], base))

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        log = sumpf.modules.LogarithmSignal()
        self.assertEqual(log.SetInput.GetType(), sumpf.Signal)
        self.assertEqual(log.SetBase.GetType(), float)
        self.assertEqual(log.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[log.SetInput, log.SetBase],
                                         noinputs=[],
                                         output=log.GetOutput)

