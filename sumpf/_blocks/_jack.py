# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2021 Jonas Schulte-Coerne
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

"""Contains the :class:`~sumpf.Jack` class, that allows playback and recording
of audio through the JACK Audio Connection Kit."""

import dataclasses
import functools
import threading
import time
import weakref
import jack
import numpy
import connectors
import sumpf
import sumpf._internal as sumpf_internal

__all__ = ("Jack",)


class Jack:
    """An interface class for the JACK Audio Connection Kit.

    The intended way to use this class is:

    1. create an instance of the JACK interface.
    2. use the sampling rate from the interface to create a playback signal.
    3. pass the signal to the :meth:`~sumpf.Jack.input` method.
    4. define a couple of capture ports with the :meth:`~sumpf.Jack.add_input_port` method.
    5. connect the instance's ports in JACK with the :meth:`~sumpf.Jack.connect` method.
    6. start the playback and the recording with the :meth:`~sumpf.Jack.start` method.
    7. retrieve the recorded signal through the :meth:`~sumpf.Jack.output` method.

    The playback ports of this class's instances, that can be in connected in JACK,
    are created from the input signal and use their labels as names, if the labels
    are defined. Also, the recording will have the same length as the input signal.

    The :meth:`~sumpf.Jack.sampling_rate`- and :meth:`~sumpf.Jack.xruns`-connectors
    can be used to retrieve the respective parameters and to connect observers,
    that are notified, when the given parameter has changed.

    The internal JACK client can either be activated or deactivated, while being
    activated means, that the client's callback functions are invoked by the JACK
    server. The client also has to be activated for establishing connections in
    JACK. An activated client dramatically increases the risk of xruns in the JACK
    server, because high work loads of the Python instance can delay the execution
    of the clients callback functions. Therefore, it recommended to enable this
    class's ``auto_deactivate`` functionality, which makes sure, that the client
    is only activated, when something is played back and/or recorded through JACK.
    The :meth:`~sumpf.Jack.connect` method stores the connections and only establishes
    them in JACK, after the client has been activated. However, this does not work,
    if the JACK connections shall be managed with external tools like *QJackCtrl*
    or even other instances of this class. For this use case, the ``auto_deactivate``
    functionality can be disabled, which means that the client is always active,
    unless it is deactivated explicitly with the :meth:`~sumpf.Jack.deactivate`
    method.
    """

    def __init__(self, name="SuMPF", input_signal=sumpf.Signal(), input_ports=(), auto_deactivate=True):
        """
        :param name: the name under which this instance is visible in JACK
        :param input_signal: the signal, that will be played back, when the
                             :meth:`~sumpf.Jack.start` method is called.
        :param input_ports: a sequence of string short names for JACK input ports,
                            that shall be created.
        :param auto_deactivate: True, if the internal JACK client shall be deactivated
                                automatically, when it is not in use, False otherwise.
        """
        # store some state variables
        self._input = input_signal
        self._auto_deactivate = auto_deactivate
        self.__connections = []
        self._channels = numpy.empty(shape=(1, 0))
        self._index = 0
        self._event = threading.Event()
        self._event.set()
        # initialize a JACK client
        self._client = jack.Client(name)
        self.__update_output_ports()
        for short_name in input_ports:
            self._client.inports.register(short_name)
        # Passthrough instances for asynchronous events
        self._sampling_rate = connectors.blocks.PassThrough(float(self._client.samplerate))
        self._xruns = connectors.blocks.PassThrough((0, None))
        # set the callbacks and activate the client
        self._client.set_process_callback(functools.partial(on_process, instance=weakref.ref(self)))
        self._client.set_shutdown_callback(functools.partial(on_shutdown, event=self._event))
        self._client.set_samplerate_callback(functools.partial(on_sampling_rate_change, pass_through=self._sampling_rate))  # pylint: disable=line-too-long; all of these lines do a very similar thing. Splitting this line would make it harder to see that
        self._client.set_xrun_callback(functools.partial(on_xrun, instance=weakref.proxy(self)))
        if not self._auto_deactivate:
            self._client.activate()

    def __del__(self):
        """Deactivates the JACK client, when this instance is deleted."""
        self._client.inports.clear()
        self._client.outports.clear()
        self._client.deactivate()
        self._client.close()

    #####################################
    # playback and recording of signals #
    #####################################

    @connectors.Input("output", laziness=connectors.Laziness.ON_ANNOUNCE)
    def start(self, *args, **kwargs):   # noqa; pylint: disable=unused-argument; these ignored arguments are required to be compatible with other input connectors
        """Starts the playback and recording.

        This method is not synchronous. It returns immediately after starting the
        recording and does not wait until it is finished. Use the :meth:`~sumpf.Jack.output`
        method in order to wait for the recording to finish.

        This method is an input connector, so that the playback and recording
        can be triggered by a value change of an output connector. Don't connect
        this connector in the same processing chain as the :meth:`~sumpf.Jack.input`
        connector though, since it is not yet guaranteed, that the :meth:`~sumpf.Jack.input`
        method is called before this one.

        :param `*args,**kwargs`: ignored parameters for compatibility with other input connectors
        :returns: ``self``
        """
        self.activate()
        self._channels = sumpf_internal.allocate_array(shape=(len(self._client.inports), self._input.length()))
        self._index = 0
        self._event.clear()
        return self

    @connectors.Input(laziness=connectors.Laziness.ON_CONNECT)
    def input(self, signal):
        """Sets the input signal, that shall be played back.

        :param signal: a :class:`~sumpf.Signal` instance
        :returns: ``self``
        """
        self._event.wait()  # don't change the signal during a recording
        self._input = signal
        self.__update_output_ports()
        return self

    @connectors.Output()
    def output(self):
        """Returns the recorded signal.
        If the recording is still in progress, this method waits until it is finished.

        :returns: a :class:`~sumpf.Signal` instance
        """
        self._event.wait()
        if self._auto_deactivate:
            time.sleep(1.1 * self._client.blocksize / self._client.samplerate)  # wait for one buffer length to avoid xruns during the last call of the process-callback
        return sumpf.Signal(channels=self._channels,
                            sampling_rate=self._sampling_rate.output(),
                            offset=self._input.offset(),
                            labels=[p.shortname for p in self._client.inports])

    ############################
    # connecting of JACK ports #
    ############################

    def connect(self, output_port, input_port):
        """Connects two ports in JACK.

        Ports of this instance can be specified in multiple ways:

        * by their full name as a string (e.g. ``SuMPF:input_1``)
        * by their short name as a string (e.g. ``input_1``)
        * by their integer channel index
        * as an instance of :class:`jack.OwnPort`

        External ports have to be specified by their full name (e.g. ``system:capture_1``).

        :param output_port: a specifier for the output port, that shall be connected to the given input port
        :param input_port: a specifier for the input_port
        :raises ValueError: if a port specifier cannot be parsed or the port cannot be found
        :returns: ``self``
        """
        try:
            self.__connect(output_port, input_port)
        except jack.JackError:
            self.__connections.append((output_port, input_port))
        return self

    @connectors.Output()
    def input_ports(self):
        """Returns a list of short names of the input ports, that have been registered
        in this instance.

        These short names will be the labels for the output signal's channels.
        Also, these short names can be passed to the :meth:`~sumpf.Jack.connect`
        method as a specifier for the respective input port.

        :returns: a list of strings
        """
        return [p.shortname for p in self._client.inports]

    @connectors.MultiInput("input_ports")
    def add_input_port(self, short_name):
        """Creates an input port, that can receive audio data in JACK.

        Calling this method adds a channel to the recorded output signal with the
        given name as its label.

        :param short_name: the short name of the port, that is used in JACK
        :returns: ``short_name``
        """
        self._client.inports.register(short_name)
        return short_name

    @add_input_port.remove
    def remove_input_port(self, port):
        """Removes an input port. The port will be automatically disconnected in
        JACK, if necessary.

        Calling this method removes a channel from the recorded output signal.

        :param port: a specifier for the port, that shall be destroyed. See the
                     :meth:``~sumpf.Jack.connect`` method for how to specify a port.
        :returns: ``self``
        """
        port = self.__input_port(port)
        # delete the ports from the stored connections dict
        if self.__connections:
            for i, p in enumerate(self._client.inports):
                if p == port:
                    index = i
                    break
            connections = []
            for o, i in self.__connections:
                if isinstance(i, (jack.OwnPort, jack.Port)):     # a workaround, because the __eq__ methods of OwnPort and Port do not check if the other object is of the same class before comparing attributes.
                    if i == port:
                        continue
                elif i in (index, port.shortname, port.name):
                    continue
                if isinstance(i, int):              # indices must be adapted, if previous ports have been deleted
                    connections.append((o, i if i < index else i - 1))
                else:
                    connections.append((o, i))
            self.__connections = connections
        # remove the port
        port.unregister()
        return self

    #########################################
    # Additional data, that comes from JACK #
    #########################################

    @connectors.MacroOutput()
    def sampling_rate(self):
        """Returns the sampling rate of the JACK server.

        :returns: the sampling rate as an integer
        """
        return self._sampling_rate.output

    @connectors.MacroOutput()
    def xruns(self):
        """Returns a tuple ``(NUMBER, XRUN)`` with information about the latest xrun
        in the JACK server.

        * ``NUMBER`` is the integer number of xruns since the instantiation of this instance
        * ``XRUN`` is an object with information about the particular xrun
           * ``XRUN.start`` the start index of the output signal's samples, that
             are corrupted due to this xrun.
           * ``XRUN.stop`` the stop index of the output signal's samples, that
             are corrupted due to this xrun.
           * ``XRUN.delay`` the delay in seconds, that was caused by this xrun
           * ``str(XRUN)`` returns a string, that can be used as error message.

        If there has never been a xrun since the instantiation of this class, the
        returned tuple is ``(0, None)``.

        :returns: a tuple as described above
        """
        return self._xruns.output

    ##################################################
    # activation and deactivation of the JACK client #
    ##################################################

    @connectors.Input(laziness=connectors.Laziness.ON_ANNOUNCE)
    def auto_deactivate(self, auto):
        """Enables or disables the ``auto_deactivate`` functionality.

        If the functionality is being enabled, an active client will be deactivated.
        However, if the functionality is being disabled, a deactivated client will
        not be activated automatically, because it is not known, if the client
        had been deactivated manually, before.

        :param auto_deactivate: True, if the internal JACK client shall be deactivated
                                automatically, when it is not in use, False otherwise.
        :returns: ``self``
        """
        self._auto_deactivate = auto
        if self._auto_deactivate:
            self._event.wait()  # don't deactivate the client during a recording
            self._store_connections()
            self._client.deactivate()
        return self

    @connectors.Input(laziness=connectors.Laziness.ON_ANNOUNCE)
    def activate(self):
        """Activates the internal JACK client manually.

        :returns: ``self``
        """
        self._client.activate()
        for c in self.__connections:
            self.__connect(*c)
        self.__connections.clear()
        return self

    @connectors.Input(laziness=connectors.Laziness.ON_ANNOUNCE)
    def deactivate(self):
        """Deactivates the internal JACK client manually.

        :returns: ``self``
        """
        self._store_connections()
        self._client.deactivate()
        return self

    ##########################
    # private helper methods #
    ##########################

    def __connect(self, output_port, input_port):
        """A helper method, that checks if the given connection already exists and creates it, if not."""
        o = self.__output_port(output_port, own=False)
        i = self.__input_port(input_port, own=False)
        if not isinstance(o, jack.OwnPort) or not o.is_connected_to(i):
            if not isinstance(i, jack.OwnPort) or not i.is_connected_to(o):
                self._client.connect(o, i)

    def _store_connections(self):
        """A helper method, that stores the current JACK connections to this instance's
        client. This method is usually invoked just before deactivating the client,
        so that the connections can be restored after reactivating the client.
        """
        connections = []
        for i, c in enumerate(self._client.outports):
            connections.extend([(i, p) for p in c.connections if not self._client.owns(p)])
        for i, c in enumerate(self._client.inports):
            connections.extend([(p, i) for p in c.connections])
        if connections:     # connections can be empty, if the client is already deactivated, so we don't want to overwrite the stored connections
            self.__connections = connections

    def __update_output_ports(self):
        """A helper method, that generates ports in the JACK server from the input signal's labels."""
        # sanitize the labels from the input signal
        labels = list(self._input.labels()[0:len(self._input)])
        checked_labels = set()
        for i, label in enumerate(labels):
            if not isinstance(label, str) or label == "" or label in checked_labels:
                new_label = f"output_{i+1}"
                while new_label in checked_labels:  # in case an input named output_x already exists
                    new_label += "_"
                labels[i] = new_label
                checked_labels.add(new_label)
            else:
                checked_labels.add(label)
        if len(labels) < len(self._input):
            labels = labels + [f"output_{i}" for i in range(len(labels) + 1, len(self._input) + 1)]
        # create the ports
        if [p.shortname for p in self._client.outports] != labels:
            self._store_connections()
            self._client.outports.clear()
            for label in labels:
                self._client.outports.register(label)
            try:
                for c in self.__connections:
                    self.__connect(*c)
            except jack.JackError:
                pass
            else:
                self.__connections.clear()

    def __input_port(self, port, own=True):
        """A helper method, that finds the input port, that is specified by ``port``.
        See the connect-method for how to specify a port.

        :param port: a specifier for the port
        :param own: if True, only ports of this instance will be scanned
        :raises ValueError: if a port specifier cannot be parsed or the port cannot be found
        :returns: a jack.Port instance
        """
        if isinstance(port, jack.Port):
            return port
        elif isinstance(port, str):
            ports = self._client.inports if own else self._client.get_ports(is_input=True)
            for p in ports:
                if port in (p.shortname, p.name):
                    return p
            raise ValueError(f"unknown port name: {port}")
        elif isinstance(port, int):
            return self._client.inports[port]
        else:
            raise ValueError(f"unknown port identifier: {port}")

    def __output_port(self, port, own=True):
        """A helper method, that finds the output port, that is specified by ``port``.
        See the connect-method for how to specify a port.

        :param port: a specifier for the port
        :param own: if True, only ports of this instance will be scanned
        :raises ValueError: if a port specifier cannot be parsed or the port cannot be found
        :returns: a jack.Port instance
        """
        if isinstance(port, jack.Port):
            return port
        elif isinstance(port, str):
            ports = self._client.outports if own else self._client.get_ports(is_output=True)
            for p in ports:
                if port in (p.shortname, p.name):
                    return p
            raise ValueError(f"unknown port name: {port}")
        elif isinstance(port, int):
            return self._client.outports[port]
        else:
            raise ValueError(f"unknown port identifier: {port}")

###################################################################
# functions for handling JACK events                              #
# they are not methods, so self can be passed as a weak reference #
###################################################################


def on_process(frames, instance):
    """The callback method, that is called, when the JACK server provides and requires new data to process."""
    # pylint: disable=protected-access; this is used like a method
    instance = instance()   # get the weakly referenced object
    if not instance._event.is_set():
        index = instance._index     # make this a local variable, because it is used a lot
        stop_index = index + frames
        channels = instance._input.channels()
        if stop_index <= instance._input.length():
            for port, channel in zip(instance._client.outports, channels):
                port.get_array()[:] = channel[index:stop_index]
            for port, channel in zip(instance._client.inports, instance._channels):
                channel[index:stop_index] = port.get_array()
        elif index < instance._input.length():
            stop_index = instance._input.length() - index
            for port, channel in zip(instance._client.outports, channels):
                port.get_array()[0:stop_index] = channel[index:]
                port.get_array()[stop_index:] = 0.0
            for port, channel in zip(instance._client.inports, instance._channels):
                channel[index:] = port.get_array()[0:stop_index]
        else:
            instance._event.set()
            if instance._auto_deactivate:  # pylint: disable=no-else-raise
                instance._store_connections()
                raise jack.CallbackExit
            else:
                return
        instance._index = stop_index


def on_sampling_rate_change(sampling_rate: int, pass_through):
    """The callback method, that is called, when the JACK server's sampling rate changes."""
    pass_through.input(float(sampling_rate))


def on_shutdown(status: jack.Status, reason: str, event):  # noqa; pylint: disable=unused-argument; these ignored arguments are required to be a compatible callback function
    """The callback method, that is called, when the JACK server is shut down."""
    event.set()


def on_xrun(delay: float, instance):
    """The callback method, that is called, when an xrun occurred in the JACK server."""
    # pylint: disable=protected-access; this is used like a method
    old = instance._xruns.output()
    xrun = XRun(start=instance._index,
                stop=instance._index + instance._client.blocksize,
                delay=delay * 1e6)    # convert the microseconds to seconds
    instance._xruns.input((old[0] + 1, xrun))

##############################
# an additional helper class #
##############################


@dataclasses.dataclass
class XRun:
    """A data class, that contains information about an xrun, that has occurred in the JACK server."""
    start: int
    stop: int
    delay: float

    def __str__(self):
        return f"xrun of {self.delay}s, that corrupted samples {self.start}-{self.stop}"
