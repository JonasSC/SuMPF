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
import unittest

import sumpf
import _common as common

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy



@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestClipSignal(unittest.TestCase):
    """
    A TestCase for the ClipSignal module.
    """
    def test_clipping(self):
        """
        Tests standard cases for clipping a Signal.
        """
        sine = sumpf.modules.SineWaveGenerator(length=100).GetSignal()
        noise = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.UniformDistribution(), seed=29001, length=100).GetSignal()
        signal = sumpf.modules.MergeSignals(signals=[sine, noise]).GetOutput()
        # test default values
        clipped = sumpf.modules.ClipSignal().GetOutput()
        self.assertEqual(clipped, sumpf.Signal())
        clipped = sumpf.modules.ClipSignal(signal=signal).GetOutput()
        self.assertEqual(clipped, signal)
        # test clipping
        clip = sumpf.modules.ClipSignal()
        clip.SetInput(signal)
        for minimum, maximum in [(-0.5, 0.5), (-0.1, 0.7), (0.2, 0.2)]:
            clip.SetThresholds((minimum, maximum))
            for i, c in enumerate(signal.GetChannels()):
                for j, s in enumerate(c):
                    if s < minimum:
                        self.assertEqual(clip.GetOutput().GetChannels()[i][j], minimum)
                    elif s > maximum:
                        self.assertEqual(clip.GetOutput().GetChannels()[i][j], maximum)
                    else:
                        self.assertEqual(clip.GetOutput().GetChannels()[i][j], s)

    def test_errors(self):
        self.assertRaises(ValueError, sumpf.modules.ClipSignal, thresholds=(1.0, -1.0))
        clip = sumpf.modules.ClipSignal()
        self.assertRaises(ValueError, clip.SetThresholds, (0.2, 0.1))

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        clip = sumpf.modules.ClipSignal()
        self.assertEqual(clip.SetInput.GetType(), sumpf.Signal)
        self.assertEqual(clip.SetThresholds.GetType(), collections.Iterable)
        self.assertEqual(clip.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[clip.SetInput, clip.SetThresholds],
                                         noinputs=[],
                                         output=clip.GetOutput)

