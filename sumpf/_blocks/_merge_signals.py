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

"""Contains the MergeSignals class"""

import connectors
import numpy
import sumpf
import sumpf._internal as sumpf_internal

__all__ = ("MergeSignals",)


class MergeSignals:
    """Merges multiple signals into one.
    The resulting signal will have the sampling rate of the first signal and the
    minimum offset of all signals. The signals will be aligned according to their
    offsets by filling the channels with zeros.

    The methods of this class are enhanced with the functionality of the *Connectors*
    package, so that instances of this class can be connected in a processing network.
    """
    modes = sumpf_internal.MergeMode

    def __init__(self, signals=(), mode=sumpf_internal.MergeMode.FIRST_DATASET_FIRST):
        """
        :param signals: a sequence of :class:`~sumpf.Signal` instances
        :param mode: a value from the :attr:`~sumpf.MergeSignals.modes` enumeration
        """
        self.__signals = connectors.MultiInputData()
        for s in signals:
            self.__signals.add(s)
        self.__mode = mode

    @connectors.Output()
    def output(self):
        """Computes the merged signal and returns it.

        :returns: a :class:`~sumpf.Signal` instance
        """
        if len(self.__signals) == 0:            # pylint: disable=len-as-condition
            return sumpf.Signal()
        elif len(self.__signals) == 1:
            return next(iter(self.__signals.values()))  # simply return the first and only signal
        else:
            # find the offset, the number of channels and the merged signal's length
            offset = min(s.offset() for s in self.__signals.values())
            number_of_channels = sum(len(s) for s in self.__signals.values())
            length = max(s.offset() + s.length() for s in self.__signals.values()) - offset
            channels = sumpf_internal.allocate_array(shape=(number_of_channels, length), dtype=numpy.float64)
            labels = [""] * number_of_channels
            # fill in the data
            if self.__mode == MergeSignals.modes.FIRST_DATASET_FIRST:
                self.__first_dataset_first(channels, length, offset, labels)
            elif self.__mode == MergeSignals.modes.FIRST_CHANNELS_FIRST:
                self.__first_channels_first(channels, offset, labels)
            else:
                raise ValueError("invalid mode: {}".format(self.__mode))
            # create and return the result
            return sumpf.Signal(channels=channels,
                                sampling_rate=next(iter(self.__signals.values())).sampling_rate(),
                                offset=offset,
                                labels=labels)

    @connectors.MultiInput("output")
    def add(self, signal):
        """Adds a signal to the end of the sequence of signals, which shall be
        merged. This method returns an ID, which can be passed to the :meth:`~sumpf.MergeSignals.remove`
        and :meth:`~sumpf.MergeSignals.replace` methods in order to remove or
        replace this signal.

        :param signal: a :class:`~sumpf.Signal` instance
        :returns: a unique identifier
        """
        return self.__signals.add(signal)

    @add.remove
    def remove(self, signal_id):
        """Removes a signal, that is specified by the given ID, from the sequence
        of signals, which shall be merged.

        :param signal_id: the unique identifier, under which the referred signal is stored
        """
        del self.__signals[signal_id]

    @add.replace
    def replace(self, signal_id, signal):
        """Replaces a signal, that is specified by the given ID, with another one.

        :param signal_id: the unique identifier, under which the referred signal is stored
        :param signal: the new :class:`~sumpf.Signal` instance
        """
        self.__signals[signal_id] = signal

    @connectors.Input("output")
    def set_mode(self, mode):
        """Sets the mode by which the channels of the merged signal are ordered.

        :param mode: a value from the :attr:`~sumpf.MergeSignals.modes` enumeration
        """
        self.__mode = mode

    def __first_dataset_first(self, channels, length, offset, labels):
        """Implementation of the `FIRST_DATASET_FIRST` merging strategy."""
        c = 0
        for signal in self.__signals.values():
            start = signal.offset() - offset
            stop = start + signal.length()
            next_c = c + len(signal)
            channels[c:next_c, start:stop] = signal.channels()
            if start > 0:
                channels[c:next_c, 0:start] = 0.0
            if stop < length:
                channels[c:next_c, stop:] = 0.0
            labels[c:c + len(signal.labels())] = signal.labels()
            c = next_c

    def __first_channels_first(self, channels, offset, labels):
        """Implementation of the `FIRST_CHANNELS_FIRST` merging strategy."""
        number_of_channels, length = channels.shape
        c = 0   # the channel index in the merged signal
        d = 0   # the channel index in the input signals
        while c < number_of_channels:
            for signal in self.__signals.values():
                if d < len(signal):
                    start = signal.offset() - offset
                    stop = start + signal.length()
                    channels[c, start:stop] = signal.channels()[d]
                    if start > 0:
                        channels[c, 0:start] = 0.0
                    if stop < length:
                        channels[c, stop:] = 0.0
                    labels[c] = signal.labels()[d]
                    c += 1
            d += 1
