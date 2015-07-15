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

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy



class TestNormalizeSignal(unittest.TestCase):
    """
    A TestCase for the NormalizeSignal module.
    """
    def test_general(self):
        """
        Tests for life the universe and everything.
        """
        inputchannels = ((3.0, -4.0, 5.0),
                         (3.0, 4.0, -5.0),
                         (0.25, -0.5, 1.0),
                         (0.25, 0.5, -1.0),
                         (0.3, -0.4, 0.5),
                         (0.3, 0.4, -0.5),
                         (3.0, 4.0, 5.0),
                         (-3.0, -4.0, -5.0),
                         (0.25, 0.5, 1.0),
                         (-0.25, -0.5, -1.0),
                         (0.3, 0.4, 0.5),
                         (-0.3, -0.4, -0.5),
                         (0.0, 0.0, 0.0))
        individuallynormalizedchannels = []
        individualfactors = [0.2, 0.2, 1.0, 1.0, 2.0, 2.0, 0.2, 0.2, 1.0, 1.0, 2.0, 2.0, 1.0]
        for i in range(len(inputchannels)):
            individuallynormalizedchannels.append(tuple(numpy.multiply(inputchannels[i], individualfactors[i])))
        globalynormalizedchannels = tuple(numpy.multiply(inputchannels, 0.2))
        labels = ("The", "first", "six", "channels", "are", "labeled")
        isignal = sumpf.Signal(channels=inputchannels, samplingrate=48000, labels=labels)
        insignal = sumpf.Signal(channels=individuallynormalizedchannels, samplingrate=48000, labels=labels)
        gnsignal = sumpf.Signal(channels=globalynormalizedchannels, samplingrate=48000, labels=labels)
        norm = sumpf.modules.NormalizeSignal()
        self.assertEqual(norm.GetOutput(), sumpf.Signal())  # the default input Signal should be empty
        norm.SetInput(isignal)
        self.assertEqual(norm.GetOutput(), gnsignal)        # by default, the input Signal's channels should not be normalized individually
        norm = sumpf.modules.NormalizeSignal(input=isignal, individual=True)
        self.assertEqual(norm.GetOutput(), insignal)        # as specified in the constructor call, the channels should be normalized individually
        norm.SetIndividual(False)
        self.assertEqual(norm.GetOutput(), gnsignal)        # as specified in the setter method call, the channels should no longer be normalized individually

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        norm = sumpf.modules.NormalizeSignal()
        self.assertEqual(norm.SetInput.GetType(), sumpf.Signal)
        self.assertEqual(norm.SetIndividual.GetType(), bool)
        self.assertEqual(norm.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[norm.SetInput, norm.SetIndividual],
                                         noinputs=[],
                                         output=norm.GetOutput)

