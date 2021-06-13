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

"""Contains classes and helper functions to load signals from a file."""

import aifc
import csv
import json
import os
import pickle
import struct
import wave
import numpy
import sumpf
from .._functions import allocate_array

__all__ = ("readers", "Reader")

readers = {}    # maps file extensions to reader instances, that can be used for future loading of a signal


def from_dict(dictionary):
    """Deserializes a signal from a dictionary."""
    if "channels" in dictionary:
        channels = allocate_array(shape=numpy.shape(dictionary["channels"]))
        channels[:, :] = dictionary["channels"]
    else:
        channels = numpy.empty(shape=(1, 0))
    return sumpf.Signal(channels=channels,
                        sampling_rate=dictionary.get("sampling_rate", 48000.0),
                        offset=dictionary.get("offset", 0),
                        labels=dictionary.get("labels", ()))


def from_rows(time_column, data_rows, labels):
    """Deserializes a signal from tabular data.

    :param time_column: a vector with time values, that correspond to the rows
                        in the data_rows matrix with the same index.
    :param data_rows: a matrix, where the rows contain a sample for each channel
                      of the signal.
    :param labels: the labels for the channels or an empty tuple.
    :returns: the deserialized signal
    """
    if len(data_rows) and len(data_rows[0]):    # pylint: disable=len-as-condition; data_rows can be a NumPy array
        sorted_time_row = sorted(time_column)
        minimum_time = sorted_time_row[0]
        maximum_time = sorted_time_row[-1]
        if len(sorted_time_row) <= 1:
            if minimum_time == 0.0:
                sampling_rate = 48000.0
            else:
                sampling_rate = 1.0 / abs(minimum_time)
        else:
            sampling_rate = (len(sorted_time_row) - 1) / (maximum_time - minimum_time)
        offset = int(round(minimum_time * sampling_rate))
        if numpy.array_equal(time_column, sorted_time_row):
            sorted_data_rows = data_rows
        else:
            sorted_data_rows = [[e for _, e in sorted(zip(time_column, data_row))] for data_row in data_rows]
        channels = allocate_array(shape=numpy.shape(sorted_data_rows))
        channels[:] = sorted_data_rows
        if len(labels) < len(channels):
            labels = tuple(labels) + ("",) * (len(channels) - len(labels))
        elif len(labels) > len(channels):
            labels = labels[0:len(channels)]
        return sumpf.Signal(channels=channels, sampling_rate=sampling_rate, offset=offset, labels=labels)
    else:
        return sumpf.Signal()


class Reader:
    """Base class for readers, that load :class:`~sumpf.Signal` instances from a file.

    Derived classes must implement the ``__call__`` method, that accepts the path to
    the file and returns the loaded signal. If anything goes wrong, the method
    shall raise an error (instead of returning None).
    """


class CsvReader(Reader):
    """Loads the signal from a CSV file, in which the first column contains the
    time samples.
    """
    extensions = (".csv",)

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Signal` from the given path.

        :param path: the path of the file, from which the signal shall be loaded
        :returns: a :class:`~sumpf.Signal` instance
        """
        with open(path, newline="") as f:
            reader = csv.reader(f)
            rows = []
            time_samples = []
            first_row = next(reader)
            try:
                time_samples.append(float(first_row[0]))
                rows.append([float(c) for c in first_row[1:]])
            except ValueError:
                labels = tuple(first_row[1:])
            else:
                labels = ()
            for row in reader:
                time_samples.append(float(row[0]))
                rows.append([float(c) for c in row[1:]])
            return from_rows(time_column=time_samples,
                             data_rows=numpy.transpose(rows),
                             labels=labels)


class JsonReader(Reader):
    """Reads a JSON representation of a signal from a file."""
    extensions = (".json", ".js")

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Signal` from the given path.

        :param path: the path of the file, from which the signal shall be loaded
        :returns: a :class:`~sumpf.Signal` instance
        """
        with open(path) as f:
            return from_dict(json.load(f))


class NumpyReader(Reader):
    """Reads a signal from a :mod:`numpy` file."""
    extensions = (".npz", ".npy")

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Signal` from the given path.

        :param path: the path of the file, from which the signal shall be loaded
        :returns: a :class:`~sumpf.Signal` instance
        """
        try:
            with numpy.load(path) as data:
                return from_dict(data)
        except AttributeError:  # npy files cannot be opened with a context manager
            array = numpy.load(path)
            filename = os.path.split(path)[-1]
            return from_rows(time_column=array[0],
                             data_rows=array[1:],
                             labels=[f"{filename} {i}" for i in range(1, array.shape[0])])


class PickleReader(Reader):
    """Reads a :mod:`pickle` serialization of a signal from a file.
    The loaded signal can also be an instance of a sub-class of :class:`~sumpf.Signal`.

    .. warning::

       Since this reader basically executes Python code from the read file, it can
       be a security hazard, that executes malicious code, when reading prepared
       files.
    """
    extensions = (".pickle",)

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Signal` from the given path.

        :param path: the path of the file, from which the signal shall be loaded
        :returns: a :class:`~sumpf.Signal` instance
        """
        with open(path, "rb") as f:
            result = pickle.load(f)
            assert isinstance(result, sumpf.Signal)
            return result


class StandardLibraryReader:
    """A base class, that contains common code to implement reading a file with
    the help of the builtin :mod:`wave` and :mod:`aifc` modules."""

    def __init__(self, module, sample_width_mapping, endianness):
        """
        :param module: the module (e.g. :mod:`wave` or :mod:`aifc`)
        :param sample_width_mapping: a dictionary, that maps the number of bytes
                                     per sample to a character for the :func:`struct.unpack`
                                     format string.
        :param endianness: "<" for little endian, ">" for big endian
        """
        self.__module = module
        self.__sample_width_mapping = sample_width_mapping
        self.__endianness = endianness

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Signal` from the given path.

        :param path: the path of the file, from which the signal shall be loaded
        :returns: a :class:`~sumpf.Signal` instance
        """
        path = str(path)  # the wave and aifc modules cannot deal with pathlib objects (at least not in Python 3.9)
        chunk_size = 2048
        with self.__module.open(path, mode="rb") as f:
            number_of_channels = f.getnchannels()
            number_of_samples = f.getnframes()
            sample_mask = self.__sample_width_mapping[f.getsampwidth()]
            signed = sample_mask.islower()  # specifies, if the integers in the file are signed or not
            channels = allocate_array(shape=(number_of_channels, number_of_samples))
            total_chunk_size = (number_of_channels * chunk_size)
            mask = f"{self.__endianness}{total_chunk_size}{sample_mask}"
            factor = 1.0 / (2 ** (8 * f.getsampwidth() - 1))    # maps the maximum value of the integers from the file to 1.0
            i = 0
            while i + chunk_size < number_of_samples:
                chunk = struct.unpack(mask, f.readframes(chunk_size))
                decoded = numpy.multiply(chunk, factor)
                for c in range(number_of_channels):
                    channels[c, i:i + chunk_size] = decoded[c:None:number_of_channels]
                i += chunk_size
            remaining_samples = number_of_samples - i
            if remaining_samples:
                remaining_chunk_size = (number_of_channels * remaining_samples)
                remaining_mask = f"{self.__endianness}{remaining_chunk_size}{sample_mask}"
                chunk = struct.unpack(remaining_mask, f.readframes(remaining_samples))
                decoded = numpy.multiply(chunk, factor)
                for c in range(number_of_channels):
                    channels[c, i:] = decoded[c:None:number_of_channels]
            if not signed:
                channels -= 1.0
            filename = os.path.split(path)[-1]
            return sumpf.Signal(channels=channels,
                                sampling_rate=float(f.getframerate()),
                                offset=0,
                                labels=[f"{filename} {i}" for i in range(1, number_of_channels + 1)])


class WaveReader(StandardLibraryReader, Reader):
    """Loads integer wav files with the help of the :mod:`wave` module."""
    extensions = (".wav",)

    def __init__(self):
        StandardLibraryReader.__init__(self,
                                       module=wave,
                                       sample_width_mapping={1: "B", 2: "h", 4: "i"},
                                       endianness="<")


class AifcReader(StandardLibraryReader, Reader):
    """Loads integer aiff files with the help of the :mod:`aifc` module."""
    extensions = (".wav",)

    def __init__(self):
        StandardLibraryReader.__init__(self,
                                       module=aifc,
                                       sample_width_mapping={1: "b", 2: "h", 4: "i"},
                                       endianness=">")


class SoundfileReader(Reader):
    """Loads signals with the help of the :mod:`soundfile` library, which is based
    on ``libsndfile``."""
    extensions = (".wav", ".aiff", ".aifc", ".aif", ".flac", ".ogg", ".oga")

    def __init__(self):
        import soundfile  # noqa; pylint: disable=unused-import,import-outside-toplevel; this shall raise an ImportError, if the soundfile library cannot be imported

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Signal` from the given path.

        :param path: the path of the file, from which the signal shall be loaded
        :returns: a :class:`~sumpf.Signal` instance
        """
        import soundfile  # pylint: disable=import-outside-toplevel; having this as a top-level import would make all writers unavailable, if the soundfile library is not installed
        with soundfile.SoundFile(path) as f:
            channels = allocate_array(shape=(f.channels, f.frames))
            channels.transpose()[:] = f.read().reshape((f.frames, f.channels))
            filename = os.path.split(path)[-1]
            return sumpf.Signal(channels=channels,
                                sampling_rate=float(f.samplerate),
                                offset=0,
                                labels=[f"{filename} {i}" for i in range(1, f.channels + 1)])
