# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2017 Jonas Schulte-Coerne
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

class TestAdjustSamplingRate(unittest.TestCase):
    """
    A TestCase for the AdjustSamplingRate class.
    """
    def test_function(self):
        """
        Tests the functionality of the AdjustSamplingRate class.
        """
        self.assertEqual(sumpf.modules.AdjustSamplingRate().GetOutput(), sumpf.Signal())
        self.assertEqual(sumpf.modules.AdjustSamplingRate(samplingrate=1325.2).GetOutput(), sumpf.Signal(samplingrate=1325.2))
        signal1 = sumpf.Signal(channels=((1.0, 2.0), (3.0, 4.0)), samplingrate=12.0, labels=("a", "b"))
        signal2 = sumpf.Signal(channels=((1.0, 2.0), (3.0, 4.0)), samplingrate=13.0, labels=("a", "b"))
        adj = sumpf.modules.AdjustSamplingRate(signal=signal1)
        adj.SetSamplingRate(signal2.GetSamplingRate())
        self.assertEqual(adj.GetOutput(), signal2)
        adj.SetSignal(signal2)
        adj.SetSamplingRate(signal1.GetSamplingRate())
        self.assertEqual(adj.GetOutput(), signal1)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        adj = sumpf.modules.AdjustSamplingRate()
        self.assertEqual(adj.SetSignal.GetType(), sumpf.Signal)
        self.assertEqual(adj.SetSamplingRate.GetType(), float)
        self.assertEqual(adj.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[adj.SetSignal, adj.SetSamplingRate],
                                         noinputs=[],
                                         output=adj.GetOutput)

