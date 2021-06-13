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

"""Contains helper functions and classes for the loading and saving data sets from/to files."""

import os

__all__ = ("read_file", "get_writer")


def read_file(path, readers, reader_base_class):  # noqa; pylint: disable=too-many-branches; this function is spaghetti code, but the sequence of read attempts is easy to follow
    """A helper function, that implements the basic algorithm for reading data
    sets from a file. The algorithm goes through the following steps:

    1. first, see if there is a reader, that has already been used for files with
       the extension of the given file before.
    2. if that fails, iterate over the reader classes, that claim to be able to
       load files with the extension of the given file and try them.
    3. if that also fails, try all reader classes.
    4. if everything has failed, raise an error.

    :param path: the path to the file, that shall be loaded
    :param readers: a dictionary, that maps file extensions to reader instances,
                    that have already been used to load files with the file extension.
                    If this function creates a new reader, that successfully reads
                    the given file, that reader will be added to the dictionary.
    :param reader_base_class: the base class for the readers. This function iterates
                              over sub-classes of this class in the steps 2. and 3..
    :returns: the loaded data set
    """
    exception = None
    # check if a reader for the given file type has already been instantiated
    extension = os.path.splitext(path)[-1]
    if extension in readers:
        readers_list = readers[extension]
    else:
        readers_list = []
    # try to open the file with an already instantiated reader
    for reader in readers_list:
        try:
            result = reader(path)
        except Exception as e:  # pylint: disable=broad-except; if anything goes wrong, the reading shall be attempted with another reader
            exception = e if exception is None else exception
        else:
            return result
    # try to open the file with a reader, that is associated with the file type
    for cls in reader_base_class.__subclasses__():
        if extension in cls.extensions and not any((isinstance(r, cls) for r in readers_list)):
            try:
                reader = cls()
            except ImportError:
                continue
            else:
                readers_list.append(reader)
                try:
                    result = reader(path)
                except Exception as e:  # pylint: disable=broad-except; if anything goes wrong, the reading shall be attempted with another reader
                    exception = e if exception is None else exception
                else:
                    return result
    # try to open the file with a reader, that is not associated with the file type
    for cls in reader_base_class.__subclasses__():
        if extension not in cls.extensions and not any((isinstance(r, cls) for r in readers_list)):
            try:
                reader = cls()
            except ImportError:
                continue
            else:
                try:
                    result = reader(path)
                except Exception as e:  # pylint: disable=broad-except; if anything goes wrong, the reading shall be attempted with another reader
                    exception = e if exception is None else exception
                else:
                    readers_list.append(reader)
                    return result
    # if all attempts to read the file failed, raise an error
    raise ValueError(f"failed to read file '{path}'") from exception


def get_writer(file_format, writers, writer_base_class):
    """Returns a writer class for the given file format. This function mainly
    exists to catch ImportErrors, if a writer requires a missing library, and
    trying to find a writer, for which all dependencies are available.

    :param file_format: the file format flag from the enumeration, that lists
                        all available formats for the given data set class.
    :param writers: a dictionary, that maps file format flags to already existing
                    writer instances. If this function instantiates a new writer,
                    it will be added to that dictionary.
    :param writer_base_class: the base class for all writers. This function may
                              iterate over all sub-classes of this class, when
                              trying to create a suitable writer.
    :returns: a writer object, that can be called with the data set and the
              file path, in which the data set shall be saved.
    """
    if file_format in writers:
        return writers[file_format]
    else:
        for cls in writer_base_class.__subclasses__():
            if file_format in cls.formats:
                try:
                    writer = cls(file_format)
                except ImportError:
                    continue
                else:
                    writers[file_format] = writer
                    return writer
        raise ValueError(f"file format cannot be written: {file_format}")
