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

"""Contains the :class:`~sumpf.Merge` class."""

import numpy
import connectors
import sumpf
import sumpf._internal as sumpf_internal

__all__ = ("Merge",)


class Merge:
    """Merges multiple data sets into one.

    Instances of this class can be used to merge multiple instances of :class:`~sumpf.Signal`,
    :class:`~sumpf.Spectrum`, :class:`~sumpf.Spectrogram` or :class:`~sumpf.Filter`
    into a single data set with more channels. All merged data sets must be of the
    same type.

    The resulting data set will have the same meta-data (e.g. sampling rate or
    frequency resolution) of the first data set. When merging signals or spectrograms,
    the offset of the merged data set will be the minimum of all data sets' offsets.
    The data sets will be aligned according to their offsets by filling the channels
    with zeros.

    The methods of this class are enhanced with the functionality of the *Connectors*
    package, so that instances of this class can be connected in a processing network.
    """
    modes = sumpf_internal.MergeMode    #: an enumeration, whose flags define the order of the merged data set's channels (see the :class:`~sumpf._internal._enums.MergeMode` enumeration)

    def __init__(self, data=(), mode=sumpf_internal.MergeMode.FIRST_DATASET_FIRST):
        """
        :param data: a sequence of :class:`~sumpf.Signal`, :class:`~sumpf.Spectrum`,
                     :class:`~sumpf.Spectrogram` or :class:`~sumpf.Filter` instances
        :param mode: a value from the :attr:`~sumpf.Merge.modes` enumeration
        """
        self.__data = connectors.MultiInputData()
        for s in data:
            self.__data.add(s)
        self.__mode = mode

    @connectors.Output()
    def output(self):
        """Computes the merged data set and returns it.

        :returns: a data set, that contains all channels of the added data sets.
        """
        if not self.__data:
            raise RuntimeError("Nothing to merge")
        if len(self.__data) == 1:
            return next(iter(self.__data.values()))  # simply return the first and only data set
        else:
            first = next(iter(self.__data.values()))
            number_of_channels = sum(len(s) for s in self.__data.values())
            labels = [""] * number_of_channels
            if isinstance(first, sumpf.Signal):
                merged_offset = min(s.offset() for s in self.__data.values())
                length = max(s.offset() + s.length() for s in self.__data.values()) - merged_offset
                channels = sumpf_internal.allocate_array(shape=(number_of_channels, length))
                for index, channel, offset, label in zip(self.__indices(),
                                                         (c for d in self.__data.values() for c in d.channels()),
                                                         (d.offset() for d in self.__data.values() for l in d.channels()),  # pylint: disable=line-too-long
                                                         (l for d in self.__data.values() for l in d.labels())):
                    start = offset - merged_offset
                    stop = start + len(channel)
                    channels[index, 0:start] = 0.0
                    channels[index, start:stop] = channel
                    channels[index, stop:] = 0.0
                    labels[index] = label
                return sumpf.Signal(channels=channels,
                                    sampling_rate=first.sampling_rate(),
                                    offset=merged_offset,
                                    labels=labels)
            elif isinstance(first, sumpf.Spectrum):
                length = max(s.length() for s in self.__data.values())
                channels = sumpf_internal.allocate_array(shape=(number_of_channels, length), dtype=numpy.complex128)
                for index, channel, label in zip(self.__indices(),
                                                 (c for d in self.__data.values() for c in d.channels()),
                                                 (l for d in self.__data.values() for l in d.labels())):
                    channels[index, 0:len(channel)] = channel
                    channels[index, len(channel):] = 0.0
                    labels[index] = label
                return sumpf.Spectrum(channels=channels,
                                      resolution=first.resolution(),
                                      labels=labels)
            elif isinstance(first, sumpf.Spectrogram):
                merged_offset = min(s.offset() for s in self.__data.values())
                length = max(s.offset() + s.length() for s in self.__data.values()) - merged_offset
                number_of_frequencies = max(s.number_of_frequencies() for s in self.__data.values())
                channels = sumpf_internal.allocate_array(shape=(number_of_channels, number_of_frequencies, length),
                                                         dtype=numpy.complex128)
                channels[:] = 0.0
                for index, channel, offset, label in zip(self.__indices(),
                                                         (c for d in self.__data.values() for c in d.channels()),
                                                         (d.offset() for d in self.__data.values() for l in d.channels()),  # pylint: disable=line-too-long
                                                         (l for d in self.__data.values() for l in d.labels())):
                    channel_frequencies, channel_length = channel.shape
                    start = offset - merged_offset
                    stop = start + channel_length
                    channels[index, 0:channel_frequencies, start:stop] = channel
                    labels[index] = label
                return sumpf.Spectrogram(channels=channels,
                                         resolution=first.resolution(),
                                         sampling_rate=first.sampling_rate(),
                                         offset=merged_offset,
                                         labels=labels)
            elif isinstance(first, sumpf.Filter):
                transfer_functions = [None] * number_of_channels
                for index, transfer_function, label in zip(self.__indices(),
                                                           (tf for d in self.__data.values() for tf in d.transfer_functions()),  # pylint: disable=line-too-long
                                                           (l for d in self.__data.values() for l in d.labels())):
                    transfer_functions[index] = transfer_function
                    labels[index] = label
                return sumpf.Filter(transfer_functions=transfer_functions, labels=labels)
            else:
                raise ValueError(f"Cannot merge data sets of type {type(first)}")

    @connectors.MultiInput("output")
    def add(self, data):
        """Adds a data set to the end of the sequence of signals, which shall be
        merged. This method returns an ID, which can be passed to the :meth:`~sumpf.Merge.remove`
        and :meth:`~sumpf.Merge.replace` methods in order to remove or
        replace this data set.

        :param data: a :class:`~sumpf.Signal`, :class:`~sumpf.Spectrum`,
                     :class:`~sumpf.Spectrogram` or :class:`~sumpf.Filter` instance
        :returns: a unique identifier
        """
        return self.__data.add(data)

    @add.remove
    def remove(self, data_id):
        """Removes a data set, that is specified by the given ID, from the sequence
        of data sets, which shall be merged.

        :param data_id: the unique identifier, under which the referred data set is stored
        :returns: self
        """
        del self.__data[data_id]
        return self

    @add.replace
    def replace(self, data_id, data):
        """Replaces a data set, that is specified by the given ID, with another one.

        :param data_id: the unique identifier, under which the referred data set is stored
        :param data: the new :class:`~sumpf.Signal`, :class:`~sumpf.Spectrum`,
                     :class:`~sumpf.Spectrogram` or :class:`~sumpf.Filter` instance
        :returns: data_id
        """
        self.__data[data_id] = data
        return data_id

    @connectors.Input("output")
    def set_mode(self, mode):
        """Sets the mode by which the channels of the merged data sets are ordered.

        :param mode: a value from the :attr:`~sumpf.Merge.modes` enumeration
        :returns: self
        """
        self.__mode = mode
        return self

    def __indices(self):
        """Generates indices for the result channel set.
        This generator can be used when iterating over the channels of the added
        data sets in the first data set first manner. It yields the indices for
        the result data set, so that the channels from the iteration can be copied
        to the right places.
        """
        if self.__mode is sumpf_internal.MergeMode.FIRST_DATASET_FIRST:
            i = 0
            for d in self.__data.values():
                for _ in range(len(d)):
                    yield i
                    i += 1
        elif self.__mode is sumpf_internal.MergeMode.FIRST_CHANNELS_FIRST:
            lengths = numpy.array([len(d) for d in self.__data.values()])
            for o, l in enumerate(lengths):
                p = o
                for i in range(l):
                    after = lengths[o:]
                    before = lengths[0:o]
                    yield p
                    p += len(after[after > i]) + len(before[before > i + 1])
        else:
            raise ValueError(f"invalid merge mode: {self.__mode}")
