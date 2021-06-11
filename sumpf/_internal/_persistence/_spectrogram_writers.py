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

"""Contains classes and helper functions to save spectrograms to a file."""

import json
import pickle
import enum
import numpy
from ._auto_writer import AutoWriter

__all__ = ("Formats", "Writer")


class Formats(enum.Enum):
    """An enumeration of the file formats, that are supported for writing :class:`~sumpf.Spectrogram`
    instances to a file."""
    AUTO = enum.auto()
    # text formats
    TEXT_JSON = enum.auto
    # Python formats
    NUMPY_NPZ = enum.auto()
    PYTHON_PICKLE = enum.auto()


_json = (Formats.TEXT_JSON,)
file_extension_mapping = {".json": _json,   # maps file extensions to formats, that are commonly associated with that format in descending order
                          ".js": _json,
                          ".npz": (Formats.NUMPY_NPZ,),
                          ".pickle": (Formats.PYTHON_PICKLE,)}


class Writer:
    """Base class for writers, that write :class:`~sumpf.Spectrogram` instances to
    a file.

    If the writer requires a third party library for writing a file in the given
    format, the derived class must override the ``__init__`` method, so that it
    accepts the file format as a parameter and raises an :exc:`ImportError``, if
    the library is missing. File formats are specified as flags from the :attr:`~sumpf.Spectrogram.file_formats`
    enumeration.

    Derived classes must also implement the ``__call__`` method, that accepts the
    spectrogram and the path as parameters. If anything goes wrong, the method shall
    raise an error.

    Derived classes must have a static attribute, which contains a tuple of file
    formats, that can be written with instances of that class.
    """

    def __init__(self, file_format):
        """
        :param file_format: a flag from the :class:`~sumpf.Spectrogram.file_formats`
                            enumeration, which specifies the file format, that
                            shall be loaded with this writer.
        :raises ImportError: if a third party library is required to write this
                             format, but not available
        """


writers = {}    # maps file formats to writer instances, that can be used for future saving of a spectrum
writers[Formats.AUTO] = AutoWriter(file_extension_mapping=file_extension_mapping,
                                   writers=writers,
                                   writer_base_class=Writer)


def as_dict(spectrogram):
    """Serializes a spectrogram to a dictionary."""
    channels = []
    for c in spectrogram.channels():
        channel = {"real": [tuple(s) for s in numpy.real(c)],
                   "imaginary": [tuple(s) for s in numpy.imag(c)]}
        channels.append(channel)
    return {"channels": channels,
            "resolution": spectrogram.resolution(),
            "sampling_rate": spectrogram.sampling_rate(),
            "offset": spectrogram.offset(),
            "labels": spectrogram.labels()}


class JsonWriter(Writer):
    """Writes a JSON representation of a spectrogram to a file."""
    formats = (Formats.TEXT_JSON,)

    def __call__(self, spectrum, path):
        """Saves the given spectrogram in the given file path.

        :param data: the :class:`~sumpf.Spectrogram` instance
        :param path: the path of the file, in which the spectrogram shall be saved
        """
        with open(path, "w") as f:
            json.dump(as_dict(spectrum), f, indent=4)


class NumpyNpzWriter(Writer):
    """Saves the spectrogram in a compressed :mod:`numpy` binary file."""
    formats = (Formats.NUMPY_NPZ,)

    def __call__(self, spectrogram, path):
        """Saves the given spectrogram in the given file path.

        :param data: the :class:`~sumpf.Spectrogram` instance
        :param path: the path of the file, in which the spectrogram shall be saved
        """
        with open(path, "wb") as f:
            numpy.savez_compressed(f,
                                   channels=spectrogram.channels(),
                                   resolution=spectrogram.resolution(),
                                   sampling_rate=spectrogram.sampling_rate(),
                                   offset=spectrogram.offset(),
                                   labels=spectrogram.labels())


class PickleWriter(Writer):
    """Writes a :mod:`pickle` serialization of a spectrogram to a file.
    The pickle format also supports sub-classes of :class:`~sumpf.Spectrogram`,
    so that loaded spectrograms are of the same class as the original.

    .. warning::

       Since the reader for this file format basically executes Python code from
       the read file, it can be a security hazard, that executes malicious code,
       when reading prepared files.
    """
    formats = (Formats.PYTHON_PICKLE,)

    def __call__(self, spectrogram, path):
        """Saves the given spectrogram in the given file path.

        :param data: the :class:`~sumpf.Spectrogram` instance
        :param path: the path of the file, in which the spectrogram shall be saved
        """
        with open(path, "wb") as f:
            pickle.dump(spectrogram, f)
