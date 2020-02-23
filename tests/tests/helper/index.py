# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2020 Jonas Schulte-Coerne
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

"""Contains a helper class for generating index definitions for testing purposes."""

import enum
import sumpf._internal as sumpf_internal


class IndexMode(enum.Enum):
    """An enumeration to specify, how an index shall be defined."""
    INTEGER = enum.auto()
    NEGATIVE_INTEGER = enum.auto()
    FLOAT = enum.auto()
    NEGATIVE_FLOAT = enum.auto()


class Index:
    """A class for testing an indexing data by allowing an index definition in
    multiple ways.

    Some data sets allow addressing data with a positive/negative integer index
    or a positive/negative float part of the data set's length.

    Instances of this class are always instantiated with a positive float part
    of the data set's length and a flag from the IndexMode enumeration. These instances
    are callable and return the index when called with the data set's length.
    """

    def __init__(self, index, mode):
        """
        :param index: a float between 0.0 and 1.0
        :param mode: a flag from the IndexMode enumeration
        """
        self.__index = index
        self.__mode = mode

    def __call__(self, length):
        """Returns the index

        :param length: the length of the data set, that shall be indexed
        """
        if self.__mode is IndexMode.INTEGER:
            return sumpf_internal.index(self.__index, length)
        elif self.__mode is IndexMode.NEGATIVE_INTEGER:
            return sumpf_internal.index(self.__index, length) - length
        elif self.__mode is IndexMode.FLOAT:
            return self.__index
        elif self.__mode is IndexMode.NEGATIVE_FLOAT:
            return self.__index - 1.0
        else:
            raise ValueError(f"Unknown index mode: {self.__mode}")

    def __repr__(self):
        """For debug output."""
        return f"{self.__class__.__name__}(index={self.__index}, mode={self.__mode})"
