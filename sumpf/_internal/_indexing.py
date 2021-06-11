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

"""Contains helper functions for indexing arrays"""

import collections

__all__ = ("index", "key_to_slices")


def index(i, length):
    """Converts a sample index to a positive, integer index.
    The given sample index ``i`` will be interpreted as follows:

    * a positive integer is interpreted as an index without any modification, even if it is larger than the given length
    * a negative integer is interpreted as an index from the back of the array
    * a positive float between 0.0 and 1.0 will be mapped to an integer between 0 and ``length``
    * a negative float between -1.0 and 0.0 will be mapped accordingly but from the back of the array
    * for an iterable, a list of indices is returned.

    :param i: the index as an integer, a float or a sequence of integers or floats
    :param length: the length of the array, that shall be accessed with the returned index
    :returns: a positive integer or a list of positive integers
    """
    if isinstance(i, float):
        i = int(round(i * length))
    elif isinstance(i, collections.abc.Iterable):
        return [index(j, length) for j in i]
    while i < 0:
        i += length
    return i


def key_to_slices(key, shape):
    """Converts a key for indexing an array to a slice.
    The key can be an integer index, a float between 0.0 and 1.0, which will be
    mapped to indices between 0 and len(array), or a slice.

    :param key: an integer, a float or a slice
    :param shape: the shape of the array
    :returns: a slice or a tuple of slices, if the shape is multidimensional
    """
    if isinstance(key, int):
        return slice(key, key + 1)
    elif isinstance(key, float):
        key = index(key, (shape[0] - 1))
        return slice(key, key + 1)
    elif isinstance(key, slice):
        return slice(*(index(e, shape[0]) if isinstance(e, float) else e for e in (key.start, key.stop, key.step)))   # pylint: disable=line-too-long; this will become even more unreadable, when it's split to multiple lines
    else:
        return tuple(key_to_slices(k, (length,)) for k, length in zip(key, shape))
