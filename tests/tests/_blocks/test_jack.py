# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2019 Jonas Schulte-Coerne
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

    @connectors.Input(laziness=connectors.Laziness.ON_ANNOUNCE)
    def xrun(self, xrun):   # pylint: disable=no-self-use; this is a connector
        """logs the xrun."""
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
    _create_client()     # skip this test if the JACK server is not running
    excitation = sumpf.MergeSignals([sumpf.GaussianNoise(length=2 ** 15).shift(-5),
                                     sumpf.SineWave(length=2 ** 15),
                                     sumpf.HannWindow(length=2 ** 15)]).output()
    assert excitation.offset() % 2 != 0     # check that the offset and length are odd values, that
    assert excitation.length() % 2 != 0     # do not coincide with the blocks of the JACK server
    jack = sumpf.Jack(input_signal=excitation, input_ports=["capture_1", "channel_2", "record_3"])
    jack.xruns.connect(_XRunHandler().xrun)
    jack.connect("Gaussian noise", "SuMPF:capture_1")
    jack.connect(1, "channel_2")
    jack.connect("SuMPF:Hann window", 2)
    jack.start()
    response = jack.output()
    assert response.channels() == pytest.approx(excitation.channels())
    assert response.offset() == excitation.offset()
    assert response.sampling_rate() == jack.sampling_rate()     # pylint: disable=comparison-with-callable; pylint got confused by the connectors.MacroOutput
    assert response.labels() == ("capture_1", "channel_2", "record_3")


def test_output_ports():
    """Tests if the output ports of the :class:`~sumpf.Jack` instances are created
    from the labels of their input signal.
    """
    with _create_client() as client:
        jack = sumpf.Jack("CUT")    # Client Under Test
        jack.xruns.connect(_XRunHandler().xrun)
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


def test_input_ports():
    """Tests if the input ports of the :class:`~sumpf.Jack` instances can be
    created as expected.
    """
    with _create_client() as client:
        jack = sumpf.Jack("c")
        jack.xruns.connect(_XRunHandler().xrun)
        # by default, there should be no input port
        assert [] == [p.name for p in client.get_ports() if p.name.startswith("c:") and p.is_input]     # get_ports(is_output=False) does not seem to filter the output ports
        # check adding a port
        jack.create_input_port("port 1")
        assert ["c:port 1"] == [p.name for p in client.get_ports() if p.name.startswith("c:") and p.is_input]
        # check adding another port and removing the first one by short name
        jack.create_input_port("port:2")
        jack.destroy_input_port("port 1")
        assert ["c:port:2"] == [p.name for p in client.get_ports() if p.name.startswith("c:") and p.is_input]
        # check adding another port and removing the previous one by name
        jack.create_input_port("port+3")
        jack.destroy_input_port("c:port:2")
        assert ["c:port+3"] == [p.name for p in client.get_ports() if p.name.startswith("c:") and p.is_input]
        # check adding another port and removing the previous one by index
        jack.create_input_port("port.4")
        jack.destroy_input_port(0)
        assert ["c:port.4"] == [p.name for p in client.get_ports() if p.name.startswith("c:") and p.is_input]


def test_destruction():
    """Tests if the :class:`~sumpf.Jack` instances are disconnected from the JACK
    server, when they are garbage collected.
    """
    with _create_client() as client:
        # create the SuMPF client and check, that it is connected to the JACL server
        jack = sumpf.Jack("destructible")
        jack.xruns.connect(_XRunHandler().xrun)
        assert ["destructible:output_1"] == [p.name for p in client.get_ports() if p.name.startswith("destructible:")]
        # destroy the SuMPF client and check, that it has been disconnected from the JACK server
        del jack
        assert [] == [p.name for p in client.get_ports() if p.name.startswith("destructible:")]
