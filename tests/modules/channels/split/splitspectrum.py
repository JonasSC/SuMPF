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


class TestSplitSpectrum(unittest.TestCase):
    """
    A test case for the SplitSpectrum module.
    """
    def setUp(self):
        self.splitter = sumpf.modules.SplitSpectrum()
        self.channels = ((1.1, 1.2, 1.3), (2.1, 2.2, 2.3), (3.1, 3.2, 3.3), (4.1, 4.2, 4.3), (5.1, 5.2, 5.3))
        self.long = sumpf.Spectrum(channels=self.channels, resolution=42.0, labels=("1", "2", "3", "4", "5"))
        self.short = sumpf.Spectrum(channels=self.channels[0:3], resolution=42.0)
        self.empty = sumpf.Spectrum()

    def test_constructor(self):
        """
        Tests if setting the data via the constructor is possible.
        """
        spl = sumpf.modules.SplitSpectrum(data=self.long)
        self.assertEqual(spl.GetOutput().GetResolution(), self.long.GetResolution())            # When an input has been set, the sampling rate should have been taken from the input
        self.assertEqual(spl.GetOutput().GetChannels(), self.empty.GetChannels())               # When no channels have been picked, the output's channels should be the same as those of an empty Spectrum
        spl = sumpf.modules.SplitSpectrum(data=self.long, channels=2)
        self.assertEqual(spl.GetOutput().GetChannels(), (self.channels[2],))                    # Selecting the channels via an integer should be possible
        spl = sumpf.modules.SplitSpectrum(data=self.long, channels=[1, 4])
        self.assertEqual(spl.GetOutput().GetChannels(), (self.channels[1], self.channels[4]))   # Selecting the channels via a list should be possible
        spl = sumpf.modules.SplitSpectrum(data=self.long, channels=list(range(5))[2:4])
        self.assertEqual(spl.GetOutput().GetChannels(), self.channels[2:4])                     # Selecting the channels via a range should be possible
        spl = sumpf.modules.SplitSpectrum(data=self.long, channels=sumpf.modules.SplitSpectrum.ALL)
        self.assertEqual(spl.GetOutput().GetChannels(), self.channels)                          # Selecting all channels via a Flag should be possible
        self.assertEqual(spl.GetOutput().GetLabels(), self.long.GetLabels())                    # the output's labels should have been copied from the input

    def test_split(self):
        """
        Tests if the splitting works as expected.
        """
        output = self.splitter.GetOutput()
        self.assertEqual(output.GetResolution(), self.empty.GetResolution())                            # When no input has been set, the output should be an empty Spectrum
        self.assertEqual(output.GetChannels(), self.empty.GetChannels())                                # When no input has been set, the output should be an empty Spectrum
        self.splitter.SetInput(self.long)
        output = self.splitter.GetOutput()
        self.assertEqual(output.GetResolution(), self.long.GetResolution())                             # When an input has been set, the resolution should have been taken from the input
        self.assertEqual(output.GetChannels(), self.empty.GetChannels())                                # When no channels have been picked, the output's channels should be the same as those of an empty Spectrum
        self.splitter.SetOutputChannels(2)
        self.assertEqual(self.splitter.GetOutput().GetChannels(), (self.channels[2],))                  # Selecting the channels via an integer should be possible
        self.splitter.SetInput(self.short)
        self.assertEqual(self.splitter.GetOutput().GetChannels(), (self.channels[2],))                  # The selected channel should be kept through the change of the input Signal, if the new Spectrum has the appropriate number of channels
        self.splitter.SetInput(self.long)
        self.splitter.SetOutputChannels([1, 4])
        self.assertEqual(self.splitter.GetOutput().GetChannels(), (self.channels[1], self.channels[4])) # Selecting the channels via a list should be possible
        self.splitter.SetInput(self.short)
        self.assertEqual(self.splitter.GetOutput().GetChannels(), (self.channels[1],))                  # When the input Spectrum is changed, all available selected channels shall be kept, all others shall be dropped
        self.splitter.SetInput(self.long)
        self.assertEqual(self.splitter.GetOutput().GetChannels(), (self.channels[1],))                  # When the input Spectrum is changed to one with more channels, the previously dropped channels should not come back
        self.splitter.SetOutputChannels(list(range(5))[2:4])
        self.assertEqual(self.splitter.GetOutput().GetChannels(), self.channels[2:4])                   # Selecting the channels via a range should be possible
        self.assertEqual(self.splitter.GetNumberOfOutputChannels(), 2)                                  # Getting the number of output channels shall work as expected
        self.splitter.SetOutputChannels([])
        self.assertEqual(self.splitter.GetOutput().GetChannels(), self.empty.GetChannels())             # Selecting no channels should be possible and lead to an empty Signal
        self.splitter.SetOutputChannels(sumpf.modules.SplitSignal.ALL)
        self.assertEqual(self.splitter.GetOutput().GetChannels(), self.channels)                        # Selecting all channels via a Flag should be possible
        self.splitter.SetInput(self.short)
        self.splitter.SetInput(self.long)
        self.assertEqual(self.splitter.GetOutput().GetChannels(), self.channels)                        # The flag should still be valid, even, when the input has changed

    def test_errors(self):
        """
        Tests if all errors are raised as expected.
        """
        self.splitter.SetOutputChannels([])                                     # selecting no channels of an empty Splitter should not raise an error
        self.splitter.SetInput(self.long)
        self.assertRaises(IndexError, self.splitter.SetOutputChannels, -1)      # selecting a channel with a negative index should raise an error
        self.splitter.SetOutputChannels(5)
        self.assertRaises(IndexError, self.splitter.GetOutput)                  # selecting a channel that is not in the Input should raise an error
        self.splitter.SetOutputChannels(2)
        self.splitter.GetOutput()
        self.splitter.SetOutputChannels([3, 5])
        self.assertRaises(IndexError, self.splitter.GetOutput)                  # selecting a channel through a list that is not in the Input should raise an error

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        self.assertEqual(self.splitter.SetInput.GetType(), sumpf.Spectrum)
        self.assertEqual(self.splitter.SetOutputChannels.GetType(), tuple)
        self.assertEqual(self.splitter.GetOutput.GetType(), sumpf.Spectrum)
        self.assertEqual(self.splitter.GetNumberOfOutputChannels.GetType(), int)
        common.test_connection_observers(testcase=self,
                                         inputs=[self.splitter.SetInput, self.splitter.SetOutputChannels],
                                         noinputs=[],
                                         output=self.splitter.GetOutput)
        common.test_connection_observers(testcase=self,
                                         inputs=[self.splitter.SetInput, self.splitter.SetOutputChannels],
                                         noinputs=[],
                                         output=self.splitter.GetNumberOfOutputChannels)

