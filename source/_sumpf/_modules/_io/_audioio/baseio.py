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
import sumpf


class BaseIO(object):
    """
    Abstract base class for AudioIO classes.
    """
    __instance = None
    SAME_AS_PLAYBACK = -1   # the flag to set the record length to the length of the playback Signal
    WAIT_FOR_STOP = -2      # this flag can be passed as record length, to keep on recording until the recording is stopped with the Stop-method

    def __init__(self, playbackchannels, recordchannels):
        """
        @param playbackchannels: the number of channels for playback
        @param recordchannels: the number of channels for recording
        """
        # allow only one instance
        if BaseIO.__instance is None:
            BaseIO.__instance = self
        else:
            raise RuntimeError("There can be only one active instance of AudioIO")
        # store stuff
        self._playbackchannels = playbackchannels
        self._recordchannels = recordchannels
        self._record_length = BaseIO.SAME_AS_PLAYBACK
        self._playback = sumpf.Signal(samplingrate=self.GetSamplingRate())
        self._record = sumpf.modules.CopySignalChannels(input=sumpf.Signal(samplingrate=self.GetSamplingRate()), channelcount=recordchannels).GetOutput()
        # state variables
        self._recording = False     # this variable shall be polled regularly during the recording process. If it is False, the recording shall be interrupted.
        self.__recording_lock = threading.Lock()

    def __del__(self):
        self.Delete()

    def Delete(self):
        """
        Deletes the stored instance, so a new one can be created.
        """
        sumpf.destroy_connectors(self)
        BaseIO.__instance = None

    @sumpf.Input(int)
    def SetRecordLength(self, length):
        """
        Sets the length in samples how long shall be recorded.
        There are two flags that can be passed as record length:
        SAME_AS_PLAYBACK makes the record length as long as the playback Signal's length.
        WAIT_FOR_STOP keeps the recording process going until the Stop method is called.
        @param length: The length how many samples shall be recorded or one of the flags SAME_AS_PLAYBACK or WAIT_FOR_STOP
        """
        self._record_length = int(length)

    @sumpf.Input(sumpf.Signal)
    def SetPlaybackSignal(self, signal):
        """
        Sets the Signal for playback.
        If the number of channels of the Signal is other than the given number
        of playback channels, the surplus channels will be cropped while the
        missing channels are filled with zeros.
        This method does not start the playback.
        @param signal: the Signal which shall be played back
        """
        if signal.GetSamplingRate() != self.GetSamplingRate():
            raise ValueError("The sampling rate of the given signal is not the same as the sampling rate of the hardware")
        self._playback = signal

    @sumpf.Output(sumpf.Signal, caching=False)
    def GetRecordedSignal(self):
        """
        Returns the recorded Signal
        @retval : the recorded Signal
        """
        return self._record

    def GetSamplingRate(self):
        """
        Virtual method whose overrides shall return the sampling rate of the hardware.
        Make sure to decorate the method with "@sumpf.Output(float)".
        @retval : the sampling rate in floating point format
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    @sumpf.Trigger("GetRecordedSignal")
    def Start(self):
        """
        Starts the playback and recording process.
        """
#       if not self.__recording_lock.locked():  # somehow this does not pass the unit test
        if not self._recording:
            self.__recording_lock.acquire()
            self._recording = True
            self._Record()
            self._recording = False
            self.__recording_lock.release()
        else:
            raise RuntimeError("The playback and/or recording has already been started")

    def Stop(self):
        """
        Stops the recording process.
        This will stop the recording process no matter how the record length is
        set. But it is mandatory to stop the recording process when the record
        length is set to WAIT_FOR_STOP.
        """
        self._recording = False
        self.__recording_lock.acquire()
        self.__recording_lock.release()

    def _Record(self):
        """
        This virtual method shall be overridden in derived classes. It shall
        implement the playback and recording process.
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def GetCapturePorts(self):
        """
        Returns a list of capture ports of other programs.
        Use GetInputs to get a list of this instance's capture ports.
        @retval : a list of capture port names as strings
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def GetPlaybackPorts(self):
        """
        Returns a list of playback ports of other programs.
        Use GetOutputs to get a list of this instance's playback ports.
        @retval : a list of playback port names as strings
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def GetInputs(self):
        """
        Returns a list of this instance's capture ports.
        Use GetCapturePorts to get a list of capture ports of other programs.
        @retval : a list of capture port names as strings
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def GetOutputs(self):
        """
        Returns a list of this instance's playback ports.
        Use GetPlaybackPorts to get a list of playback ports of other programs.
        @retval : a list of playback port names as strings
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def Connect(self, playback_port, capture_port):
        """
        Connects the given playback port to the given capture port.
        Use GetCapturePorts or GetInputs to get a list of possible capture ports.
        Use GetPlaybackPorts or GetOutputs to get a list of possible playback ports.
        @param playback_port: a string name of a playback port
        @param capture_port: a string name of a capture port
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def Disconnect(self, playback_port, capture_port):
        """
        Disconnects the given playback port from the given capture port.
        Use GetCapturePorts or GetInputs to get a list of possible capture ports.
        Use GetPlaybackPorts or GetOutputs to get a list of possible playback ports.
        @param playback_port: a string name of a playback port
        @param capture_port: a string name of a capture port
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

