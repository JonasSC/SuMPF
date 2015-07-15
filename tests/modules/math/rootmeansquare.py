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
    pass



@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestRootMeanSquare(unittest.TestCase):
    """
    A TestCase for the RootMeanSquare module.
    """
    def test_full_integration(self):
        """
        Tests the integration time flag FULL.
        """
        samplingrate = 100.0
        gen1 = sumpf.modules.SineWaveGenerator(frequency=5, phase=0.3, samplingrate=samplingrate, length=samplingrate)
        gen2 = sumpf.modules.ImpulseGenerator(delay=0.1, samplingrate=samplingrate, length=samplingrate)
        merge = sumpf.modules.MergeSignals()
        sumpf.connect(gen1.GetSignal, merge.AddInput)
        sumpf.connect(gen2.GetSignal, merge.AddInput)
        rms = sumpf.modules.RootMeanSquare(integration_time=sumpf.modules.RootMeanSquare.FULL)
        sumpf.connect(merge.GetOutput, rms.SetInput)
        result = rms.GetOutput()
        self.assertEqual(result.GetSamplingRate(), samplingrate)                        # the sampling rate has to be taken from the input Signal
        self.assertEqual(len(result), samplingrate)                                     # the length has to be the same as the input Signal
        self.assertEqual(result.GetLabels(), merge.GetOutput().GetLabels())             # the labels have to be copied from the input Signal
        self.assertAlmostEqual(result.GetChannels()[0][0], 0.5 ** 0.5)                  # the RMS value has to be calculated correctly
        self.assertEqual(result.GetChannels()[1][0], (1.0 / samplingrate) ** 0.5)       # the RMS value has to be calculated correctly
        self.assertEqual(min(result.GetChannels()[0]), max(result.GetChannels()[0]))    # all samples of a channel have to have the same value
        self.assertEqual(min(result.GetChannels()[1]), max(result.GetChannels()[1]))    # all samples of a channel have to have the same value

    def test_integration_time(self):
        """
        Tests various integration times.
        """
        rms = sumpf.modules.RootMeanSquare()
        self.assertEqual(rms.GetOutput(), sumpf.Signal())                                       # on initialization the input Signal (and therefore the output Signal as well) shall be an empty Signal
        signal = sumpf.Signal(channels=((1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 0.0),), samplingrate=8.0)
        rms = sumpf.modules.RootMeanSquare(signal=signal)
        rms.SetIntegrationTime(0.125)
        output = rms.GetOutput()
        self.assertEqual(output.GetChannels()[0], tuple(numpy.abs(signal.GetChannels()[0])))    #
        rms.SetIntegrationTime(sumpf.modules.RootMeanSquare.FAST)
        self.assertEqual(rms.GetOutput(), output)                                               # sumpf.RootMeanSquare.FAST should be the same as an integration time of 0.125s
        rms.SetIntegrationTime(1)
        output = rms.GetOutput()
        self.assertEqual(output.GetChannels()[0][0], 0.5 ** 0.5)                                #
        self.assertEqual(output.GetChannels()[0][4], 1.0)                                       #
        self.assertEqual(output.GetChannels()[0][-1], 0.5 ** 0.5)                               #
        rms.SetIntegrationTime(sumpf.modules.RootMeanSquare.SLOW)
        self.assertEqual(rms.GetOutput(), output)                                               # sumpf.RootMeanSquare.SLOW should be the same as an integration time of 1.0s
        rms.SetIntegrationTime(5.0)
        self.assertEqual(len(rms.GetOutput()), len(signal))                                     # the length of the output Signal should be the same as the length of the input Signal

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        rms = sumpf.modules.RootMeanSquare()
        self.assertEqual(rms.SetInput.GetType(), sumpf.Signal)
        self.assertEqual(rms.SetIntegrationTime.GetType(), float)
        self.assertEqual(rms.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[rms.SetInput, rms.SetIntegrationTime],
                                         noinputs=[],
                                         output=rms.GetOutput)

