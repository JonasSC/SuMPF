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

"""Functionality for reading and writing files with :class:`~sumpf.Filter` instances."""

import enum
import numpy
import sumpf
from sumpf import _internal as sumpf_internal

__all__ = ("formats", "readers", "writers", "Reader", "Writer")


class formats(enum.Enum):
    """An enumeration of the file formats, that are supported for writing :class:`~sumpf.Filter`
    instances to a file."""
    AUTO = enum.auto()
    # text formats
    TEXT_REPR = enum.auto()
    TEXT_JSON = enum.auto
    # Python formats
    PYTHON_PICKLE = enum.auto()


_json = (formats.TEXT_JSON,)
file_extension_mapping = {".txt": (formats.TEXT_REPR,),     # maps file extensions to formats, that are commonly associated with that format in descending order
                          ".json": _json,
                          ".js": _json,
                          ".pickle": (formats.PYTHON_PICKLE,)}


class Reader:
    """Base class for readers, that load :class:`~sumpf.Filter` instances from a file.

    Derived classes must implement the ``__call__`` method, that accepts the path to
    the file and returns the loaded filter. If anything goes wrong, the method
    shall raise an error (instead of returning None).
    """


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


readers = {}    # maps file extensions to reader instances, that can be used for future loading of a filter
writers = {}    # maps file formats to writer instances, that can be used for future saving of a filter
writers[formats.AUTO] = sumpf_internal.AutoWriter(file_extension_mapping=file_extension_mapping,
                                                  writers=writers,
                                                  writer_base_class=Writer)

###########
# Readers #
###########


class ReprReader(Reader):
    """Reads a :func:`repr`-string of a filter from a file and evaluates it.

    .. warning::

       Since this reader basically executes Python code from the read file, it can
       be a security hazard, that executes malicious code, when reading prepared
       files.
    """
    extensions = (".txt",)

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Filter` from the given path.

        :param path: the path of the file, from which the filter shall be loaded
        :returns: a :class:`~sumpf.Filter` instance
        """
        with open(path) as f:
            result = eval(f.read(), {}, {"Filter": sumpf.Filter, "array": numpy.array})   # pylint: disable=eval-used
            assert isinstance(result, sumpf.Filter)
            return result


class JsonReader(Reader):
    """Reads a JSON representation of a filter from a file."""
    extensions = (".json", ".js")

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Filter` from the given path.

        :param path: the path of the file, from which the filter shall be loaded
        :returns: a :class:`~sumpf.Filter` instance
        """
        import json
        with open(path) as f:
            data = json.load(f)
            transfer_functions = [sumpf_internal.term_from_dict(tf) for tf in data["transfer_functions"]]
            return sumpf.Filter(transfer_functions=transfer_functions,
                                labels=data["labels"])


class PickleReader(Reader):
    """Reads a :mod:`pickle` serialization of a filter from a file.
    The loaded filter can also be an instance of a sub-class of :class:`~sumpf.Filter`.

    .. warning::

       Since this reader basically executes Python code from the read file, it can
       be a security hazard, that executes malicious code, when reading prepared
       files.
    """
    extensions = (".pickle",)

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Filter` from the given path.

        :param path: the path of the file, from which the filter shall be loaded
        :returns: a :class:`~sumpf.Filter` instance
        """
        import pickle
        with open(path, "rb") as f:
            result = pickle.load(f)
            assert isinstance(result, sumpf.Filter)
            return result

###########
# Writers #
###########


class ReprWriter(Writer):
    """Writes the :func:`repr`-string of a filter to a file.

    .. warning::

       Since the reader for this file format basically executes Python code from
       the read file, it can be a security hazard, that executes malicious code,
       when reading prepared files.
    """
    formats = (formats.TEXT_REPR,)

    def __call__(self, filter_, path):
        """Saves the given filter in the given file path.

        :param data: the :class:`~sumpf.Filter` instance
        :param path: the path of the file, in which the filter shall be saved
        """
        with open(path, "w") as f:
            flt = sumpf.Filter(transfer_functions=filter_.transfer_functions(), labels=filter_.labels())
            f.write(repr(flt))


class JsonWriter(Writer):
    """Writes a JSON representation of a filter to a file."""
    formats = (formats.TEXT_JSON,)

    def __call__(self, filter_, path):
        """Saves the given filter in the given file path.

        :param data: the :class:`~sumpf.Filter` instance
        :param path: the path of the file, in which the filter shall be saved
        """
        import json
        dictionary = {"transfer_functions": [tf.as_dict() for tf in filter_.transfer_functions()],
                      "labels": filter_.labels()}
        with open(path, "w") as f:
            json.dump(dictionary, f, indent=4)


class PickleWriter(Writer):
    """Writes a :mod:`pickle` serialization of a filter to a file.
    The pickle format also supports sub-classes of :class:`~sumpf.Filter`, so that
    loaded filters are of the same class as the original.

    .. warning::

       Since the reader for this file format basically executes Python code from
       the read file, it can be a security hazard, that executes malicious code,
       when reading prepared files.
    """
    formats = (formats.PYTHON_PICKLE,)

    def __call__(self, filter_, path):
        """Saves the given filter in the given file path.

        :param data: the :class:`~sumpf.Filter` instance
        :param path: the path of the file, in which the filter shall be saved
        """
        import pickle
        with open(path, "wb") as f:
            pickle.dump(filter_, f)
