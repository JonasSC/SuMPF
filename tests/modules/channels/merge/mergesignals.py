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


class TestMergeSignals(unittest.TestCase):
    """
    A test case for the MergeSignals module
    """
    def setUp(self):
        self.merger = sumpf.modules.MergeSignals()
        self.signal1 = sumpf.Signal(channels=((11.1, 11.2, 11.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3)), samplingrate=42.0, labels=("1.1", "1.2", "1.3"))
        self.signal2 = sumpf.Signal(channels=((21.1, 21.2, 21.3), (22.1, 22.2, 22.3)), samplingrate=42.0, labels=("2.1", "2.2"))
        self.signal3 = sumpf.Signal(channels=((31.1, 31.2), (32.1, 32.2), (33.1, 33.2)), samplingrate=42.0)
        self.signal4 = sumpf.Signal(channels=((41.1, 41.2, 41.3), (42.1, 42.2, 42.3), (43.1, 43.2, 43.3)), samplingrate=23.0)
        self.signal5 = sumpf.Signal(channels=((51.1, 51.2, 51.3, 51.4), (52.1, 52.2, 52.3, 52.4)), samplingrate=42.0)

    def test_constructor_and_clear(self):
        """
        Tests if adding a list of Signals with the constructor works and if removing them with the Clear method works.
        """
        channels_fsf = ((11.1, 11.2, 11.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3), (21.1, 21.2, 21.3), (22.1, 22.2, 22.3))
        channels_fcf = ((11.1, 11.2, 11.3), (21.1, 21.2, 21.3), (12.1, 12.2, 12.3), (22.1, 22.2, 22.3), (13.1, 13.2, 13.3))
        channels_fsff = ((11.1, 11.2, 11.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3), (21.1, 21.2, 21.3), (22.1, 22.2, 22.3), (31.1, 31.2, 0.0), (32.1, 32.2, 0.0), (33.1, 33.2, 0.0))
        merger = sumpf.modules.MergeSignals(signals=[self.signal1, self.signal2], merge_strategy=sumpf.modules.MergeSignals.FIRST_CHANNEL_FIRST)
        self.assertEqual(merger.GetOutput().GetChannels(), channels_fcf)
        merger.Clear()
        self.assertEqual(merger.GetOutput().GetChannels(), ((0.0, 0.0),))
        quickmerged = sumpf.modules.MergeSignals([self.signal1, self.signal2]).GetOutput()
        self.assertEqual(quickmerged.GetChannels(), channels_fsf)
        self.assertRaises(RuntimeError, sumpf.modules.MergeSignals([self.signal1, self.signal2, self.signal3]).GetOutput)
        self.assertEqual(sumpf.modules.MergeSignals([self.signal1, self.signal2, self.signal3], on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS).GetOutput().GetChannels(), channels_fsff)

    def test_merge(self):
        """
        Tests if the merge works as expected
        """
        self.assertEqual(self.merger.GetOutput().GetChannels(), sumpf.Signal().GetChannels())       # this must not raise an error, instead it should return an empty Signal
        self.merger.SetMergeStrategy(sumpf.modules.MergeSignals.FIRST_SIGNAL_FIRST)
        id1 = self.merger.AddInput(self.signal1)
        self.assertEqual(self.merger.GetOutput().GetSamplingRate(), self.signal1.GetSamplingRate()) # sampling rate should have been taken from the first signal
        self.assertEqual(self.merger.GetOutput().GetChannels(), self.signal1.GetChannels())         # channel data should have been taken from the first signal
        id2 = self.merger.AddInput(self.signal2)
        self.assertEqual(self.merger.GetOutput().GetSamplingRate(), self.signal1.GetSamplingRate()) # sampling rate should not have changed
        channels = ((11.1, 11.2, 11.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3), (21.1, 21.2, 21.3), (22.1, 22.2, 22.3))
        self.assertEqual(self.merger.GetOutput().GetChannels(), channels)                           # channel data should be the channels from the first signal with the second signal's channels appended
        self.assertEqual(self.merger.GetOutput().GetLabels(), ("1.1", "1.2", "1.3", "2.1", "2.2"))  # the labels should have been taken from the input Signals
        self.merger.RemoveInput(id1)
        self.assertEqual(self.merger.GetOutput().GetSamplingRate(), self.signal2.GetSamplingRate()) # sampling rate should not have changed
        self.assertEqual(self.merger.GetOutput().GetChannels(), self.signal2.GetChannels())         # The channel data from the first signal should have been removed
        id1 = self.merger.AddInput(self.signal1)
        self.assertEqual(self.merger.GetOutput().GetSamplingRate(), self.signal1.GetSamplingRate()) # sampling rate should not have changed
        channels = ((21.1, 21.2, 21.3), (22.1, 22.2, 22.3), (11.1, 11.2, 11.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3))
        self.assertEqual(self.merger.GetOutput().GetChannels(), channels)                               # now the second Signal should come before the first Signal
        self.merger.SetMergeStrategy(sumpf.modules.MergeSignals.FIRST_CHANNEL_FIRST)
        self.assertEqual(self.merger.GetOutput().GetSamplingRate(), self.signal1.GetSamplingRate())
        channels = ((21.1, 21.2, 21.3), (11.1, 11.2, 11.3), (22.1, 22.2, 22.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3))
        self.assertEqual(self.merger.GetOutput().GetChannels(), channels)                           # now the order should have been changed according to the other merge strategy
        self.assertEqual(self.merger.GetOutput().GetLabels(), ("2.1", "1.1", "2.2", "1.2", "1.3"))  # the labels should have been taken from the input Signals
        self.merger.RemoveInput(id1)
        self.merger.RemoveInput(id2)
        id4 = self.merger.AddInput(self.signal4)
        self.assertEqual(self.merger.GetOutput().GetSamplingRate(), self.signal4.GetSamplingRate()) # the sampling rate should have been taken from the fourth signal
        self.assertEqual(self.merger.GetNumberOfOutputChannels(), len(self.signal4.GetChannels()))  # the GetNumberOfOutputChannels should also work as expected

    def test_samplingratechanges(self):
        """
        Tests if the errors are raised correctly when multiple input Signals
        change their sampling rate.
        """
        # in this scenario, all input Signals change their sampling rate to the
        # same value, so no error should be raised.
        prp = sumpf.modules.ChannelDataProperties(signal_length=100, samplingrate=42)
        gen1 = sumpf.modules.SilenceGenerator()
        sumpf.connect(prp.GetSignalLength, gen1.SetLength)
        sumpf.connect(prp.GetSamplingRate, gen1.SetSamplingRate)
        gen2 = sumpf.modules.SilenceGenerator()
        sumpf.connect(prp.GetSignalLength, gen2.SetLength)
        sumpf.connect(prp.GetSamplingRate, gen2.SetSamplingRate)
        mrg = sumpf.modules.MergeSignals()
        sumpf.connect(gen1.GetSignal, mrg.AddInput)
        sumpf.connect(gen2.GetSignal, mrg.AddInput)
        amp = sumpf.modules.AmplifySignal()
        sumpf.connect(mrg.GetOutput, amp.SetInput)
        prp.SetSamplingRate(23)     # this command changes the sampling rate
        # in this scenario, all input Signals are changed, but the sampling rate
        # changes to different values, so this should raise an error.
        prp = sumpf.modules.ChannelDataProperties(signal_length=100, samplingrate=42)
        gen1 = sumpf.modules.SilenceGenerator()
        sumpf.connect(prp.GetSignalLength, gen1.SetLength)
        sumpf.connect(prp.GetSamplingRate, gen1.SetSamplingRate)
        gen2 = sumpf.modules.SilenceGenerator()
        sumpf.connect(prp.GetSignalLength, gen2.SetLength)
        gen2.SetSamplingRate(prp.GetSamplingRate())
        sel = sumpf.modules.SelectSignal(selection=1)
        sumpf.connect(gen2.GetSignal, sel.SetInput1)
        sumpf.connect(gen1.GetSignal, sel.SetInput2)
        tst = ConnectionTester()
        sumpf.connect(sel.GetOutput, tst.Trigger)
        mrg = sumpf.modules.MergeSignals()
        sumpf.connect(gen1.GetSignal, mrg.AddInput)
        sumpf.connect(sel.GetOutput, mrg.AddInput)
        amp = sumpf.modules.AmplifySignal()
        sumpf.connect(mrg.GetOutput, amp.SetInput)
        self.assertFalse(tst.triggered)
        self.assertRaises(RuntimeError, prp.SetSamplingRate, 23)    # this command changes the sampling rate
        self.assertTrue(tst.triggered)                          # make sure that all input Signals have changed

    def test_errors(self):
        """
        Tests if errors are raised correctly
        """
        self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSignals.RAISE_ERROR)
        id1 = self.merger.AddInput(self.signal1)
        self.assertRaises(ValueError, self.merger.RemoveInput, id1 + 42)        # this should fail, because the id does not exist
        id2 = self.merger.AddInput(self.signal3)
        self.assertRaises(RuntimeError, self.merger.GetOutput)                  # this should fail, because the channels do not have the same length
        self.merger.RemoveInput(id2)
        id3 = self.merger.AddInput(self.signal3)
        self.assertRaises(RuntimeError, self.merger.GetOutput)                  # this should fail, because the sampling rate is not equal
        self.merger.RemoveInput(id3)
        self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
        self.merger.AddInput(self.signal3)
        self.merger.GetOutput()                                                 # this should not fail
        self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSignals.CROP)
        self.merger.GetOutput()                                                 # this should not fail
        self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSignals.RAISE_ERROR)
        self.assertRaises(RuntimeError, self.merger.GetOutput)                  # this should fail, because the channels do not have the same length

    def test_length_conflict_resolution(self):
        """
        Tests if adding Signals with different lengths works as expected.
        """
        self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
        id1 = self.merger.AddInput(self.signal1)
        id3 = self.merger.AddInput(self.signal3)
        channels = self.merger.GetOutput().GetChannels()
        self.assertEqual(channels[0:3], self.signal1.GetChannels())         # the longer Signal should simply be copied
        self.assertEqual(channels[3][0:2], self.signal3.GetChannels()[0])   # the first elements should be the same as in the shorter Signal
        self.assertEqual(channels[3][2], 0.0)                               # zeros should be added to the shorter Signal
        self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSignals.CROP)
        channels = self.merger.GetOutput().GetChannels()
        self.assertEqual(channels[0], self.signal1.GetChannels()[0][0:2])   # the longer Signal's channels should be cropped during the merge
        self.assertEqual(channels[3:6], self.signal3.GetChannels())         # the shorter Signal should simply be copied
        self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSignals.RAISE_ERROR_EXCEPT_EMPTY)
        self.assertRaises(RuntimeError, self.merger.GetOutput)              # this should fail because channels do not have the same length
        self.merger.RemoveInput(id3)
        ide = self.merger.AddInput(sumpf.Signal())
        channels = self.merger.GetOutput().GetChannels()
        samplingrate = self.merger.GetOutput().GetSamplingRate()
        self.assertEqual(channels[0:3], self.signal1.GetChannels())         # the first Signal should simply be copied
        self.assertEqual(channels[3], (0.0,) * len(self.signal1))           # the empty Signal should be stretched with zeros
        self.assertEqual(samplingrate, self.signal1.GetSamplingRate())      # the sampling rate should have been taken from the non empty Signal
        self.merger.RemoveInput(id1)
        id5 = self.merger.AddInput(self.signal5)
        channels = self.merger.GetOutput().GetChannels()
        samplingrate = self.merger.GetOutput().GetSamplingRate()
        self.assertEqual(channels[0], (0.0,) * len(self.signal5))           # the empty Signal should again be stretched with zeros
        self.assertEqual(channels[1:3], self.signal5.GetChannels())         # the non empty Signal should simply be copied
        self.assertEqual(samplingrate, self.signal1.GetSamplingRate())      # the sampling rate should have been taken from the non empty Signal

    def test_connections(self):
        """
        Tests if the connections work
        """
        tester1 = ConnectionTester()
        tester2 = ConnectionTester()
        sumpf.connect(self.merger.GetOutput, tester1.Trigger)
        sumpf.connect(tester1.GetSignal, self.merger.AddInput)
        self.assertTrue(tester1.triggered)                                                              # connecting to input should work and it should trigger the output
        self.assertEqual(len(self.merger.GetOutput().GetChannels()), 2)                                 # after adding one connection there should be one channel in the output signal
        tester1.SetSamplingRate(44100)
        self.assertEqual(self.merger.GetOutput().GetSamplingRate(), 44100)                              # changing the sampling rate of the only signal in the merger should be possible
        tester1.SetSamplingRate(48000)
        sumpf.connect(tester2.GetSignal, self.merger.AddInput)
        self.assertEqual(len(self.merger.GetOutput().GetChannels()), 4)                                 # after adding a second connection there should be two channels in the output signal
        tester1.ChangeChannels()
        self.assertEqual(self.merger.GetOutput().GetChannels()[0:2], tester1.GetSignal().GetChannels()) # the order of the channels should remain, even if the output of tester1 has changed
        tester1.triggered = False
        sumpf.disconnect(tester1.GetSignal, self.merger.AddInput)
        self.assertTrue(tester1.triggered)                                                              # disconnecting from input should should trigger the output as well
        self.assertEqual(len(self.merger.GetOutput().GetChannels()), 2)                                 # after removing one connection there should be one channel left in the output signal

    def test_synchronous_changes(self):
        """
        Tests what happens, when all input Signals are changed at the same time.
        """
        properties = sumpf.modules.ChannelDataProperties(signal_length=2, samplingrate=13.37)
        sine = sumpf.modules.SineWaveGenerator()
        sumpf.connect(properties.GetSignalLength, sine.SetLength)
        sumpf.connect(properties.GetSamplingRate, sine.SetSamplingRate)
        tri = sumpf.modules.TriangleWaveGenerator()
        sumpf.connect(properties.GetSignalLength, tri.SetLength)
        sumpf.connect(properties.GetSamplingRate, tri.SetSamplingRate)
        merger = sumpf.modules.MergeSignals()
        sumpf.connect(sine.GetSignal, merger.AddInput)
        sumpf.connect(tri.GetSignal, merger.AddInput)
        trigger = ConnectionTester()
        sumpf.connect(merger.GetOutput, trigger.Trigger)
        self.assertFalse(trigger.triggered)
        properties.SetSamplingRate(47.11)       # this should not raise an error
        self.assertTrue(trigger.triggered)
        trigger.triggered = False
        properties.SetSignalLength(4)           # this should not raise an error either
        self.assertTrue(trigger.triggered)

