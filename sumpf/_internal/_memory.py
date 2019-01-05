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

"""Contains functionalities for memory management"""

import ctypes
from multiprocessing import sharedctypes
import numpy

__all__ = ("allocate_array", "sanitize_labels")


def allocate_array(shape, dtype=numpy.float64):
    """Allocates a :func:`numpy.array` with the given shape and the given dtype in the shared memory.

    :param shape: the shape of the requested array
    :param dtype: the dtype of the numbers, that are stored in the array (defaults to ``numpy.float64``
    :returns: a :func:`numpy.array`
    """
    # compute the required memory
    factor = numpy.dtype(dtype).itemsize // numpy.dtype(numpy.float64).itemsize
    size = factor * int(numpy.prod(shape))
    # allocate a flat array in the shared memory
    flat_array = sharedctypes.RawArray(ctypes.c_double, size)
    # cast the array into a NumPy array with the desired shape and dtype
    shaped_array = numpy.frombuffer(flat_array, dtype=dtype).reshape(shape)
    return shaped_array


def sanitize_labels(labels, number):
    """Sanitizes the labels for the channels of data sets such as signals, spectrums
    or filters:

    * the returned labels are stored in a tuple
    * the length of the tuple will be the same as the give number
    * for missing labels, empty strings are added
    * surplus labels are cropped

    :param labels: a possibly incomplete sequence of string labels or None to
                   generate a tuple of empty strings
    :param number: the desired length of the returned tuple, which should e.g.
                   be the number of channels of the signal or spectrum
    :returns: a tuple of string labels
    """
    if labels is None:
        return ("",) * number
    elif len(labels) < number:
        return tuple(labels) + ("",) * (number - len(labels))
    elif len(labels) > number:
        return tuple(labels[0:number])
    else:
        return tuple(labels)
