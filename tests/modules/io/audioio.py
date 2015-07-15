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

import threading
import time
import unittest

import sumpf

import _common as common

class TestAudioIO(unittest.TestCase):
    """
    A TestCase for the soundcard interfaces.
    """
    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_channel_order(self):
        """
        Tests if the channels of the recorded Signal are ordered as expected.
        Currently this works only for DummyIO instances, because SuMPF cannot
        determine the latency of a real hardware interface yet.
        """
        # setup sound card interface
#       aio = sumpf.modules.audioio.factory(playbackchannels=3, recordchannels=3)
        aio = sumpf.modules.audioio.DummyIO(playbackchannels=3, recordchannels=3)
        aio.Connect(playback_port=aio.GetOutputs()[2], capture_port=aio.GetInputs()[0])
        aio.Connect(playback_port=aio.GetOutputs()[0], capture_port=aio.GetInputs()[1])
        aio.Connect(playback_port=aio.GetOutputs()[1], capture_port=aio.GetInputs()[2])
        # create some test Signals
        length = 2 ** 14
        gen1 = sumpf.modules.ImpulseGenerator(delay=0.01, frequency=0.0, samplingrate=None, length=length)
        sumpf.connect(aio.GetSamplingRate, gen1.SetSamplingRate)
        gen2 = sumpf.modules.SineWaveGenerator(frequency=2500.0, phase=0.0, samplingrate=None, length=length)
        sumpf.connect(aio.GetSamplingRate, gen2.SetSamplingRate)
        gen3 = sumpf.modules.SquareWaveGenerator(frequency=4400.0, phase=0.0, samplingrate=None, length=length)
        sumpf.connect(aio.GetSamplingRate, gen3.SetSamplingRate)
        pmr = sumpf.modules.MergeSignals()
        sumpf.connect(gen1.GetSignal, pmr.AddInput)
        sumpf.connect(gen2.GetSignal, pmr.AddInput)
        sumpf.connect(gen3.GetSignal, pmr.AddInput)
        # record
        sumpf.connect(pmr.GetOutput, aio.SetPlaybackSignal)
        aio.Start()
        # create reference Signal
        rmr = sumpf.modules.MergeSignals()
        sumpf.connect(gen3.GetSignal, rmr.AddInput)
        sumpf.connect(gen1.GetSignal, rmr.AddInput)
        sumpf.connect(gen2.GetSignal, rmr.AddInput)
        clb = sumpf.modules.CopyLabelsToSignal()
        sumpf.connect(rmr.GetOutput, clb.SetDataInput)
        sumpf.connect(aio.GetRecordedSignal, clb.SetLabelInput)
        # compare
        result = aio.GetRecordedSignal()
        aio.Delete()
        common.compare_signals_almost_equal(testcase=self, signal1=result, signal2=clb.GetOutput())

    @unittest.skipUnless(sumpf.config.get("run_incomplete_tests"), "Incomplete tests are skipped")
    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_recording(self):
        """
        Tests if the recording parameters are accepted.
        """
        aio = sumpf.modules.audioio.factory()
        try:
            self.assertEqual(len(aio.GetOutputs()), 1)  # the number of outputs shall be 1 if no constructor parameter is given
            self.assertEqual(len(aio.GetInputs()), 1)   # the number of inputs shall be 1 if no constructor parameter is given
        finally:
            aio.Delete()
        gen = sumpf.modules.SilenceGenerator(length=2 ** 14 - 5)
        cpy = sumpf.modules.CopySignalChannels(channelcount=1)
        sumpf.connect(gen.GetSignal, cpy.SetInput)
        aio = sumpf.modules.audioio.factory(playbackchannels=2, recordchannels=3)
        try:
            sumpf.connect(aio.GetSamplingRate, gen.SetSamplingRate)
            sumpf.connect(cpy.GetOutput, aio.SetPlaybackSignal)
            self.assertEqual(len(aio.GetOutputs()), 2)
            self.assertEqual(len(aio.GetInputs()), 3)
            aio.Connect(playback_port=aio.GetOutputs()[0], capture_port=aio.GetInputs()[2])
            aio.Start()
            self.assertEqual(len(aio.GetRecordedSignal()), 2 ** 14 - 5)
            self.assertEqual(len(aio.GetRecordedSignal().GetChannels()), 3)
            aio.SetRecordLength(2 ** 12 + 3)
            aio.Connect(playback_port=aio.GetOutputs()[1], capture_port=aio.GetInputs()[0])
            aio.Disconnect(playback_port=aio.GetOutputs()[0], capture_port=aio.GetInputs()[2])
            aio.Start()
            self.assertEqual(len(aio.GetRecordedSignal()), 2 ** 12 + 3)
            cpy.SetChannelCount(4)
            aio.Connect(playback_port=aio.GetOutputs()[0], capture_port=aio.GetInputs()[1])
            aio.Connect(playback_port=aio.GetOutputs()[1], capture_port=aio.GetInputs()[1])
            aio.Start()
            self.assertEqual(len(aio.GetRecordedSignal().GetChannels()), 3)
            aio.Disconnect(playback_port=aio.GetOutputs()[0], capture_port=aio.GetInputs()[1])
            aio.Disconnect(playback_port=aio.GetOutputs()[1], capture_port=aio.GetInputs()[0])
            aio.Disconnect(playback_port=aio.GetOutputs()[1], capture_port=aio.GetInputs()[1])
        finally:
            aio.Delete()

    @unittest.skipUnless(sumpf.config.get("run_incomplete_tests"), "Incomplete tests are skipped")
    def test_wait_for_stop(self):
        """
        Tests if the WAIT_FOR_STOP flag does everything right.
        """
        def test(aio):
            try:
                aio.SetRecordLength(type(aio).WAIT_FOR_STOP)
                def stop():
                    time.sleep(0.5)
                    aio.Stop()
                stop_thread = threading.Thread(target=stop)
                stop_thread.start()
                aio.Start()
                self.assertGreater(len(aio.GetRecordedSignal()), 0.4 * aio.GetSamplingRate())
            finally:
                aio.Delete()
        test(sumpf.modules.audioio.factory(playbackchannels=0, recordchannels=1))
        test(sumpf.modules.audioio.DummyIO(playbackchannels=0, recordchannels=1))

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        def test(aio):
            try:
                self.assertEqual(aio.SetRecordLength.GetType(), int)
                self.assertEqual(aio.SetPlaybackSignal.GetType(), sumpf.Signal)
                self.assertEqual(aio.GetRecordedSignal.GetType(), sumpf.Signal)
                self.assertEqual(aio.GetSamplingRate.GetType(), float)
                common.test_connection_observers(testcase=self,
                                                 inputs=[aio.Start],
                                                 noinputs=[aio.SetRecordLength, aio.SetPlaybackSignal],
                                                 output=aio.GetRecordedSignal)
            finally:
                aio.Delete()
        test(sumpf.modules.audioio.factory())
        test(sumpf.modules.audioio.DummyIO())

    def test_dummy_io_setsamplingrate(self):
        """
        Tests if the SetSamplingRate method of the DummyIO class works as expected.
        """
        dummyio = sumpf.modules.audioio.DummyIO()
        try:
            # test default
            self.assertEqual(dummyio.GetSamplingRate(), sumpf.config.get("default_samplingrate"))
            # test setting the sampling rate
            dummyio.SetSamplingRate(47.11)
            self.assertEqual(dummyio.GetSamplingRate(), 47.11)
            dummyio.SetSamplingRate(42)
            self.assertIsInstance(dummyio.GetSamplingRate(), float)
            self.assertEqual(dummyio.GetSamplingRate(), 42.0)
            # test connectors
            common.test_connection_observers(testcase=self,
                                             inputs=[dummyio.SetSamplingRate],
                                             noinputs=[],
                                             output=dummyio.GetSamplingRate)
            common.test_connection_observers(testcase=self,
                                             inputs=[],
                                             noinputs=[dummyio.SetSamplingRate],
                                             output=dummyio.GetRecordedSignal)
        finally:
            dummyio.Delete()

