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

"""Contains the ConcatenateSignals class"""

import connectors
import numpy
import sumpf
import sumpf._internal as sumpf_internal

__all__ = ("ConcatenateSignals",)


class ConcatenateSignals:
    """Concatenates multiple signals to one signal.
    The resulting signal will have the sampling rate of the first signal and the
    maximum number of channels of all signals. Missing channels of signals with
    fewer channels will be filled with zeros.
    A negative offset of a signal makes it overlap with the previous signal(s).
    In this case, the overlapping samples will be added. Positive offsets lead
    to a gap between two subsequent signals, which will be filled with zeros.

    The methods of this class are enhanced with the functionality of the *Connectors*
    package, so that instances of this class can be connected in a processing network.
    """

    def __init__(self, signals=()):
        """
        :param signals: a sequence of Signal instances
        """
        self.__signals = connectors.MultiInputData()
        for s in signals:
            self.__signals.add(s)

    @connectors.Output()
    def output(self):
        """Computes the concatenated signal and returns it

        :returns: a Signal instance
        """
        if len(self.__signals) == 0:            # pylint: disable=len-as-condition
            return sumpf.Signal()
        elif len(self.__signals) == 1:
            for s in self.__signals.values():
                return s
        else:
            # find the start and stop samples of the signals
            index = 0
            indices = []
            number_of_channels = 0
            for s in self.__signals.values():
                start = index + s.offset()
                index = start + s.length()
                indices.append((start, index, s.channels()))
                number_of_channels = max(number_of_channels, len(s))
            indices.sort(key=lambda t: (t[0], t[1]))
            # allocate an array for the concatenated channels
            offset = min(i[0] for i in indices)
            length = max(i[1] for i in indices) - offset
            channels = sumpf_internal.allocate_array(shape=(number_of_channels, length), dtype=numpy.float64)
            # copy the first signal
            start, stop, signal_channels = indices[0]
            start -= offset
            stop -= offset
            channels[0:len(signal_channels), start:stop] = signal_channels
            if len(signal_channels) < number_of_channels:
                channels[len(signal_channels):, start:stop] = 0.0
            # copy the other signals
            last_index = 0  # the maximum sample index, at which there is already data in the channels array
            for index, previous in zip(indices[1:], indices[0:-1]):
                start, stop, signal_channels = index
                start -= offset
                stop -= offset
                last_index = max(last_index, previous[1] - offset)
                if start < last_index:  # the current signal overlaps with the previous one, add the signals in the overlapping region
                    if last_index >= stop:
                        stop = start + len(signal_channels[0])
                        channels[0:len(signal_channels), start:stop] += signal_channels[:, 0:]
                        continue
                    else:
                        channels[0:len(signal_channels), start:last_index] += signal_channels[:, 0:last_index - start]
                        signal_channels = signal_channels[:, last_index - start:]
                        start = last_index
                elif start > last_index:    # a gap between the current signal and the previous one, fill it with zeros
                    channels[:, last_index:start] = 0.0
                channels[0:len(signal_channels), start:stop] = signal_channels
                if len(signal_channels) < number_of_channels:   # if the current signal has less channels than the other, fill the missing channels with zeros
                    channels[len(signal_channels):, start:stop] = 0.0
            # create and return the result
            return sumpf.Signal(channels=channels,
                                sampling_rate=next(iter(self.__signals.values())).sampling_rate(),
                                offset=offset,
                                labels=tuple("Concatenation {}".format(i) for i in range(1, number_of_channels + 1)))

    @connectors.MultiInput("output")
    def add(self, signal):
        """Adds a signal to the end of the sequence of signals, which shall be
        concatenated. This method returns an ID, which can be passed to the
        :meth:`remove` and :meth:`replace` methods in order to remove or replace
        this signal.

        :param signal: a signal instance
        :returns: a unique identifier
        """
        return self.__signals.add(signal)

    @add.remove
    def remove(self, signal_id):
        """Removes a signal, that is specified by the given ID, from the sequence
        of signals, which shall be concatenated.

        :param signal_id: the unique identifier, under which the referred signal is stored
        """
        del self.__signals[signal_id]

    @add.replace
    def replace(self, signal_id, signal):
        """Replaces a signal, that is specified by the given ID, with another one.

        :param signal_id: the unique identifier, under which the referred signal is stored
        :param signal: the new Signal instance
        """
        self.__signals[signal_id] = signal
