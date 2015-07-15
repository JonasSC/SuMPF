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
from .connectiontester import ConnectionTester


class TestMergeSpectrums(unittest.TestCase):
    """
    A testcase for the MergeSpectrums module
    """
    def setUp(self):
        self.merger = sumpf.modules.MergeSpectrums()
        self.spectrum1 = sumpf.Spectrum(channels=((11.1, 11.2, 11.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3)), resolution=42.0, labels=("1.1", "1.2", "1.3"))
        self.spectrum2 = sumpf.Spectrum(channels=((21.1, 21.2, 21.3), (22.1, 22.2, 22.3)), resolution=42.0, labels=("2.1", "2.2"))
        self.spectrum3 = sumpf.Spectrum(channels=((31.1, 31.2), (32.1, 32.2), (33.1, 33.2)), resolution=42.0)
        self.spectrum4 = sumpf.Spectrum(channels=((41.1, 41.2, 41.3), (42.1, 42.2, 42.3), (43.1, 43.2, 43.3)), resolution=23.0)
        self.spectrum5 = sumpf.Spectrum(channels=((51.1, 51.2, 51.3, 51.4), (52.1, 52.2, 52.3, 52.4)), resolution=42.0)

    def test_constructor_and_clear(self):
        """
        Tests if adding a list of Spectrums with the constructor works and if removing them with the Clear method works.
        """
        channels_fsf = ((11.1, 11.2, 11.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3), (21.1, 21.2, 21.3), (22.1, 22.2, 22.3))
        channels_fcf = ((11.1, 11.2, 11.3), (21.1, 21.2, 21.3), (12.1, 12.2, 12.3), (22.1, 22.2, 22.3), (13.1, 13.2, 13.3))
        channels_fsff = ((11.1, 11.2, 11.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3), (21.1, 21.2, 21.3), (22.1, 22.2, 22.3), (31.1, 31.2, 0.0), (32.1, 32.2, 0.0), (33.1, 33.2, 0.0))
        merger = sumpf.modules.MergeSpectrums(spectrums=[self.spectrum1, self.spectrum2], merge_strategy=sumpf.modules.MergeSpectrums.FIRST_CHANNEL_FIRST)
        self.assertEqual(merger.GetOutput().GetChannels(), channels_fcf)
        merger.Clear()
        self.assertEqual(merger.GetOutput().GetChannels(), ((0.0, 0.0),))
        quickmerged = sumpf.modules.MergeSpectrums([self.spectrum1, self.spectrum2]).GetOutput()
        self.assertEqual(quickmerged.GetChannels(), channels_fsf)
        self.assertRaises(RuntimeError, sumpf.modules.MergeSpectrums([self.spectrum1, self.spectrum2, self.spectrum3]).GetOutput)
        self.assertEqual(sumpf.modules.MergeSpectrums([self.spectrum1, self.spectrum2, self.spectrum3], on_length_conflict=sumpf.modules.MergeSpectrums.FILL_WITH_ZEROS).GetOutput().GetChannels(), channels_fsff)

    def test_merge(self):
        """
        Tests if the merge works as expected
        """
        self.assertEqual(self.merger.GetOutput().GetChannels(), sumpf.Spectrum().GetChannels())     # this must not raise an error, instead it should return an empty Spectrum
        self.merger.SetMergeStrategy(sumpf.modules.MergeSpectrums.FIRST_SPECTRUM_FIRST)
        id1 = self.merger.AddInput(self.spectrum1)
        self.assertEqual(self.merger.GetOutput().GetResolution(), self.spectrum1.GetResolution())   # the resolution should have been taken from the first spectrum
        self.assertEqual(self.merger.GetOutput().GetChannels(), self.spectrum1.GetChannels())       # channel data should have been taken from the first spectrum
        id2 = self.merger.AddInput(self.spectrum2)
        self.assertEqual(self.merger.GetOutput().GetResolution(), self.spectrum1.GetResolution())   # resolution should not have changed
        channels = ((11.1, 11.2, 11.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3), (21.1, 21.2, 21.3), (22.1, 22.2, 22.3))
        self.assertEqual(self.merger.GetOutput().GetChannels(), channels)                           # the channel data should be the channels from the first spectrum with the second spectrum's channels appended
        self.assertEqual(self.merger.GetOutput().GetLabels(), ("1.1", "1.2", "1.3", "2.1", "2.2"))  # the labels should have been taken from the input Spectrums
        self.merger.RemoveInput(id1)
        self.assertEqual(self.merger.GetOutput().GetResolution(), self.spectrum2.GetResolution())   # the resolution should not have changed
        self.assertEqual(self.merger.GetOutput().GetChannels(), self.spectrum2.GetChannels())       # the channel data from the first spectrum should have been removed
        id1 = self.merger.AddInput(self.spectrum1)
        self.assertEqual(self.merger.GetOutput().GetResolution(), self.spectrum1.GetResolution())   # the resolution should not have changed
        channels = ((21.1, 21.2, 21.3), (22.1, 22.2, 22.3), (11.1, 11.2, 11.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3))
        self.assertEqual(self.merger.GetOutput().GetChannels(), channels)                           # now the second Spectrum should come before the first Spectrum
        self.merger.SetMergeStrategy(sumpf.modules.MergeSpectrums.FIRST_CHANNEL_FIRST)
        self.assertEqual(self.merger.GetOutput().GetResolution(), self.spectrum1.GetResolution())
        channels = ((21.1, 21.2, 21.3), (11.1, 11.2, 11.3), (22.1, 22.2, 22.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3))
        self.assertEqual(self.merger.GetOutput().GetChannels(), channels)                           # now the order should have been changed according to the other merge strategy
        self.assertEqual(self.merger.GetOutput().GetLabels(), ("2.1", "1.1", "2.2", "1.2", "1.3"))  # the labels should have been taken from the input Spectrums
        self.merger.RemoveInput(id1)
        self.merger.RemoveInput(id2)
        id4 = self.merger.AddInput(self.spectrum4)
        self.assertEqual(self.merger.GetOutput().GetResolution(), self.spectrum4.GetResolution())   # the resolution should have been taken from the fourth spectrum
        self.assertEqual(self.merger.GetNumberOfOutputChannels(), len(self.spectrum4.GetChannels()))# the GetNumberOfOutputChannels should also work as expected

    def test_resolutionchanges(self):
        """
        Tests if the errors are raised correctly when multiple input Spectrums
        change their resolution.
        """
        # in this scenario, all input Spectrums change their resolution to the
        # same value, so no error should be raised.
        prp = sumpf.modules.ChannelDataProperties(spectrum_length=100, resolution=42)
        gen1 = sumpf.modules.FilterGenerator()
        sumpf.connect(prp.GetSpectrumLength, gen1.SetLength)
        sumpf.connect(prp.GetResolution, gen1.SetResolution)
        gen2 = sumpf.modules.FilterGenerator()
        sumpf.connect(prp.GetSpectrumLength, gen2.SetLength)
        sumpf.connect(prp.GetResolution, gen2.SetResolution)
        mrg = sumpf.modules.MergeSpectrums()
        sumpf.connect(gen1.GetSpectrum, mrg.AddInput)
        sumpf.connect(gen2.GetSpectrum, mrg.AddInput)
        amp = sumpf.modules.AmplifySpectrum()
        sumpf.connect(mrg.GetOutput, amp.SetInput)
        prp.SetResolution(23)       # this command changes the resolution
        # in this scenario, all input Spectrums are changed, but the resolution
        # changes to different values, so this should raise an error.
        prp = sumpf.modules.ChannelDataProperties(spectrum_length=100, resolution=42)
        gen1 = sumpf.modules.FilterGenerator()
        sumpf.connect(prp.GetSpectrumLength, gen1.SetLength)
        sumpf.connect(prp.GetResolution, gen1.SetResolution)
        gen2 = sumpf.modules.FilterGenerator()
        sumpf.connect(prp.GetSpectrumLength, gen2.SetLength)
        gen2.SetResolution(prp.GetResolution())
        sel = sumpf.modules.SelectSpectrum(selection=1)
        sumpf.connect(gen2.GetSpectrum, sel.SetInput1)
        sumpf.connect(gen1.GetSpectrum, sel.SetInput2)
        tst = ConnectionTester()
        sumpf.connect(sel.GetOutput, tst.Trigger)
        mrg = sumpf.modules.MergeSpectrums()
        sumpf.connect(gen1.GetSpectrum, mrg.AddInput)
        sumpf.connect(sel.GetOutput, mrg.AddInput)
        amp = sumpf.modules.AmplifySpectrum()
        sumpf.connect(mrg.GetOutput, amp.SetInput)
        self.assertFalse(tst.triggered)
        self.assertRaises(RuntimeError, prp.SetResolution, 23)  # this command changes the resolution
        self.assertTrue(tst.triggered)                          # make sure that all input Spectrums have changed

    def test_errors(self):
        """
        Tests if errors are raised correctly
        """
        self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSpectrums.RAISE_ERROR)
        id1 = self.merger.AddInput(self.spectrum1)
        self.assertRaises(ValueError, self.merger.RemoveInput, id1 + 42)                    # this should fail, because the id does not exist
        id2 = self.merger.AddInput(self.spectrum3)
        self.assertRaises(RuntimeError, self.merger.GetOutput)                              # this should fail, because the channels do not have the same length
        self.merger.RemoveInput(id2)
        id3 = self.merger.AddInput(self.spectrum4)
        self.assertRaises(RuntimeError, self.merger.GetOutput)                              # this should fail, because the resolution is not equal
        self.merger.RemoveInput(id3)
        self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSpectrums.FILL_WITH_ZEROS)
        self.merger.AddInput(self.spectrum3)
        self.merger.GetOutput()                                                             # this should not fail
        self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSpectrums.CROP)
        self.merger.GetOutput()                                                             # this should not fail
        self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSpectrums.RAISE_ERROR)
        self.assertRaises(RuntimeError, self.merger.GetOutput)                              # this should fail, because the channels do not have the same length

    def test_length_conflict_resolution(self):
        """
        Tests if adding Spectrums with different lengths works as expected.
        """
        self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSpectrums.FILL_WITH_ZEROS)
        id1 = self.merger.AddInput(self.spectrum1)
        id3 = self.merger.AddInput(self.spectrum3)
        channels = self.merger.GetOutput().GetChannels()
        self.assertEqual(channels[0:3], self.spectrum1.GetChannels())               # the longer Spectrum should simply be copied
        self.assertEqual(channels[3][0:2], self.spectrum3.GetChannels()[0])         # first elements should be the same as in the shorter Spectrum
        self.assertEqual(channels[3][2], 0.0)                                       # zeros should be added to the shorter Spectrum
        self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSpectrums.CROP)
        channels = self.merger.GetOutput().GetChannels()
        self.assertEqual(channels[0], self.spectrum1.GetChannels()[0][0:2])         # the longer Spectrum's channels should be cropped during the merge
        self.assertEqual(channels[3:6], self.spectrum3.GetChannels())                   # the shorter Spectrum should simply be copied
        self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSpectrums.RAISE_ERROR_EXCEPT_EMPTY)
        self.assertRaises(RuntimeError, self.merger.GetOutput)                      # this should fail because channels do not have the same length
        self.merger.RemoveInput(id3)
        ide = self.merger.AddInput(sumpf.Spectrum())
        channels = self.merger.GetOutput().GetChannels()
        resolution = self.merger.GetOutput().GetResolution()
        self.assertEqual(channels[0:3], self.spectrum1.GetChannels())               # the first Spectrum should simply be copied
        self.assertEqual(channels[3], (0.0,) * len(self.spectrum1))                 # the empty Spectrum should be stretched with zeros
        self.assertEqual(resolution, self.spectrum1.GetResolution())                # the resolution should have been taken from the non empty Spectrum
        self.merger.RemoveInput(id1)
        id5 = self.merger.AddInput(self.spectrum5)
        channels = self.merger.GetOutput().GetChannels()
        samplingrate = self.merger.GetOutput().GetResolution()
        self.assertEqual(channels[0], (0.0,) * len(self.spectrum5))                 # the empty Spectrum should again be stretched with zeros
        self.assertEqual(channels[1:3], self.spectrum5.GetChannels())               # the non empty Spectrum should simply be copied
        self.assertEqual(samplingrate, self.spectrum1.GetResolution())              # the resolution should have been taken from the non empty Signal

    def test_connections(self):
        """
        Tests if the connections work
        """
        tester1 = ConnectionTester()
        tester2 = ConnectionTester()
        sumpf.connect(self.merger.GetOutput, tester1.Trigger)
        sumpf.connect(tester1.GetSpectrum, self.merger.AddInput)
        self.assertTrue(tester1.triggered)                                                                  # connecting to input should work and it should trigger the output
        self.assertEqual(len(self.merger.GetOutput().GetChannels()), 2)                                     # after adding one connection there should be the two channels from result of the connected output in the output spectrum
        tester1.SetSamplingRate(22050)
        self.assertEqual(self.merger.GetOutput().GetResolution(), 1.0 / 22050)                              # changing the resolution of the only spectrum in the merger should be possible
        tester1.SetSamplingRate(48000)
        sumpf.connect(tester2.GetSpectrum, self.merger.AddInput)
        self.assertEqual(len(self.merger.GetOutput().GetChannels()), 4)                                     # after adding a second connection there should be four channels in the output spectrum
        tester1.ChangeChannels()
        self.assertEqual(self.merger.GetOutput().GetChannels()[0:2], tester1.GetSpectrum().GetChannels())   # the order of the channels should remain, even if the output of tester1 has changed
        tester1.triggered = False
        sumpf.disconnect(tester1.GetSpectrum, self.merger.AddInput)
        self.assertTrue(tester1.triggered)                                                                  # disconnecting from input should should trigger the output as well
        self.assertEqual(len(self.merger.GetOutput().GetChannels()), 2)                                     # after removing one connection there should be one channel left in the output spectrum

    def test_synchronous_changes(self):
        """
        Tests what happens, when all input Spectrums are changed at the same time.
        """
        properties = sumpf.modules.ChannelDataProperties(spectrum_length=2, resolution=13.37)
        filter1 = sumpf.modules.FilterGenerator()
        sumpf.connect(properties.GetSpectrumLength, filter1.SetLength)
        sumpf.connect(properties.GetResolution, filter1.SetResolution)
        filter2 = sumpf.modules.FilterGenerator()
        sumpf.connect(properties.GetSpectrumLength, filter2.SetLength)
        sumpf.connect(properties.GetResolution, filter2.SetResolution)
        merger = sumpf.modules.MergeSpectrums()
        sumpf.connect(filter1.GetSpectrum, merger.AddInput)
        sumpf.connect(filter2.GetSpectrum, merger.AddInput)
        trigger = ConnectionTester()
        sumpf.connect(merger.GetOutput, trigger.Trigger)
        self.assertFalse(trigger.triggered)
        properties.SetResolution(47.11)         # this should not raise an error
        self.assertTrue(trigger.triggered)
        trigger.triggered = False
        properties.SetSpectrumLength(4)         # this should not raise an error either
        self.assertTrue(trigger.triggered)

