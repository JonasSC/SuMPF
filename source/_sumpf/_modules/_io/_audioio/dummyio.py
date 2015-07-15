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

import sumpf

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy

from .baseio import BaseIO


class DummyIO(BaseIO):
    """
    A class whose instance pretends to manage the playback and recording of audio
    data through the sound card.
    This is a dummy class which does not access any sound hardware.
    There can only be one active instance of this class.
    """
    def __init__(self, playbackchannels=1, recordchannels=1):
        self.__samplingrate = sumpf.config.get("default_samplingrate")
        BaseIO.__init__(self, playbackchannels, recordchannels)
        self.__wait_for_stop_lock = threading.Lock()
        self.__connections = {}
        for i in range(self._recordchannels):
            self.__connections[i] = []

    @sumpf.Output(float)
    def GetSamplingRate(self):
        """
        Returns the sampling rate of the faked audio hardware.
        @retval : the sampling rate in floating point format
        """
        return self.__samplingrate

    @sumpf.Input(float, "GetSamplingRate")
    def SetSamplingRate(self, samplingrate):
        """
        This method can be used to set the sampling rate of a DummyIO instance.
        The real sound card interfaces do not have this method, because they take
        the sampling rate from the sound card.
        @param samplingrate: the float value to which the sampling rate shall be set
        """
        self.__samplingrate = float(samplingrate)

    def Stop(self):
        """
        Stops the recording process.
        This will stop the recording process no matter how the record length is
        set. But it is mandatory to stop the recording process when the record
        length is set to WAIT_FOR_STOP.
        """
        if self.__wait_for_stop_lock.locked():
            self.__wait_for_stop_lock.release()
        BaseIO.Stop(self)

    def _Record(self):
        """
        Pretends to start the playback and recording process.
        """
        # wait while pretending to record audio data
        record_length = self._record_length
        self.__unlocked_by_function = False
        if self._record_length != DummyIO.WAIT_FOR_STOP:
            if record_length == DummyIO.SAME_AS_PLAYBACK:
                record_length = len(self._playback)
            def unlock():
                time.sleep(record_length / self.GetSamplingRate())
                self.__unlocked_by_function = True
                self.Stop()
            unlock_thread = threading.Thread(target=unlock)
            self.__wait_for_stop_lock.acquire()
            unlock_thread.start()
        else:
            self.__wait_for_stop_lock.acquire()
        start = time.time()
        self.__wait_for_stop_lock.acquire()
        stop = time.time()
        self.__wait_for_stop_lock.release()
        if not self.__unlocked_by_function:
            record_length = int(round((stop - start) * self.GetSamplingRate()))
        del self.__unlocked_by_function
        # construct a "recorded" Signal
        channels = []
        labels = []
        for i in range(self._recordchannels):
            if len(self.__connections[i]) == 0 or min(self.__connections[i]) >= len(self._playback.GetChannels()):
                channels.append((0.0,) * record_length)
            elif len(self.__connections[i]) == 1:
                channel = list(self._playback.GetChannels()[self.__connections[i][0]])
                for a in range(len(channel), record_length):
                    channel.append(0.0)
                channel = channel[0:record_length]
                channels.append(tuple(channel))
            else:
                channel = [0.0] * record_length
                for c in self.__connections[i]:
                    if c < len(self._playback.GetChannels()):
                        newchannel = list(self._playback.GetChannels()[self.__connections[i][0]])
                        for a in range(len(newchannel), record_length):
                            newchannel.append(0.0)
                        newchannel = newchannel[0:record_length]
                        channel = list(numpy.add(channel, newchannel))
                channels.append(tuple(channel))
            labels.append("Recorded " + str(i))
        self._record = sumpf.Signal(channels=channels, samplingrate=self.GetSamplingRate(), labels=labels)

    def GetCapturePorts(self):
        """
        Returns a list of capture ports of other programs.
        Use GetInputs to get a list of this instance's capture ports.
        @retval : a list of capture port names as strings
        """
        return []

    def GetPlaybackPorts(self):
        """
        Returns a list of playback ports of other programs.
        Use GetOutputs to get a list of this instance's playback ports.
        @retval : a list of playback port names as strings
        """
        return []

    def GetInputs(self):
        """
        Returns a list of this instance's capture ports.
        Use GetCapturePorts to get a list of capture ports of other programs.
        @retval : a list of capture port names as strings
        """
        return list(range(self._recordchannels))

    def GetOutputs(self):
        """
        Returns a list of this instance's playback ports.
        Use GetPlaybackPorts to get a list of playback ports of other programs.
        @retval : a list of playback port names as strings
        """
        return list(range(self._playbackchannels))

    def Connect(self, playback_port, capture_port):
        """
        Connects the given playback port to the given capture port.
        Use GetCapturePorts or GetInputs to get a list of possible capture ports.
        Use GetPlaybackPorts or GetOutputs to get a list of possible playback ports.
        @param playback_port: a string name of a playback port
        @param capture_port: a string name of a capture port
        """
        if playback_port not in self.__connections[capture_port]:
            self.__connections[capture_port].append(playback_port)
        else:
            raise RuntimeError("The given connection already exists")

    def Disconnect(self, playback_port, capture_port):
        """
        Disconnects the given playback port from the given capture port.
        Use GetCapturePorts or GetInputs to get a list of possible capture ports.
        Use GetPlaybackPorts or GetOutputs to get a list of possible playback ports.
        @param playback_port: a string name of a playback port
        @param capture_port: a string name of a capture port
        """
        self.__connections[capture_port].remove(playback_port)

