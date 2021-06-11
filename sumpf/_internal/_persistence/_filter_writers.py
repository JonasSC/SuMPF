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

"""Contains classes and helper functions to write signals to a file."""

import csv
import enum
import json
import pickle
import numpy
import sumpf._internal as sumpf_internal
from ._auto_writer import AutoWriter

__all__ = ("FilterFormats", "BandsFormats", "Writer", "filter_writers", "bands_writers")


class FilterFormats(enum.Enum):
    """An enumeration of the file formats, that are supported for writing :class:`~sumpf.Filter`
    instances to a file."""
    AUTO = enum.auto()
    # text formats
    TEXT_JSON = enum.auto
    TEXT_REPR = enum.auto()
    # Python formats
    PYTHON_PICKLE = enum.auto()


class BandsFormats(enum.Enum):
    """An enumeration of the file formats, that are supported for writing :class:`~sumpf.Bands`
    instances to a file."""
    AUTO = enum.auto()
    # text formats
    TEXT_TAB_I = enum.auto()
    TEXT_TAB_J = enum.auto()
    TEXT_PIPE_I = enum.auto()
    TEXT_PIPE_J = enum.auto()
    TEXT_GNUPLOT = enum.auto()
    TEXT_CSV = enum.auto()
    TEXT_JSON = enum.auto
    TEXT_REPR = enum.auto()
    # Python formats
    NUMPY_NPY = enum.auto()
    NUMPY_NPZ = enum.auto()
    PYTHON_PICKLE = enum.auto()


_json = (FilterFormats.TEXT_JSON,)
filter_extension_mapping = {  # maps file extensions to formats, that are commonly associated with that format in descending order
    ".txt": (FilterFormats.TEXT_REPR,),
    ".json": _json,
    ".js": _json,
    ".pickle": (FilterFormats.PYTHON_PICKLE,)
}
_json = (BandsFormats.TEXT_JSON,)
bands_extension_mapping = {  # maps file extensions to formats, that are commonly associated with that format in descending order
    ".txt": (BandsFormats.TEXT_TAB_I, BandsFormats.TEXT_TAB_J, BandsFormats.TEXT_PIPE_I, BandsFormats.TEXT_PIPE_J, BandsFormats.TEXT_REPR, BandsFormats.TEXT_GNUPLOT),  # pylint: disable=line-too-long
    ".dat": (BandsFormats.TEXT_TAB_I, BandsFormats.TEXT_TAB_J, BandsFormats.TEXT_PIPE_I, BandsFormats.TEXT_PIPE_J, BandsFormats.TEXT_GNUPLOT, BandsFormats.TEXT_CSV),   # pylint: disable=line-too-long
    ".asc": (BandsFormats.TEXT_TAB_I, BandsFormats.TEXT_TAB_J, BandsFormats.TEXT_PIPE_I, BandsFormats.TEXT_PIPE_J, BandsFormats.TEXT_GNUPLOT),                          # pylint: disable=line-too-long
    ".tab": (BandsFormats.TEXT_TAB_I, BandsFormats.TEXT_TAB_J, BandsFormats.TEXT_GNUPLOT),
    ".csv": (BandsFormats.TEXT_CSV,),
    ".json": _json,
    ".js": _json,
    ".npy": (BandsFormats.NUMPY_NPY,),
    ".npz": (BandsFormats.NUMPY_NPZ,),
    ".pickle": (BandsFormats.PYTHON_PICKLE,)
}


class Writer:
    """Base class for writers, that write :class:`~sumpf.Filter` instances to a file.

    If the writer requires a third party library for writing a file in the given
    format, the derived class must override the ``__init__`` method, so that it
    accepts the file format as a parameter and raises an :exc:`ImportError``, if
    the library is missing. File formats are specified as flags from the :attr:`~sumpf.Filter.file_formats`
    enumeration.

    Derived classes must also implement the ``__call__`` method, that accepts the
    filter and the path as parameters. If anything goes wrong, the method shall
    raise an error.

    Derived classes must have a static attribute ``formats``, which contains a
    tuple of file formats, that can be written with instances of that class.
    """

    def __init__(self, file_format):
        """
        :param file_format: a flag from the :class:`~sumpf.Filter.file_formats`
                            enumeration, which specifies the file format, that
                            shall be loaded with this writer.
        :raises ImportError: if a third party library is required to write this
                             format, but not available
        """


filter_writers = {}    # maps file formats to writer instances, that can be used for future saving of a filter
filter_writers[FilterFormats.AUTO] = AutoWriter(file_extension_mapping=filter_extension_mapping,
                                                writers=filter_writers,
                                                writer_base_class=Writer)
bands_writers = {}    # maps file formats to writer instances, that can be used for future saving of a bands filter
bands_writers[BandsFormats.AUTO] = AutoWriter(file_extension_mapping=bands_extension_mapping,
                                              writers=bands_writers,
                                              writer_base_class=Writer)


class TableWriter:
    """A base class for reading bands filter from tabular files."""

    def __call__(self, filter_, path):
        """Saves the given bands filter in the given file path.

        :param filter_: the :class:`~sumpf.Bands` instance
        :param path: the path of the file, in which the bands filter shall be saved
        """
        bands = {}
        tfs = filter_.transfer_functions()
        for i, tf in enumerate(tfs):
            if not isinstance(tf, sumpf_internal.filter_terms.Bands):
                raise ValueError("Only filters with transfer functions of type sumpf.Filter.Bands can be saved in this format.")    # pylint: disable=line-too-long
            frequencies = tf.xs
            for f, y in zip(frequencies, tf.ys):
                if f not in bands:
                    band = [None] * i
                    bands[f] = band
                else:
                    band = bands[f]
                band.append(y)
            for f in bands.keys() - set(frequencies):
                bands[f].append(None)
        if not bands and len(filter_):  # pylint: disable=len-as-condition; the evaluation of Filter instances as a boolean is not implemented, yet
            bands[None] = [None] * len(filter_)
        self._write(bands, filter_.labels(), path, tfs)

    def _write(self, bands, labels, path, transfer_functions):
        """An abstract method, whose overrides shall write the bands filter to the given file path.

        :param bands: a dictionary, that maps frequencies to lists with values
                      of the filter's channels. If a channel does not have a value
                      at a frequency, that is contained in this dictionary, the
                      respective list entry is None.
        :param labels: a tuple with the string labels of the filter's channels
        :param path: the path of the file, in which the filter shall be stored
        :param transfer_functions: the transfer functions of the filter's channels
        """
        raise NotImplementedError("this method must be implemented in a derived class")


class TextTableWriter(TableWriter):
    """Base class for writers, that store filters with only :func:`sumpf.Filter.Bands`
    filters in a tabular text file.

    Derived classes must override methods, that define the delimiter between the
    table's columns and how the numbers are rendered to stings.
    """

    def _write(self, bands, labels, path, transfer_functions):
        """Writes the bands filter to the given file path.

        :param bands: a dictionary, that maps frequencies to lists with values
                      of the filter's channels. If a channel does not have a value
                      at a frequency, that is contained in this dictionary, the
                      respective list entry is None.
        :param labels: a tuple with the string labels of the filter's channels
        :param path: the path of the file, in which the filter shall be stored
        :param transfer_functions: the transfer functions of the filter's channels
        """
        delimiter = self._delimiter()
        with open(path, "w") as file_:
            labels = delimiter.join(" ".join(l.splitlines()) for l in labels)
            file_.write(f"# frequencies{delimiter}{labels}\n")
            for f, ys in sorted(bands.items()):
                frequency = self._number(f)
                channels = delimiter.join([self._number(y) for y in ys])
                file_.write(f"{frequency}{delimiter}{channels}\n")

    def _number(self, number):
        """An abstract method, whose overrides shall return a text representation
        of the given number, that shall be written to the file.

        :param number: the number
        :returns: a text representation of the number
        """
        raise NotImplementedError("this method must be implemented in a derived class")

    def _delimiter(self):
        """An abstract method, whose overrides shall return the delimiter, with
        which the numbers shall be separated in the file.

        :returns: a string delimiter
        """
        raise NotImplementedError("this method must be implemented in a derived class")


class TextTabIWriter(TextTableWriter, Writer):
    """Writer class for storing :func:`sumpf.Filter.Bands` filters in a tabular
    text file, in which the first column contains the frequency samples.

    This writer separates the table's columns with tabulators and denotes the
    imaginary part of a complex number with an *i*.
    """
    formats = (BandsFormats.TEXT_TAB_I,)

    def _number(self, number):
        """Returns a text representation of the given number, that shall be written to the file.

        :param number: the number
        :returns: a text representation of the number
        """
        if number is None:
            return "nan"
        elif isinstance(number, (float, int)):
            return repr(number)
        else:
            imag = number.imag
            if imag == 0.0:
                return f"{number.real!r}+0.0i"
            elif imag > 0.0:
                return f"{number.real!r}+{imag!r}i"
            else:
                return f"{number.real!r}-{-imag!r}i"

    def _delimiter(self):
        """Returns the delimiter, with which the numbers shall be separated in the file.

        :returns: a string delimiter
        """
        return "\t"


class TextTabJWriter(TextTableWriter, Writer):
    """Writer class for storing :func:`sumpf.Filter.Bands` filters in a tabular
    text file, in which the first column contains the frequency samples.

    This writer separates the table's columns with tabulators and denotes the
    imaginary part of a complex number with a *j*, like it is usual in Python.
    """
    formats = (BandsFormats.TEXT_TAB_J,)

    def _number(self, number):
        """Returns a text representation of the given number, that shall be written to the file.

        :param number: the number
        :returns: a text representation of the number
        """
        if number is None:
            return "nan"
        elif isinstance(number, (float, int)):
            return repr(number)
        else:
            imag = number.imag
            if imag == 0.0:
                return f"{number.real!r}+0.0j"
            elif imag > 0.0:
                return f"{number.real!r}+{imag!r}j"
            else:
                return f"{number.real!r}-{-imag!r}j"

    def _delimiter(self):
        """Returns the delimiter, with which the numbers shall be separated in the file.

        :returns: a string delimiter
        """
        return "\t"


class TextPipeIWriter(TextTableWriter, Writer):
    """Writer class for storing :func:`sumpf.Filter.Bands` filters in a tabular
    text file, in which the first column contains the frequency samples.

    This writer separates the table's columns with pipes and denotes the imaginary
    part of a complex number with an *i*.
    """
    formats = (BandsFormats.TEXT_PIPE_I,)

    def _number(self, number):
        """Returns a text representation of the given number, that shall be written to the file.

        :param number: the number
        :returns: a text representation of the number
        """
        if number is None:
            return "nan"
        elif isinstance(number, (float, int)):
            return repr(number)
        else:
            imag = number.imag
            if imag == 0.0:
                return f"{number.real!r}+0.0i"
            elif imag > 0.0:
                return f"{number.real!r}+{imag!r}i"
            else:
                return f"{number.real!r}-{-imag!r}i"

    def _delimiter(self):
        """Returns the delimiter, with which the numbers shall be separated in the file.

        :returns: a string delimiter
        """
        return " | "


class TextPipeJWriter(TextTableWriter, Writer):
    """Writer class for storing :func:`sumpf.Filter.Bands` filters in a tabular
    text file, in which the first column contains the frequency samples.

    This writer separates the table's columns with pipes and denotes the imaginary
    part of a complex number with a *j*, like it is usual in Python.
    """
    formats = (BandsFormats.TEXT_PIPE_J,)

    def _number(self, number):
        """Returns a text representation of the given number, that shall be written to the file.

        :param number: the number
        :returns: a text representation of the number
        """
        if number is None:
            return "nan"
        elif isinstance(number, (float, int)):
            return repr(number)
        else:
            imag = number.imag
            if imag == 0.0:
                return f"{number.real!r}+0.0j"
            elif imag > 0.0:
                return f"{number.real!r}+{imag!r}j"
            else:
                return f"{number.real!r}-{-imag!r}j"

    def _delimiter(self):
        """Returns the delimiter, with which the numbers shall be separated in the file.

        :returns: a string delimiter
        """
        return " | "


class TextGnuplotWriter(TextTableWriter, Writer):
    """Writer class for storing :func:`sumpf.Filter.Bands` filters in a tabular
    text file, in which the first column contains the frequency samples.

    This writer separates the table's columns with tabulators and formats complex
    numbers as a tuple of their real and imaginary part in curly brackets, like
    it is usual in gnuplot.
    """
    formats = (BandsFormats.TEXT_GNUPLOT,)

    def _number(self, number):
        """Returns a text representation of the given number, that shall be written to the file.

        :param number: the number
        :returns: a text representation of the number
        """
        if number is None:
            return "{nan, nan}"
        elif isinstance(number, (float, int)):
            return repr(number)
        else:
            return f"{{{number.real!r},{number.imag!r}}}"

    def _delimiter(self):
        """Returns the delimiter, with which the numbers shall be separated in the file.

        :returns: a string delimiter
        """
        return "\t"


class CsvWriter(TableWriter, Writer):
    """Saves the bands filter in a CSV file, in which the first column contains
    the frequency samples.
    """
    formats = (BandsFormats.TEXT_CSV,)

    def _write(self, bands, labels, path, transfer_functions):
        """Writes the bands filter to the given file path.

        :param bands: a dictionary, that maps frequencies to lists with values
                      of the filter's channels. If a channel does not have a value
                      at a frequency, that is contained in this dictionary, the
                      respective list entry is None.
        :param labels: a tuple with the string labels of the filter's channels
        :param path: the path of the file, in which the filter shall be stored
        :param transfer_functions: the transfer functions of the filter's channels
        """
        with open(path, "w", newline="") as f:
            columns = ["frequency"]
            columns.extend(labels)
            writer = csv.writer(f)
            writer.writerow(columns)
            for f, ys in sorted(bands.items()):
                writer.writerow((f, *ys))


class ReprWriter(Writer):
    """Writes the :func:`repr`-string of a filter to a file.

    .. warning::

       Since the reader for this file format basically executes Python code from
       the read file, it can be a security hazard, that executes malicious code,
       when reading prepared files.
    """
    formats = (FilterFormats.TEXT_REPR, BandsFormats.TEXT_REPR)

    def __call__(self, filter_, path):
        """Saves the given filter in the given file path.

        :param data: the :class:`~sumpf.Filter` instance
        :param path: the path of the file, in which the filter shall be saved
        """
        with open(path, "w") as f:
            f.write(repr(filter_))


class JsonWriter(Writer):
    """Writes a JSON representation of a filter to a file."""
    formats = (FilterFormats.TEXT_JSON, BandsFormats.TEXT_JSON)

    def __call__(self, filter_, path):
        """Saves the given filter in the given file path.

        :param data: the :class:`~sumpf.Filter` instance
        :param path: the path of the file, in which the filter shall be saved
        """
        dictionary = {"transfer_functions": [tf.as_dict() for tf in filter_.transfer_functions()],
                      "labels": filter_.labels()}
        with open(path, "w") as f:
            json.dump(dictionary, f, indent=4)


class NumpyNpyWriter(TableWriter, Writer):
    """Saves a bands filter in a :mod:`numpy` array file, in which the first column
    contains the frequency samples.
    """
    formats = (BandsFormats.NUMPY_NPY,)

    def _write(self, bands, labels, path, transfer_functions):
        """Writes the bands filter to the given file path.

        :param bands: a dictionary, that maps frequencies to lists with values
                      of the filter's channels. If a channel does not have a value
                      at a frequency, that is contained in this dictionary, the
                      respective list entry is None.
        :param labels: a tuple with the string labels of the filter's channels
        :param path: the path of the file, in which the filter shall be stored
        :param transfer_functions: the transfer functions of the filter's channels
        """
        if bands:
            columns = max(len(v) for v in bands.values()) + 1
        else:
            columns = 2
        array = numpy.empty(shape=(len(bands), columns), dtype=numpy.complex128)
        for (f, ys), row in zip(sorted(bands.items()), array):
            row[0] = numpy.nan if f is None else f
            row[1:] = [numpy.nan if s is None else s for s in ys]
        with open(path, "wb") as f:
            numpy.save(f, array)


class NumpyNpzWriter(TableWriter, Writer):
    """Saves a bands filter in a compressed :mod:`numpy` binary file."""
    formats = (BandsFormats.NUMPY_NPZ,)

    def _write(self, bands, labels, path, transfer_functions):
        """Writes the bands filter to the given file path.

        :param bands: a dictionary, that maps frequencies to lists with values
                      of the filter's channels. If a channel does not have a value
                      at a frequency, that is contained in this dictionary, the
                      respective list entry is None.
        :param labels: a tuple with the string labels of the filter's channels
        :param path: the path of the file, in which the filter shall be stored
        :param transfer_functions: the transfer functions of the filter's channels
        """
        if bands:
            columns = max(len(v) for v in bands.values())
        else:
            columns = 1
        frequencies = numpy.empty(len(bands), dtype=numpy.float64)
        array = numpy.empty(shape=(len(bands), columns), dtype=numpy.complex128)
        for i, ((f, ys), row) in enumerate(zip(sorted(bands.items()), array)):
            frequencies[i] = f
            row[:] = [numpy.nan if s is None else s for s in ys]
        with open(path, "wb") as f:
            numpy.savez_compressed(f,
                                   frequencies=frequencies,
                                   channels=array,
                                   interpolations=[tf.interpolation for tf in transfer_functions],
                                   extrapolations=[tf.extrapolation for tf in transfer_functions],
                                   labels=labels)


class PickleWriter(Writer):
    """Writes a :mod:`pickle` serialization of a filter to a file.
    The pickle format also supports sub-classes of :class:`~sumpf.Filter`, so that
    loaded filters are of the same class as the original.

    .. warning::

       Since the reader for this file format basically executes Python code from
       the read file, it can be a security hazard, that executes malicious code,
       when reading prepared files.
    """
    formats = (FilterFormats.PYTHON_PICKLE, BandsFormats.PYTHON_PICKLE)

    def __call__(self, filter_, path):
        """Saves the given filter in the given file path.

        :param data: the :class:`~sumpf.Filter` instance
        :param path: the path of the file, in which the filter shall be saved
        """
        with open(path, "wb") as f:
            pickle.dump(filter_, f)
