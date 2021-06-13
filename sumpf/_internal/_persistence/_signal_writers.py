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

"""Contains classes and helper functions to save signals to a file."""

import aifc
import csv
import enum
import json
import math
import pickle
import struct
import wave
import numpy
from ._auto_writer import AutoWriter

__all__ = ("Formats", "Writer")


class Formats(enum.Enum):
    """An enumeration of the file formats, that are supported for writing :class:`~sumpf.Signal`
    instances to a file."""
    AUTO = enum.auto()
    # text formats
    TEXT_CSV = enum.auto()
    TEXT_JSON = enum.auto
    # Python formats
    NUMPY_NPZ = enum.auto()
    NUMPY_NPY = enum.auto()
    PYTHON_PICKLE = enum.auto()
    # wav
    WAV_UINT8 = enum.auto()
    WAV_INT16 = enum.auto()
    WAV_INT24 = enum.auto()
    WAV_INT32 = enum.auto()
    WAV_FLOAT32 = enum.auto()
    WAV_FLOAT64 = enum.auto()
    WAV_ULAW = enum.auto()
    WAV_ALAW = enum.auto()
    # aiff
    AIFF_UINT8 = enum.auto()
    AIFF_INT8 = enum.auto()
    AIFF_INT16 = enum.auto()
    AIFF_INT24 = enum.auto()
    AIFF_INT32 = enum.auto()
    AIFF_FLOAT32 = enum.auto()
    AIFF_FLOAT64 = enum.auto()
    AIFF_ULAW = enum.auto()
    AIFF_ALAW = enum.auto()
    # lossless compression
    FLAC_INT8 = enum.auto()
    FLAC_INT16 = enum.auto()
    FLAC_INT24 = enum.auto()
    # lossy compression
    OGG_VORBIS = enum.auto()


_json = (Formats.TEXT_JSON,)
_aiff = (Formats.AIFF_FLOAT32, Formats.AIFF_INT32, Formats.AIFF_INT24, Formats.AIFF_INT16, Formats.AIFF_FLOAT64, Formats.AIFF_INT8, Formats.AIFF_UINT8, Formats.AIFF_ULAW, Formats.AIFF_ALAW)   # pylint: disable=line-too-long; the file formats are grouped in lines
_vorbis = (Formats.OGG_VORBIS,)
file_extension_mapping = {".csv": (Formats.TEXT_CSV,),  # maps file extensions to formats, that are commonly associated with that format in descending order
                          ".json": _json,
                          ".js": _json,
                          ".npz": (Formats.NUMPY_NPZ,),
                          ".npy": (Formats.NUMPY_NPY,),
                          ".pickle": (Formats.PYTHON_PICKLE,),
                          ".wav": (Formats.WAV_FLOAT32, Formats.WAV_INT32, Formats.WAV_INT24, Formats.WAV_INT16, Formats.WAV_FLOAT64, Formats.WAV_UINT8, Formats.WAV_ULAW, Formats.WAV_ALAW),   # pylint: disable=line-too-long; the file formats are grouped in lines
                          ".aiff": _aiff,
                          ".aifc": _aiff,
                          ".aif": _aiff,
                          ".flac": (Formats.FLAC_INT24, Formats.FLAC_INT16, Formats.FLAC_INT8),
                          ".ogg": _vorbis,
                          ".oga": _vorbis}


class Writer:
    """Base class for writers, that write :class:`~sumpf.Signal` instances to a file.

    If the writer requires a third party library for writing a file in the given
    format, the derived class must override the ``__init__`` method, so that it
    accepts the file format as a parameter and raises an :exc:`ImportError``, if
    the library is missing. File formats are specified as flags from the :attr:`~sumpf.Signal.file_formats`
    enumeration.

    Derived classes must also implement the ``__call__`` method, that accepts the
    signal and the path as parameters. If anything goes wrong, the method shall
    raise an error.

    Derived classes must have a static attribute ``formats``, which contains a
    tuple of file formats, that can be written with instances of that class.
    """

    def __init__(self, file_format):
        """
        :param file_format: a flag from the :class:`~sumpf.Signal.file_formats`
                            enumeration, which specifies the file format, that
                            shall be loaded with this writer.
        :raises ImportError: if a third party library is required to write this
                             format, but not available
        """


writers = {}    # maps file formats to writer instances, that can be used for future saving of a signal
writers[Formats.AUTO] = AutoWriter(file_extension_mapping=file_extension_mapping,
                                   writers=writers,
                                   writer_base_class=Writer)


def as_dict(signal):
    """Serializes a signal to a dictionary."""
    return {"channels": [tuple(c) for c in signal.channels()],
            "sampling_rate": signal.sampling_rate(),
            "offset": signal.offset(),
            "labels": signal.labels()}


class CsvWriter(Writer):
    """Saves the signal in a CSV file, in which the first column contains the
    time samples.
    """
    formats = (Formats.TEXT_CSV,)

    def __call__(self, signal, path):
        """Saves the given signal in the given file path.

        :param data: the :class:`~sumpf.Signal` instance
        :param path: the path of the file, in which the signal shall be saved
        """
        with open(path, "w", newline="") as f:
            columns = ["time"]
            columns.extend(signal.labels())
            writer = csv.writer(f)
            writer.writerow(columns)
            for t, row in zip(signal.time_samples(), signal.channels().transpose()):
                writer.writerow((t, *row))


class JsonWriter(Writer):
    """Writes a JSON representation of a signal to a file."""
    formats = (Formats.TEXT_JSON,)

    def __call__(self, signal, path):
        """Saves the given signal in the given file path.

        :param data: the :class:`~sumpf.Signal` instance
        :param path: the path of the file, in which the signal shall be saved
        """
        with open(path, "w") as f:
            json.dump(as_dict(signal), f, indent=4)


class NumpyNpyWriter(Writer):
    """Saves the signal in a :mod:`numpy` array file, in which the first column contains
    the time samples.
    """
    formats = (Formats.NUMPY_NPY,)

    def __call__(self, signal, path):
        """Saves the given signal in the given file path.

        :param data: the :class:`~sumpf.Signal` instance
        :param path: the path of the file, in which the signal shall be saved
        """
        array = numpy.empty(shape=(len(signal) + 1, signal.length()))
        array[0, :] = signal.time_samples()
        array[1:, :] = signal.channels()
        with open(path, "wb") as f:
            numpy.save(f, array)


class NumpyNpzWriter(Writer):
    """Saves the signal in a compressed :mod:`numpy` binary file."""
    formats = (Formats.NUMPY_NPZ,)

    def __call__(self, signal, path):
        """Saves the given signal in the given file path.

        :param data: the :class:`~sumpf.Signal` instance
        :param path: the path of the file, in which the signal shall be saved
        """
        with open(path, "wb") as f:
            numpy.savez_compressed(f,
                                   channels=signal.channels(),
                                   sampling_rate=signal.sampling_rate(),
                                   offset=signal.offset(),
                                   labels=signal.labels())


class PickleWriter(Writer):
    """Writes a :mod:`pickle` serialization of a signal to a file.
    The pickle format also supports sub-classes of :class:`~sumpf.Signal`, so that
    loaded signals are of the same class as the original.

    .. warning::

       Since the reader for this file format basically executes Python code from
       the read file, it can be a security hazard, that executes malicious code,
       when reading prepared files.
    """
    formats = (Formats.PYTHON_PICKLE,)

    def __call__(self, signal, path):
        """Saves the given signal in the given file path.

        :param data: the :class:`~sumpf.Signal` instance
        :param path: the path of the file, in which the signal shall be saved
        """
        with open(path, "wb") as f:
            pickle.dump(signal, f)


class StandardLibraryWriter:
    """A base class, that contains common code to implement saving a file with
    the help of the builtin :mod:`wave` and :mod:`aifc` modules."""
    formats = (Formats.WAV_INT32, Formats.WAV_INT16, Formats.WAV_UINT8,
               Formats.AIFF_INT32, Formats.AIFF_INT16, Formats.AIFF_INT8)

    def __init__(self, module, bits, signed, endianness):
        """
        :param module: the module (e.g. :mod:`wave` or :mod:`aifc`)
        :param bits: the number of bits per sample
        :param signed: True if the samples in the output files are signed, False otherwise.
        :param endianness: "<" for little endian, ">" for big endian
        """
        self.__module = module
        self.__bytes_per_sample = int(math.ceil(bits / 8))
        self.__sample_mask = {32: "i", 16: "h", 8: "b"}[bits]
        if not signed:
            self.__sample_mask = self.__sample_mask.upper()
        self.__factor = 2 ** (bits - 1)
        self.__signed = signed
        self.__endianness = endianness

    def __call__(self, signal, path):
        """Saves the given signal in the given file path.

        :param data: the :class:`~sumpf.Signal` instance
        :param path: the path of the file, in which the signal shall be saved
        """
        path = str(path)  # the wave and aifc modules cannot deal with pathlib objects (at least not in Python 3.9)
        number_of_channels, number_of_samples = signal.shape()
        chunk_size = 2048
        total_chunk_size = (number_of_channels * chunk_size)
        mask = f"{self.__endianness}{total_chunk_size}{self.__sample_mask}"
        array = numpy.empty(number_of_channels * chunk_size)
        with self.__module.open(path, "wb") as f:
            f.setnchannels(number_of_channels)
            f.setsampwidth(self.__bytes_per_sample)
            f.setframerate(max(1, int(round(signal.sampling_rate()))))
            i = 0
            while i + chunk_size <= signal.length():
                for c in range(number_of_channels):
                    array[c:None:number_of_channels] = signal.channels()[c, i:i + chunk_size]
                if not self.__signed:
                    array += 1.0
                array *= self.__factor
                chunk = struct.pack(mask, *numpy.round(array).astype(int))
                f.writeframes(chunk)
                i += chunk_size
            remaining_samples = number_of_samples - i
            if remaining_samples:
                remaining_chunk_size = number_of_channels * remaining_samples
                mask = f"{self.__endianness}{remaining_chunk_size}{self.__sample_mask}"
                if len(array) < remaining_chunk_size:
                    array = numpy.empty(remaining_chunk_size)
                else:
                    array = array[0:remaining_chunk_size]
                for c in range(number_of_channels):
                    array[c:None:number_of_channels] = signal.channels()[c, i:]
                if not self.__signed:
                    array += 1.0
                array *= self.__factor
                chunk = struct.pack(mask, *numpy.round(array).astype(int))
                f.writeframes(chunk)


class WaveWriter(StandardLibraryWriter, Writer):
    """Saves integer wav files with the help of the :mod:`wave` module."""
    formats = (Formats.WAV_INT32, Formats.WAV_INT16, Formats.WAV_UINT8)

    def __init__(self, file_format):
        """
        :param file_format: a flag from the :class:`~sumpf.Signal.file_formats`
                            enumeration, which specifies the file format, that
                            shall be loaded with this writer.
        """
        Writer.__init__(self, file_format)
        if file_format == Formats.WAV_INT32:
            StandardLibraryWriter.__init__(self, module=wave, bits=32, signed=True, endianness="<")
        elif file_format == Formats.WAV_INT16:
            StandardLibraryWriter.__init__(self, module=wave, bits=16, signed=True, endianness="<")
        elif file_format == Formats.WAV_UINT8:
            StandardLibraryWriter.__init__(self, module=wave, bits=8, signed=False, endianness="<")


class AifcWriter(StandardLibraryWriter, Writer):
    """Saves integer aiff files with the help of the :mod:`aifc` module."""
    formats = (Formats.AIFF_INT32, Formats.AIFF_INT16, Formats.AIFF_INT8)

    def __init__(self, file_format):
        """
        :param file_format: a flag from the :class:`~sumpf.Signal.file_formats`
                            enumeration, which specifies the file format, that
                            shall be loaded with this writer.
        """
        Writer.__init__(self, file_format)
        if file_format == Formats.AIFF_INT32:
            StandardLibraryWriter.__init__(self, module=aifc, bits=32, signed=True, endianness=">")
        elif file_format == Formats.AIFF_INT16:
            StandardLibraryWriter.__init__(self, module=aifc, bits=16, signed=True, endianness=">")
        elif file_format == Formats.AIFF_INT8:
            StandardLibraryWriter.__init__(self, module=aifc, bits=8, signed=True, endianness=">")


class SoundfileWriter(Writer):
    """Saves signals with the help of the :mod:`soundfile` library, which is based
    on ``libsndfile``."""
    # pylint: disable=line-too-long; the file formats are grouped in lines
    formats = (Formats.WAV_UINT8, Formats.WAV_INT16, Formats.WAV_INT24, Formats.WAV_INT32, Formats.WAV_FLOAT32, Formats.WAV_FLOAT64, Formats.WAV_ULAW, Formats.WAV_ALAW,
               Formats.AIFF_UINT8, Formats.AIFF_INT8, Formats.AIFF_INT16, Formats.AIFF_INT24, Formats.AIFF_INT32, Formats.AIFF_FLOAT32, Formats.AIFF_FLOAT64, Formats.AIFF_ULAW, Formats.AIFF_ALAW,
               Formats.FLAC_INT8, Formats.FLAC_INT16, Formats.FLAC_INT24,
               Formats.OGG_VORBIS)

    def __init__(self, file_format):
        """
        :param file_format: a flag from the :class:`~sumpf.Signal.file_formats`
                            enumeration, which specifies the file format, that
                            shall be loaded with this writer.
        :raises ImportError: if the library :mod:`soundfile` is not available
        """
        import soundfile  # noqa; pylint: disable=unused-import,import-outside-toplevel; this shall raise an ImportError, if the soundfile library cannot be imported
        super().__init__(file_format)
        settings = {Formats.WAV_UINT8: ("WAV", "PCM_U8", self.__int_greater_zero),
                    Formats.WAV_INT16: ("WAV", "PCM_16", self.__int_greater_zero),
                    Formats.WAV_INT24: ("WAV", "PCM_24", self.__int_greater_zero),
                    Formats.WAV_INT32: ("WAV", "PCM_32", self.__int_greater_zero),
                    Formats.WAV_FLOAT32: ("WAV", "FLOAT", self.__int_greater_zero),
                    Formats.WAV_FLOAT64: ("WAV", "DOUBLE", self.__int_greater_zero),
                    Formats.WAV_ULAW: ("WAV", "ULAW", self.__int_greater_zero),
                    Formats.WAV_ALAW: ("WAV", "ALAW", self.__int_greater_zero),
                    Formats.AIFF_UINT8: ("AIFF", "PCM_U8", self.__int_greater_zero),
                    Formats.AIFF_INT8: ("AIFF", "PCM_S8", self.__int_greater_zero),
                    Formats.AIFF_INT16: ("AIFF", "PCM_16", self.__int_greater_zero),
                    Formats.AIFF_INT24: ("AIFF", "PCM_24", self.__int_greater_zero),
                    Formats.AIFF_INT32: ("AIFF", "PCM_32", self.__int_greater_zero),
                    Formats.AIFF_FLOAT32: ("AIFF", "FLOAT", self.__int_greater_zero),
                    Formats.AIFF_FLOAT64: ("AIFF", "DOUBLE", self.__int_greater_zero),
                    Formats.AIFF_ULAW: ("AIFF", "ULAW", self.__int_greater_zero),
                    Formats.AIFF_ALAW: ("AIFF", "ALAW", self.__int_greater_zero),
                    Formats.FLAC_INT8: ("FLAC", "PCM_S8", self.__flac),
                    Formats.FLAC_INT16: ("FLAC", "PCM_16", self.__flac),
                    Formats.FLAC_INT24: ("FLAC", "PCM_24", self.__flac),
                    Formats.OGG_VORBIS: ("OGG", "VORBIS", self.__vorbis)}
        selected = settings[file_format]
        self.__format = selected[0]
        self.__subtype = selected[1]
        self.__sampling_rate_conversion = selected[2]

    def __call__(self, signal, path):
        """Saves the given signal in the given file path.

        :param data: the :class:`~sumpf.Signal` instance
        :param path: the path of the file, in which the signal shall be saved
        """
        import soundfile  # pylint: disable=import-outside-toplevel; having this as a top-level import would make all writers unavailable, if the soundfile library is not installed
        soundfile.write(file=path,
                        data=signal.channels().transpose(),
                        samplerate=self.__sampling_rate_conversion(signal.sampling_rate()),
                        subtype=self.__subtype,
                        format=self.__format)

    def __int_greater_zero(self, sampling_rate):    # pylint: disable=no-self-use; this "function" should be connected with this class and not as public as a static method
        """Converts the input signal's sampling rate to the nearest integer, that
        is greater than zero.
        """
        return max(1, int(round(sampling_rate)))

    def __flac(self, sampling_rate):                # pylint: disable=no-self-use; this "function" should be connected with this class and not as public as a static method
        """Converts the input signal's sampling rate to the nearest value, that
        is supported by the FLAC format.
        """
        if sampling_rate < 65535.5:
            return max(1, int(round(sampling_rate)))
        else:
            return min(int(round(sampling_rate, -1)), 655350)

    def __vorbis(self, sampling_rate):              # pylint: disable=no-self-use; this "function" should be connected with this class and not as public as a static method
        """Converts the input signal's sampling rate to the nearest value, that
        is supported by the Ogg-Vorbis format.
        """
        return max(1000, min(int(round(sampling_rate)), 200000))
