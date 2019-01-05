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

"""Contains helper functions for indexing arrays"""

__all__ = ("key_to_slices", "sample_interval")


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
        key = int(round((shape[0] - 1) * key))
        return slice(key, key + 1)
    elif isinstance(key, slice):
        return slice(*(int(round(shape[0] * e)) if isinstance(e, float) else e for e in (key.start, key.stop, key.step)))   # pylint: disable=line-too-long; this will become even more unreadable, when it's split to multiple lines
    else:
        return tuple(key_to_slices(k, (length,)) for k, length in zip(key, shape))


def sample_interval(interval, length):
    """Converts an interval for sample indices to two positive, integer indices.
    The interval can be given as a sequence of two numbers, which can be:

    * a positive integer, which is interpreted as an index, without any modification
    * a negative integer, which is interpreted as an index from the back of the array
    * a positive float between 0.0 and 1.0, which will be mapped to an integer between 0 and ``length``
    * a negative float between -1.0 and 0.0, which will be mapped accordingly but from the back of the array

    :param interval: a sequence of two numbers
    :param length: the length of the array, that shall be accessed with the returned indices
    :returns: two positive integers
    """
    start, stop = (int(round(length * b)) if isinstance(b, float) else b for b in interval)
    while start < 0:
        start += length
    while stop < 0:
        stop += length
    return start, stop
