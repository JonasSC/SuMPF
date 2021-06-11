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

"""Contains classes and helper functions to save spectrums to a file."""

import csv
import json
import pickle
import enum
import numpy
from ._auto_writer import AutoWriter

__all__ = ("Formats", "Writer")


class Formats(enum.Enum):
    """An enumeration of the file formats, that are supported for writing :class:`~sumpf.Spectrum`
    instances to a file."""
    AUTO = enum.auto()
    # text formats
    TEXT_CSV = enum.auto()
    TEXT_JSON = enum.auto
    # Python formats
    NUMPY_NPZ = enum.auto()
    NUMPY_NPY = enum.auto()
    PYTHON_PICKLE = enum.auto()


_json = (Formats.TEXT_JSON,)
file_extension_mapping = {".csv": (Formats.TEXT_CSV,),  # maps file extensions to formats, that are commonly associated with that format in descending order
                          ".json": _json,
                          ".js": _json,
                          ".npz": (Formats.NUMPY_NPZ,),
                          ".npy": (Formats.NUMPY_NPY,),
                          ".pickle": (Formats.PYTHON_PICKLE,)}


class Writer:
    """Base class for writers, that write :class:`~sumpf.Spectrum` instances to
    a file.

    If the writer requires a third party library for writing a file in the given
    format, the derived class must override the ``__init__`` method, so that it
    accepts the file format as a parameter and raises an :exc:`ImportError``, if
    the library is missing. File formats are specified as flags from the :attr:`~sumpf.Spectrum.file_formats`
    enumeration.

    Derived classes must also implement the ``__call__`` method, that accepts the
    spectrum and the path as parameters. If anything goes wrong, the method shall
    raise an error.

    Derived classes must have a static attribute, which contains a tuple of file
    formats, that can be written with instances of that class.
    """

    def __init__(self, file_format):
        """
        :param file_format: a flag from the :class:`~sumpf.Spectrum.file_formats`
                            enumeration, which specifies the file format, that
                            shall be loaded with this writer.
        :raises ImportError: if a third party library is required to write this
                             format, but not available
        """


writers = {}    # maps file formats to writer instances, that can be used for future saving of a spectrum
writers[Formats.AUTO] = AutoWriter(file_extension_mapping=file_extension_mapping,
                                   writers=writers,
                                   writer_base_class=Writer)


def as_dict(spectrum):
    """Serializes a spectrum to a dictionary."""
    return {"channels": [{"real": tuple(numpy.real(c)),
                          "imaginary": tuple(numpy.imag(c))}
                         for c in spectrum.channels()],
            "resolution": spectrum.resolution(),
            "labels": spectrum.labels()}


class CsvWriter(Writer):
    """Saves the spectrum in a CSV file, in which the first column contains the
    frequency samples.
    """
    formats = (Formats.TEXT_CSV,)

    def __call__(self, spectrum, path):
        """Saves the given spectrum in the given file path.

        :param data: the :class:`~sumpf.Spectrum` instance
        :param path: the path of the file, in which the spectrum shall be saved
        """
        with open(path, "w", newline="") as f:
            columns = ["frequency"]
            columns.extend(spectrum.labels())
            writer = csv.writer(f)
            writer.writerow(columns)
            for t, row in zip(spectrum.frequency_samples(), spectrum.channels().transpose()):
                writer.writerow((t, *row))


class JsonWriter(Writer):
    """Writes a JSON representation of a spectrum to a file."""
    formats = (Formats.TEXT_JSON,)

    def __call__(self, spectrum, path):
        """Saves the given spectrum in the given file path.

        :param data: the :class:`~sumpf.Spectrum` instance
        :param path: the path of the file, in which the spectrum shall be saved
        """
        with open(path, "w") as f:
            json.dump(as_dict(spectrum), f, indent=4)


class NumpyNpyWriter(Writer):
    """Saves the spectrum in a :mod:`numpy` array file, in which the first column contains
    the frequency samples.
    """
    formats = (Formats.NUMPY_NPY,)

    def __call__(self, spectrum, path):
        """Saves the given spectrum in the given file path.

        :param data: the :class:`~sumpf.Spectrum` instance
        :param path: the path of the file, in which the spectrum shall be saved
        """
        array = numpy.empty(shape=(len(spectrum) + 1, spectrum.length()), dtype=numpy.complex128)
        array[0, :] = spectrum.frequency_samples()
        array[1:, :] = spectrum.channels()
        with open(path, "wb") as f:
            numpy.save(f, array)


class NumpyNpzWriter(Writer):
    """Saves the spectrum in a compressed :mod:`numpy` binary file."""
    formats = (Formats.NUMPY_NPZ,)

    def __call__(self, spectrum, path):
        """Saves the given spectrum in the given file path.

        :param data: the :class:`~sumpf.Spectrum` instance
        :param path: the path of the file, in which the spectrum shall be saved
        """
        with open(path, "wb") as f:
            numpy.savez_compressed(f,
                                   channels=spectrum.channels(),
                                   resolution=spectrum.resolution(),
                                   labels=spectrum.labels())


class PickleWriter(Writer):
    """Writes a :mod:`pickle` serialization of a spectrum to a file.
    The pickle format also supports sub-classes of :class:`~sumpf.Spectrum`, so
    that loaded spectrums are of the same class as the original.

    .. warning::

       Since the reader for this file format basically executes Python code from
       the read file, it can be a security hazard, that executes malicious code,
       when reading prepared files.
    """
    formats = (Formats.PYTHON_PICKLE,)

    def __call__(self, spectrum, path):
        """Saves the given spectrum in the given file path.

        :param data: the :class:`~sumpf.Spectrum` instance
        :param path: the path of the file, in which the spectrum shall be saved
        """
        with open(path, "wb") as f:
            pickle.dump(spectrum, f)
