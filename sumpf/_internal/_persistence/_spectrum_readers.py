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

"""Contains classes and helper functions to load spectrums from a file."""

import csv
import json
import os
import pickle
import numpy
import sumpf
from .._functions import allocate_array

__all__ = ("readers", "Reader")

readers = {}    # maps file extensions to reader instances, that can be used for future loading of a spectrum


def from_dict(channels, dictionary):
    """Deserializes a spectrum from a dictionary."""
    return sumpf.Spectrum(channels=channels,
                          resolution=dictionary.get("resolution", 1.0),
                          labels=dictionary.get("labels", ()))


def from_rows(frequency_column, data_rows, labels):     # pylint: disable=too-many-branches; the branches are not too complicated in this one
    """Deserializes a spectrum from tabular data.

    :param frequency_column: a vector with frequency values, that correspond to
                             the rows in the data_rows matrix with the same index.
    :param data_rows: a matrix, where the rows contain a complex sample for each
                      channel of the spectrum.
    :param labels: the labels for the channels or an empty tuple.
    :returns: the deserialized spectrum
    """
    if len(data_rows) and len(data_rows[0]):    # pylint: disable=len-as-condition; data_rows can be a NumPy array
        # determine the resolution
        sorted_frequency_row = sorted(frequency_column)
        minimum_frequency = sorted_frequency_row[0]
        maximum_frequency = sorted_frequency_row[-1]
        if len(sorted_frequency_row) <= 1:
            resolution = 0.0
        else:
            resolution = (maximum_frequency - minimum_frequency) / (len(sorted_frequency_row) - 1)
        # determine the offset, that must be either cropped or filled with zero samples
        if resolution == 0.0:
            offset = 0
        else:
            offset = int(round(minimum_frequency / resolution))
        # sort the data rows by their corresponding value in the frequency column
        if numpy.array_equal(frequency_column, sorted_frequency_row):
            sorted_data_rows = data_rows
        else:
            sorted_data_rows = [[e for _, e in sorted(zip(frequency_column, data_row))] for data_row in data_rows]
        # create the channels
        if offset == 0:
            channels = allocate_array(shape=numpy.shape(sorted_data_rows), dtype=numpy.complex128)
            channels[:] = sorted_data_rows
        elif offset < 0:
            channels = allocate_array(shape=numpy.subtract(numpy.shape(sorted_data_rows), (0, offset)),
                                      dtype=numpy.complex128)
            channels[:] = sorted_data_rows[:, offset:]
        else:
            channels = allocate_array(shape=numpy.add(numpy.shape(sorted_data_rows), (0, offset)),
                                      dtype=numpy.complex128)
            channels[:, 0:offset] = 0.0 + 0j
            channels[:, offset:] = sorted_data_rows[:]
        # extend the labels if necessary
        if len(labels) < len(channels):
            labels = tuple(labels) + ("",) * (len(channels) - len(labels))
        elif len(labels) > len(channels):
            labels = labels[0:len(channels)]
        # create the Spectrum instance
        return sumpf.Spectrum(channels=channels, resolution=resolution, labels=labels)
    else:
        return sumpf.Spectrum()


class Reader:
    """Base class for readers, that load :class:`~sumpf.Spectrum` instances from
    a file.

    Derived classes must implement the ``__call__`` method, that accepts the path to
    the file and returns the loaded spectrum. If anything goes wrong, the method
    shall raise an error (instead of returning None).
    """


class CsvReader(Reader):
    """Loads the spectrum from a CSV file, in which the first column contains the
    frequency samples.
    """
    extensions = (".csv",)

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Spectrum` from the given path.

        :param path: the path of the file, from which the spectrum shall be loaded
        :returns: a :class:`~sumpf.Spectrum` instance
        """
        with open(path, newline="") as f:
            reader = csv.reader(f)
            rows = []
            frequency_samples = []
            first_row = next(reader)
            try:
                frequency_samples.append(float(first_row[0]))
                rows.append([complex(c) for c in first_row[1:]])
            except ValueError:
                labels = tuple(first_row[1:])
            else:
                filename = os.path.split(path)[-1]
                labels = [f"{filename} {i}" for i in range(1, len(first_row))]
            for row in reader:
                frequency_samples.append(float(row[0]))
                rows.append([complex(c) for c in row[1:]])
            return from_rows(frequency_column=frequency_samples,
                             data_rows=numpy.transpose(rows),
                             labels=labels)


class JsonReader(Reader):
    """Reads a JSON representation of a spectrum from a file."""
    extensions = (".json", ".js")

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Spectrum` from the given path.

        :param path: the path of the file, from which the spectrum shall be loaded
        :returns: a :class:`~sumpf.Spectrum` instance
        """
        with open(path) as f:
            data = json.load(f)
            if "channels" in data:
                number_of_channels = len(data["channels"])
                if number_of_channels:
                    number_of_samples = len(data["channels"][0]["real"])
                    if number_of_samples:
                        channels = allocate_array(shape=(number_of_channels, number_of_samples), dtype=numpy.complex128)
                        for i, c in enumerate(data["channels"]):
                            numpy.multiply(1j, c["imaginary"], out=channels[i])
                            numpy.add(channels[i], c["real"], out=channels[i])
                    else:
                        channels = numpy.empty(shape=(1, 0), dtype=numpy.complex128)
                else:
                    channels = numpy.empty(shape=(1, 0), dtype=numpy.complex128)
            else:
                channels = numpy.empty(shape=(1, 0), dtype=numpy.complex128)
            return from_dict(channels, data)


class NumpyReader(Reader):
    """Reads a spectrum from a :mod:`numpy` file."""
    extensions = (".npz", ".npy")

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Spectrum` from the given path.

        :param path: the path of the file, from which the spectrum shall be loaded
        :returns: a :class:`~sumpf.Spectrum` instance
        """
        try:
            with numpy.load(path) as data:
                channels = allocate_array(shape=data["channels"].shape, dtype=numpy.complex128)
                channels[:] = data["channels"]
                return from_dict(channels, data)
        except AttributeError:  # npy files cannot be opened with a context manager
            array = numpy.load(path)
            filename = os.path.split(path)[-1]
            return from_rows(frequency_column=array[0].real,
                             data_rows=array[1:],
                             labels=[f"{filename} {i}" for i in range(1, array.shape[0])])


class PickleReader(Reader):
    """Reads a :mod:`pickle` serialization of a spectrum from a file.
    The loaded spectrum can also be an instance of a sub-class of :class:`~sumpf.Spectrum`.

    .. warning::

       Since this reader basically executes Python code from the read file, it can
       be a security hazard, that executes malicious code, when reading prepared
       files.
    """
    extensions = (".pickle",)

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Spectrum` from the given path.

        :param path: the path of the file, from which the spectrum shall be loaded
        :returns: a :class:`~sumpf.Spectrum` instance
        """
        with open(path, "rb") as f:
            result = pickle.load(f)
            assert isinstance(result, sumpf.Spectrum)
            return result
