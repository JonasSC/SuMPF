# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2020 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""Contains tests for the interface class for the JACK Audio Connection Kit."""

import os
import logging
import connectors
import numpy
import pytest
import sumpf


def _create_client():
    """A helper function, that checks if the jack client package is available and
    the JACK server is running. If so, it creates a :class:`jack.Client` instance
    and returns it. Otherwise, it skips the test, from which this function was called.
    """
    jack = pytest.importorskip("jack")
    devnull = os.open(os.devnull, os.O_RDWR)    # temporarily reroute stderr to devnull to suppress error messages from the JACK library
    stderr = os.dup(2)
    try:
        os.dup2(devnull, 2)
        client = jack.Client("Testclient", no_start_server=True)

        def process_callback(frames):           # pylint: disable=unused-argument; the argument is necessary for this callback function
            for inport, outport in zip(client.inports, client.outports):
                outport.get_buffer()[:] = inport.get_buffer()

        client.set_process_callback(process_callback)
    except jack.JackError:
        pytest.skip("JACK server is not running")
    else:
        return client
    finally:
        os.dup2(stderr, 2)
        os.close(devnull)


class _XRunHandler:
    """A helper class, that logs an error message, whenever an xrun occurs in
    the JACK server."""

    def __init__(self):
        self.xruns = []

    @connectors.Input(laziness=connectors.Laziness.ON_ANNOUNCE)
    def xrun(self, xrun):
        """logs the xrun."""
        self.xruns.append(xrun)
        logging.error(xrun[1])


def test_availability():
    """Tests, that the :class:`~sumpf.Jack` class is only available, when the
    jack client package is available.
    """
    try:
        import jack     # noqa; pylint: disable=unused-import; this shall raise an ImportError, if the JACK library cannot be imported
    except ImportError:
        assert not hasattr(sumpf, "Jack")
    else:
        assert hasattr(sumpf, "Jack")


def test_playback_and_recording():
    """Tests connecting ports in JACK, playing back and recording a signal."""
    with _create_client():  # skip this test if the JACK server is not running or the JACK client library is not available
        excitation = sumpf.MergeSignals([sumpf.GaussianNoise(length=2 ** 15).shift(-5),
                                         sumpf.SineWave(length=2 ** 15),
                                         sumpf.HannWindow(length=2 ** 15)]).output()
        assert excitation.offset() % 2 != 0     # check that the offset and length are odd values, that
        assert excitation.length() % 2 != 0     # do not coincide with the blocks of the JACK server
        xruns = _XRunHandler()
        jack = sumpf.Jack(input_signal=excitation, input_ports=["capture_1", "channel_2", "record_3"])
        jack.xruns.connect(xruns.xrun)
        jack.connect("Gaussian noise", "SuMPF:capture_1")
        jack.connect(1, "channel_2")
        jack.connect("SuMPF:Hann window", 2)
        jack.start()
        response = jack.output()
        assert response.channels() == pytest.approx(excitation.channels())
        assert response.offset() == excitation.offset()
        assert response.sampling_rate() == jack.sampling_rate()     # pylint: disable=comparison-with-callable; pylint got confused by the connectors.MacroOutput
        assert response.labels() == ("capture_1", "channel_2", "record_3")
        assert xruns.xruns == []


def test_multiple_starts():
    """Tests if the playback and the recording can be started multiple times"""
    with _create_client():  # skip this test if the JACK server is not running or the JACK client library is not available
        excitation = sumpf.SineWave(length=2 ** 15)
        xruns = _XRunHandler()
        jack = sumpf.Jack(input_signal=excitation, input_ports=["capture_1"])
        jack.xruns.connect(xruns.xrun)
        jack.connect(0, 0)
        jack.start()
        response = jack.output()
        assert response.channels() == pytest.approx(excitation.channels())
        jack.add_input_port("capture_2")
        jack.connect(0, 1)
        jack.start()
        response = jack.output()
        assert response[0].channels() == pytest.approx(excitation.channels())
        assert response[1].channels() == pytest.approx(excitation.channels())
        assert xruns.xruns == []


def test_output_ports():
    """Tests if the output ports of the :class:`~sumpf.Jack` instances are created
    from the labels of their input signal.
    """
    with _create_client() as client:
        xruns = _XRunHandler()
        jack = sumpf.Jack("CUT")    # Client Under Test
        jack.xruns.connect(xruns.xrun)
        # check the output port for the empty default input signal
        assert ["CUT:output_1"] == [p.name for p in client.get_ports(is_output=True) if p.name.startswith("CUT:")]
        # check adding and renaming output ports
        jack.input(sumpf.MergeSignals([sumpf.BetaNoise(), sumpf.SquareWave()]).output())
        assert ["CUT:Beta noise", "CUT:Square wave"] == [p.name for p in client.get_ports(is_output=True) if p.name.startswith("CUT:")]             # pylint: disable=line-too-long
        # check removing and renaming output ports
        jack.input(sumpf.ExponentialSweep())
        assert ["CUT:Sweep"] == [p.name for p in client.get_ports(is_output=True) if p.name.startswith("CUT:")]
        # check generating port names from a signal with crooked labels
        jack.input(sumpf.Signal(channels=numpy.eye(3), labels=(None, "output_1")))  # one label None, one label already exists as port name and one label is missing
        assert ["CUT:output_1", "CUT:output_2", "CUT:output_3"] == [p.name for p in client.get_ports(is_output=True) if p.name.startswith("CUT:")]  # pylint: disable=line-too-long
        assert xruns.xruns == []


def test_input_ports():
    """Tests if the input ports of the :class:`~sumpf.Jack` instances can be
    created as expected.
    """
    with _create_client() as client:
        xruns = _XRunHandler()
        jack = sumpf.Jack("c")
        jack.xruns.connect(xruns.xrun)
        # by default, there should be no input port
        assert [] == [p.name for p in client.get_ports() if p.name.startswith("c:") and p.is_input]     # get_ports(is_output=False) does not seem to filter the output ports
        # check adding a port
        jack.add_input_port("port 1")
        assert ["c:port 1"] == [p.name for p in client.get_ports() if p.name.startswith("c:") and p.is_input]
        # check adding another port and removing the first one by short name
        jack.add_input_port("port:2")
        jack.remove_input_port("port 1")
        assert ["c:port:2"] == [p.name for p in client.get_ports() if p.name.startswith("c:") and p.is_input]
        # check adding another port and removing the previous one by name
        jack.add_input_port("port+3")
        jack.remove_input_port("c:port:2")
        assert ["c:port+3"] == [p.name for p in client.get_ports() if p.name.startswith("c:") and p.is_input]
        # check adding another port and removing the previous one by index
        jack.add_input_port("port.4")
        jack.remove_input_port(0)
        assert ["c:port.4"] == [p.name for p in client.get_ports() if p.name.startswith("c:") and p.is_input]
        assert xruns.xruns == []


def test_port_creation_connectors():
    """Tests the connectors to create and destroy connectors."""
    with _create_client():  # skip this test if the JACK server is not running or the JACK client library is not available
        xruns = _XRunHandler()
        jack = sumpf.Jack()
        jack.xruns.connect(xruns.xrun)
        t1 = connectors.blocks.PassThrough().input.connect(jack.input_ports)
        assert t1.output() == []
        t2 = connectors.blocks.PassThrough("x").output.connect(jack.add_input_port)
        assert t1.output() == ["x"]
        t2.input("y")
        assert t1.output() == ["y"]
        t2.output.disconnect(jack.add_input_port)
        assert t1.output() == []


def test_automatic_deactivation():
    """Tests the functionality for activating and deactivating the JACK client automatically."""
    with _create_client() as client:
        import jack
        signal = sumpf.SineWave(length=2 ** 12)
        xruns = _XRunHandler()
        sumpf_jack = sumpf.Jack("auto", input_signal=signal, input_ports=["capture"])     # auto_deactivate should be enabled by default
        sumpf_jack.xruns.connect(xruns.xrun)
        with pytest.raises(jack.JackError):
            client.connect("auto:Sine", "auto:capture")     # this should fail, because the JACK client is deactivated
        sumpf_jack.connect(0, 0)
        with pytest.raises(jack.JackError):
            client.disconnect("auto:Sine", "auto:capture")  # this should fail, because the JACK client is still deactivated
        sumpf_jack.start()
        response = sumpf_jack.output()
        with pytest.raises(jack.JackError):
            client.disconnect("auto:Sine", "auto:capture")  # this should fail, because the JACK client is automatically deactivated after recording
        assert response[0].channels() == pytest.approx(signal.channels())


def test_manual_activation():
    """Tests the methods for activating and deactivating the JACK client manually."""
    with _create_client() as client:
        import jack
        signal = sumpf.SineWave(length=2 ** 12)
        xruns = _XRunHandler()
        sumpf_jack = sumpf.Jack("manual", input_signal=signal, input_ports=["capture"], auto_deactivate=False)
        sumpf_jack.xruns.connect(xruns.xrun)
        client.connect("manual:Sine", "manual:capture")         # the client should be activated by default
        sumpf_jack.deactivate()
        with pytest.raises(jack.JackError):
            client.disconnect("manual:Sine", "manual:capture")  # this should fail, because the JACK client is deactivated
        sumpf_jack.activate()
        client.disconnect("manual:Sine", "manual:capture")      # this should not fail, because the connection should have been restored
        client.connect("manual:Sine", "manual:capture")
        sumpf_jack.start()
        response = sumpf_jack.output()
        assert response[0].channels() == pytest.approx(signal.channels())
        client.disconnect("manual:Sine", "manual:capture")      # this should not fail, because the JACK client should remain active after the recording
        sumpf_jack.deactivate()


def test_ports_and_connections_when_deactivated():
    """tests the creation of connections and ports while the client is deactivated."""
    with _create_client() as client:
        client.inports.register("input")
        client.outports.register("output")
        # test creating and connecting ports, when the client is deactivated
        signal1 = sumpf.MergeSignals([sumpf.SineWave(length=2 ** 12),
                                      sumpf.HannWindow(length=2 ** 12),
                                      sumpf.ExponentialSweep(length=2 ** 12)]).output()
        xruns = _XRunHandler()
        sumpf_jack = sumpf.Jack(name="port_creation", input_signal=signal1)
        sumpf_jack.xruns.connect(xruns.xrun)
        sumpf_jack.add_input_port("index1")
        sumpf_jack.add_input_port("shortname")
        sumpf_jack.add_input_port("name")
        sumpf_jack.add_input_port("index2")
        sumpf_jack.connect(0, 0)
        sumpf_jack.connect("Hann window", "shortname")
        sumpf_jack.connect("port_creation:Sweep", "port_creation:name")
        sumpf_jack.connect(0, "Testclient:input")
        sumpf_jack.connect("Testclient:output", 3)
        sumpf_jack.start()
        reference = sumpf.MergeSignals([signal1,
                                        signal1[0, 0:-client.blocksize].shift(client.blocksize)]).output()
        assert sumpf_jack.output().channels() == pytest.approx(reference.channels())
        # test that the connections remain established, when the output ports change
        signal2 = sumpf.MergeSignals([sumpf.BartlettWindow(length=2 ** 12),
                                      sumpf.ExponentialSweep(length=2 ** 12),
                                      sumpf.SineWave(length=2 ** 12)]).output()
        sumpf_jack.input(signal2)
        sumpf_jack.start()
        reference = sumpf.MergeSignals([signal2,
                                        signal2[0, 0:-client.blocksize].shift(client.blocksize)]).output()
        assert sumpf_jack.output().channels() == pytest.approx(reference.channels())
        # test that the connections are broken, when the input ports are changed
        sumpf_jack.remove_input_port("index1")
        sumpf_jack.remove_input_port("shortname")
        sumpf_jack.remove_input_port("name")
        sumpf_jack.remove_input_port("index2")
        sumpf_jack.add_input_port("a")
        sumpf_jack.add_input_port("b")
        sumpf_jack.add_input_port("c")
        sumpf_jack.add_input_port("d")
        sumpf_jack.start()
        assert (sumpf_jack.output().channels() == numpy.zeros(shape=sumpf_jack.output().shape())).all()


def test_ports_and_connections_when_activated():
    """tests the creation of connections and ports while the client is activated."""
    with _create_client() as client:
        client.inports.register("input")
        client.outports.register("output")
        # test creating and connecting ports, when the client is deactivated
        signal1 = sumpf.MergeSignals([sumpf.SineWave(length=2 ** 12),
                                      sumpf.HannWindow(length=2 ** 12),
                                      sumpf.ExponentialSweep(length=2 ** 12)]).output()
        xruns = _XRunHandler()
        sumpf_jack = sumpf.Jack(name="port_creation", input_signal=signal1, auto_deactivate=False)
        sumpf_jack.xruns.connect(xruns.xrun)
        sumpf_jack.activate()
        sumpf_jack.add_input_port("index1")
        sumpf_jack.add_input_port("shortname")
        sumpf_jack.add_input_port("name")
        sumpf_jack.add_input_port("index2")
        sumpf_jack.connect(0, 0)
        sumpf_jack.connect("Hann window", "shortname")
        sumpf_jack.connect("port_creation:Sweep", "port_creation:name")
        sumpf_jack.connect(0, "Testclient:input")
        sumpf_jack.connect("Testclient:output", 3)
        sumpf_jack.start()
        assert sumpf_jack.output().channels()[0:3] == pytest.approx(signal1.channels())
        # test that the connections remain established, when the output ports change
        signal2 = sumpf.MergeSignals([sumpf.HannWindow(length=2 ** 12),
                                      sumpf.ExponentialSweep(length=2 ** 12),
                                      sumpf.SineWave(length=2 ** 12)]).output()
        sumpf_jack.input(signal2)
        sumpf_jack.start()
        assert sumpf_jack.output().channels()[0:3] == pytest.approx(signal2.channels())
        # test that the connections are broken, when the input ports are changed
        sumpf_jack.remove_input_port("index1")
        sumpf_jack.remove_input_port("shortname")
        sumpf_jack.remove_input_port("name")
        sumpf_jack.remove_input_port("index2")
        sumpf_jack.add_input_port("a")
        sumpf_jack.add_input_port("b")
        sumpf_jack.add_input_port("c")
        sumpf_jack.add_input_port("d")
        sumpf_jack.start()
        assert (sumpf_jack.output().channels()[0:3] == numpy.zeros(shape=sumpf_jack.output()[0:3].shape())).all()
        sumpf_jack.deactivate()


def test_destruction():
    """Tests if the :class:`~sumpf.Jack` instances are disconnected from the JACK
    server, when they are garbage collected.
    """
    with _create_client() as client:
        # create the SuMPF client and check, that it is connected to the JACK server
        xruns = _XRunHandler()
        jack = sumpf.Jack("destructible")
        jack.xruns.connect(xruns.xrun)
        assert ["destructible:output_1"] == [p.name for p in client.get_ports() if p.name.startswith("destructible:")]
        # destroy the SuMPF client and check, that it has been disconnected from the JACK server
        del jack
        assert [] == [p.name for p in client.get_ports() if p.name.startswith("destructible:")]
        assert xruns.xruns == []
