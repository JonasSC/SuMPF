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

import subprocess

import jack
import numpy

import sumpf

from .baseio import BaseIO


class JackIO(BaseIO):
    """
    A class whose instance manages the playback and recording of audio data through
    the sound card.
    It uses JACK for audio input/output.
    There can only be one active instance of this class.
    """
    def __init__(self, playbackchannels=1, recordchannels=1):
        """
        @param playbackchannels: the number of channels for playback (can not be changed later)
        @param recordchannels: the number of channels for recording (can not be changed later)
        """
        self.__deleted = True
        # set up jack
        self.__prefix = "SuMPF"
        self.__inputs = []
        self.__outputs = []
        jack.attach(self.__prefix)
        self.__deleted = False
        for i in range(recordchannels):
            portname = "in_" + str(i + 1)
            self.__inputs.append(self.__prefix + ":" + portname)
            jack.register_port(portname, jack.IsInput)
        for i in range(playbackchannels):
            portname = "out_" + str(i + 1)
            self.__outputs.append(self.__prefix + ":" + portname)
            jack.register_port(portname, jack.IsOutput)
        jack.activate()
        # other stuff
        BaseIO.__init__(self, playbackchannels, recordchannels)
#       self.__periods = self.__GetNumberOfPeriods()
        self.__periods = 2
        self.__buffer_size = 0 # This will be set when the interaction with the sound card starts

    def Delete(self):
        """
        Shuts down the jack connection and prepares the instance for garbage collection.
        """
        if not self.__deleted:
            jack.deactivate()
            jack.detach()
            sumpf.destroy_connectors(self)
            BaseIO.Delete(self)
            self.__deleted = True

    @sumpf.Output(float)
    def GetSamplingRate(self):
        """
        Returns the sampling rate of the jack server.
        @retval : the sampling rate in floating point format
        """
        return jack.get_sample_rate()

    def _Record(self):
        """
        Starts the playback and recording process.
        """
        self.__buffer_size = jack.get_buffer_size()
        playback = []
        record = []
        record_length = self._record_length
        if record_length == JackIO.SAME_AS_PLAYBACK or record_length == JackIO.WAIT_FOR_STOP:
            record_length = len(self._playback)
        # cut the playback signal in chunks of the size of the buffer and write it into a list of numpy arrays
        b = 0
        while b < record_length:
            playbuffer = numpy.zeros(shape=(self._playbackchannels, self.__buffer_size), dtype=numpy.float32)
            for c in range(self._playbackchannels):
                if c < len(self._playback.GetChannels()):
                    for s in range(self.__buffer_size):
                        if b + s < len(self._playback):
                            playbuffer[c][s] = self._playback.GetChannels()[c][b + s]
            playback.append(playbuffer)
            b += self.__buffer_size
        for i in range(self.__periods):
            playbuffer = numpy.zeros(shape=(self._playbackchannels, self.__buffer_size), dtype=numpy.float32)
            playback.append(playbuffer)
        # play empty buffer to avoid InputSyncErrors
        playbuffer = numpy.zeros(shape=(self._playbackchannels, self.__buffer_size), dtype=numpy.float32)
        self.__PlayAndRecord(playbuffer, "while not recording")
        # play and record with playback signal
        for b in playback:
            if not self._recording:
                break
            recorded = self.__PlayAndRecord(b)
            record.append(recorded)
        # play and record until the Stop method is called
        if self._record_length == JackIO.WAIT_FOR_STOP:
            while self._recording:
                playbuffer = numpy.zeros(shape=(self._recordchannels, self.__buffer_size), dtype=numpy.float32)
                recorded = self.__PlayAndRecord(playbuffer)
                record.append(recorded)
            record_length = (len(record) - self.__periods) * self.__buffer_size
        # play empty buffer to avoid crackling noises at playback stop
        playbuffer = numpy.zeros(shape=(self._playbackchannels, self.__buffer_size), dtype=numpy.float32)
        self.__PlayAndRecord(playbuffer, "while not recording")
        # create output Signal
        channels = []
        labels = []
        for c in range(self._recordchannels):
            channel = []
            for b in range(self.__periods, len(record)):
                for s in record[b][c]:
                    channel.append(s)
            channels.append(tuple(channel[0:record_length]))
            labels.append("Recorded " + str(c))
        self._record = sumpf.Signal(channels=channels, samplingrate=self.GetSamplingRate(), labels=labels)

    def __PlayAndRecord(self, playbuffer, errormessage=""):
        """
        A wrapper for jack.process.
        @param playbuffer: a numpy array with samples that shall be played
        @param errormessage: an optional message that will be appended to the standard message, when a jack-Error has occured
        @retval : a buffer with the recorded samples
        """
        recorded = numpy.zeros(shape=(self._recordchannels, self.__buffer_size), dtype=numpy.float32)
        try:
            jack.process(playbuffer, recorded)
        except jack.InputSyncError:
            pass
#           print("InputSyncError %s" % errormessage)
        except jack.OutputSyncError:
            print("OutputSyncError %s" % errormessage)
        return recorded

    def GetCapturePorts(self):
        """
        Returns a list of capture ports of other programs.
        Use GetInputs to get a list of this instance's capture ports.
        @retval : a list of capture port names as strings
        """
        ports = jack.get_ports()
        result = []
        prefix = self.__prefix + ":"
        for p in ports:
            if jack.get_port_flags(p) & jack.IsInput:
                if not p.startswith(prefix):
                    result.append(p)
        return result

    def GetPlaybackPorts(self):
        """
        Returns a list of playback ports of other programs.
        Use GetOutputs to get a list of this instance's playback ports.
        @retval : a list of playback port names as strings
        """
        ports = jack.get_ports()
        result = []
        prefix = self.__prefix + ":"
        for p in ports:
            if jack.get_port_flags(p) & jack.IsOutput:
                if not p.startswith(prefix):
                    result.append(p)
        return result

    def GetInputs(self):
        """
        Returns a list of this instance's capture ports.
        Use GetCapturePorts to get a list of capture ports of other programs.
        @retval : a list of capture port names as strings
        """
        return self.__inputs

    def GetOutputs(self):
        """
        Returns a list of this instance's playback ports.
        Use GetPlaybackPorts to get a list of playback ports of other programs.
        @retval : a list of playback port names as strings
        """
        return self.__outputs

    def Connect(self, playback_port, capture_port):
        """
        Connects the given playback port to the given capture port.
        Use GetCapturePorts or GetInputs to get a list of possible capture ports.
        Use GetPlaybackPorts or GetOutputs to get a list of possible playback ports.
        @param playback_port: a string name of a playback port
        @param capture_port: a string name of a capture port
        """
        jack.connect(playback_port, capture_port)

    def Disconnect(self, playback_port, capture_port):
        """
        Disconnects the given playback port from the given capture port.
        Use GetCapturePorts or GetInputs to get a list of possible capture ports.
        Use GetPlaybackPorts or GetOutputs to get a list of possible playback ports.
        @param playback_port: a string name of a playback port
        @param capture_port: a string name of a capture port
        """
        jack.disconnect(playback_port, capture_port)

    def __GetNumberOfPeriods(self):
        """
        Querys the number of buffer periods of the jack server.
        Since neither the Jack latency functions nor the querying of the number
        of buffer periods are available in PyJack, this method is a dirty workaround
        to obtain this number.
        @retval : The number of buffer periods of the Jack server
        """
        for p in self.GetCapturePorts():
            if jack.get_port_flags(p) & jack.IsPhysical:
                return int(subprocess.check_output(["jack_lsp", "-l", p]).split("\n")[1].strip().split(" ")[-2]) / jack.get_buffer_size()
        return 2

