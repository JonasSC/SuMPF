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

"""Contains the :class:`~sumpf.Concatenate` class."""

import connectors
import sumpf
import sumpf._internal as sumpf_internal

__all__ = ("Concatenate",)


class Concatenate:
    """Concatenates multiple signals or spectrograms to one long data set.
    The resulting data set will have the meta data (e.g. sampling rate or frequency
    resolution) of the first added data set and the maximum number of channels of
    all data sets. Missing channels of data sets with fewer channels will be filled
    with zeros.

    A negative offset of a data set makes it overlap with the previous data set(s).
    In this case, the overlapping samples will be added. Positive offsets lead
    to a gap between two subsequent signals, which will be filled with zeros.

    The methods of this class are enhanced with the functionality of the *Connectors*
    package, so that instances of this class can be connected in a processing network.
    """

    def __init__(self, data=()):
        """
        :param data: a sequence of :class:`~sumpf.Signal` or :class:`~sumpf.Spectrogram` instances
        """
        self.__data = connectors.MultiInputData()
        for d in data:
            self.__data.add(d)

    @connectors.Output()
    def output(self):  # noqa: C901; it's either a complex method or a lot of duplicated code
        # pylint: disable=too-many-branches,too-many-statements;
        """Computes the concatenated signal and returns it

        :returns: a Signal instance
        """
        if not self.__data:
            raise RuntimeError("Nothing to concatenate")
        if len(self.__data) == 1:
            return next(iter(self.__data.values()))  # simply return the first and only data set
        else:
            first = next(iter(self.__data.values()))
            # find the start and stop samples of the data sets
            index = 0
            indices = []
            number_of_channels = 0
            for s in self.__data.values():
                start = index + s.offset()
                index = start + s.length()
                indices.append((start, index, s.channels()))
                number_of_channels = max(number_of_channels, len(s))
            indices.sort(key=lambda t: (t[0], t[1]))
            # allocate an array for the concatenated channels and copy the first data set
            offset = min(i[0] for i in indices)
            length = max(i[1] for i in indices) - offset
            start, stop, dataset_channels = indices[0]
            start -= offset
            stop -= offset
            if len(dataset_channels.shape) == 2:
                signal = True
                channels = sumpf_internal.allocate_array(shape=(number_of_channels, length),
                                                         dtype=dataset_channels.dtype)
                channels[0:len(dataset_channels), start:stop] = dataset_channels
                if len(dataset_channels) < number_of_channels:
                    channels[len(dataset_channels):, start:stop] = 0.0
            else:
                signal = False
                number_of_frequencies = max(i[2].shape[1] for i in indices)
                channels = sumpf_internal.allocate_array(shape=(number_of_channels, number_of_frequencies, length),
                                                         dtype=dataset_channels.dtype)
                l, f = dataset_channels.shape[0:2]
                channels[0:l, 0:f, start:stop] = dataset_channels
                if f < number_of_frequencies:
                    channels[0:l, f:, start:stop] = 0.0
                if l < number_of_channels:
                    channels[l:, :, start:stop] = 0.0
            # copy the other data sets
            last_index = 0  # the maximum sample index, at which there is already data in the channels array
            for index, previous in zip(indices[1:], indices[0:-1]):
                start, stop, dataset_channels = index
                start -= offset
                stop -= offset
                l, f = dataset_channels.shape[0:2]
                last_index = max(last_index, previous[1] - offset)
                if start < last_index:  # the current data set overlaps with the previous one, add the samples in the overlapping region
                    if last_index >= stop:  # pylint: disable=no-else-continue
                        stop = start + dataset_channels.shape[-1]
                        if signal:
                            channels[0:l, start:stop] += dataset_channels
                        else:
                            channels[0:l, 0:f, start:stop] += dataset_channels
                        continue
                    else:
                        if signal:
                            channels[0:l, start:last_index] += dataset_channels[:, 0:last_index - start]
                            dataset_channels = dataset_channels[:, last_index - start:]
                        else:
                            channels[0:l, 0:f, start:last_index] += dataset_channels[:, :, 0:last_index - start]
                            dataset_channels = dataset_channels[:, :, last_index - start:]
                        start = last_index
                elif start > last_index:    # a gap between the current data set and the previous one, fill it with zeros
                    if signal:
                        channels[:, last_index:start] = 0.0
                    else:
                        channels[:, :, last_index:start] = 0.0
                if signal:
                    channels[0:l, start:stop] = dataset_channels
                    if len(dataset_channels) < number_of_channels:   # if the current signal has less channels than the other, fill the missing channels with zeros
                        channels[l:, start:stop] = 0.0
                else:
                    channels[0:l, 0:f, start:stop] = dataset_channels
                    if f < number_of_frequencies:
                        channels[0:l, f:, start:stop] = 0.0
                    if len(dataset_channels) < number_of_channels:   # if the current signal has less channels than the other, fill the missing channels with zeros
                        channels[l:, :, start:stop] = 0.0
            # create and return the result
            if signal:
                return sumpf.Signal(channels=channels,
                                    sampling_rate=first.sampling_rate(),
                                    offset=offset,
                                    labels=tuple(f"Concatenation {i}" for i in range(1, number_of_channels + 1)))
            else:
                return sumpf.Spectrogram(channels=channels,
                                         resolution=first.resolution(),
                                         sampling_rate=first.sampling_rate(),
                                         offset=offset,
                                         labels=tuple(f"Concatenation {i}" for i in range(1, number_of_channels + 1)))

    @connectors.MultiInput("output")
    def add(self, data):
        """Adds a data set to the end of the sequence, which shall be concatenated.
        This method returns an ID, which can be passed to the :meth:`remove` and
        :meth:`replace` methods in order to remove or replace this data set.

        :param data: a :class:`~sumpf.Signal` or :class:`~sumpf.Spectrogram` instance
        :returns: a unique identifier
        """
        return self.__data.add(data)

    @add.remove
    def remove(self, data_id):
        """Removes a data set, that is specified by the given ID, from the sequence,
        which shall be concatenated.

        :param data_id: the unique identifier, under which the referred data set is stored
        :returns: self
        """
        del self.__data[data_id]
        return self

    @add.replace
    def replace(self, data_id, data):
        """Replaces a data set, that is specified by the given ID, with another one.

        :param data_id: the unique identifier, under which the referred data set is stored
        :param data: the new :class:`~sumpf.Signal` or :class:`~sumpf.Spectrogram` instance
        :returns: data_id
        """
        self.__data[data_id] = data
        return data_id
