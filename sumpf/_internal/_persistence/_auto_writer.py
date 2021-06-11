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

"""Contains the AutoWriter class, which is a generic implementation for finding
an appropriate writer to save a given data set to disk.
"""

import os
from . import _functions as functions

__all__ = ("AutoWriter",)


class AutoWriter:
    """An implementation of the ``AUTO`` file format writer, that tries to guess
    the actual file format from the extension of the given file name. Instances
    of this class can be put in the respective ``writers`` dictionaries, so the
    :func:`get_writer` function finds them. When instantiating this class, it
    requires constructor parameters, that configure the writer instance for the
    given data set.
    """

    def __init__(self, file_extension_mapping, writers, writer_base_class):
        """
        :param file_extension_mapping: a dictionary from file extension to lists
                                       of enumeration flags, that specify formats
                                       for files, that can have the file extension.
        :param writers: a dictionary, that maps file format flags to already existing
                        writer instances. If this function instantiates a new writer,
                        it will be added to that dictionary.
        :param writer_base_class: the base class for all writers. This function
                                  may iterate over all sub-classes of this class,
                                  when trying to create a suitable writer.
        """
        self.__file_extension_mapping = file_extension_mapping
        self.__writers = writers
        self.__writer_base_class = writer_base_class
        self.__extensions = {}

    def __call__(self, data, path):
        """Saves the given data set in the given file path.

        :param data: the data set
        :param path: the path of the file, in which the data set shall be saved
        """
        extension = os.path.splitext(path)[-1]
        # check if a writer for the given format is already instantiated
        if extension in self.__extensions:
            writers = self.__extensions.get(extension, ())
            for i, writer in enumerate(writers):
                try:
                    writer(data, path)
                except ValueError:
                    pass
                else:
                    if i > 0:   # make the writer of the last successful write the first one to be tried the next time
                        del writers[i]
                        writers.insert(0, writer)
                    return
        # if no compatible writer is instantiated, check every writer, that is associated with the given file extension
        if extension in self.__file_extension_mapping:
            for file_format in self.__file_extension_mapping[extension]:
                try:
                    writer = functions.get_writer(file_format, self.__writers, self.__writer_base_class)
                    writer(data, path)
                except ImportError:
                    pass
                except ValueError:
                    pass
                else:
                    self.__extensions.setdefault(extension, []).append(writer)
                    return
            raise ImportError(f"no library found for writing to a {extension}-file")
        # if no compatible writer is associated with the file extension, raise an error
        raise ValueError(f"file format for extension '{extension}' cannot be determined")
