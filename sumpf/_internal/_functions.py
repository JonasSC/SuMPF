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

"""Contains common functionalities"""

import collections
import ctypes
from multiprocessing import sharedctypes
import numpy
import sumpf

__all__ = ("arrays_equal", "allocate_array", "get_window", "sanitize_labels")


def arrays_equal(a, b):
    """Compares two :func:`numpy.array` instances for equality.

    This function is necessary because of the inconsistent behavior of how :mod:`numpy`
    handles equality checks. Usually, a ``==``-comparison returns a :func:`numpy.array`
    of booleans, while in some situations, a boolean is returned directly.

    Also, if one array is empty, the result of a ``==``-comparison is an empty
    array, too, whose :meth:`~numpy.ndarray.all` method evaluates to ``True``.
    This is of course unexpected, if the other array from the comparison is not
    empty.

    :param `a,b`: :func:`numpy.array` instances
    :returns: a boolean
    """
    result = a == b
    if isinstance(result, bool):
        return result
    else:
        return result.all() and a.shape == b.shape


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


def get_window(window, overlap, symmetric=True, sampling_rate=48000.0):
    """Convenience method for defining a window function

    * if window is an integer, a window function with that length will be generated.
       * if overlap is zero, the generated window will be a rectangular window.
       * otherwise, a Hann window will be generated.
    * if window is a :func:`numpy.array`, it will be wrapped in a :class:`~sumpf.Signal`.
    * if window is iterable, it will be converted to a :func:`numpy.array` and then wrapped in a :class:`~sumpf.Signal`.
    * otherwise, it will be returned as it is.

    :param window: an integer window length or a window signal
    :param overlap: the overlap in the application of the window function as an integer or a float
    :param symmetric: True, if the window's last sample shall be the same as its
                      first sample. False, if the window's last sample shall be
                      the same as its second sample. The latter is often beneficial
                      in segmentation applications, as it makes it easier to meet
                      the "constant overlap add"-constraint.
    :param sampling_rate: optional, specifies the sampling rate if a window is generated
    :returns: a :class:`~sumpf.Signal` instance
    """
    if isinstance(window, int):
        if overlap == 0:
            return sumpf.RectangularWindow(sampling_rate=sampling_rate, length=window, symmetric=symmetric)
        else:
            return sumpf.HannWindow(sampling_rate=sampling_rate, length=window, symmetric=symmetric)
    elif isinstance(window, numpy.ndarray):
        if len(window.shape) == 1:
            return sumpf.Signal(channels=numpy.array([window]), sampling_rate=sampling_rate, labels=("Window",))
        elif len(window.shape) == 2:
            return sumpf.Signal(channels=numpy.array(window), sampling_rate=sampling_rate, labels=("Window",) * len(window))    # pylint: disable=line-too-long; breaking this line would not make the code more readable
        else:
            raise ValueError(f"Array of shape {window.shape} cannot be wrapped in a Signal")
    elif isinstance(window, collections.abc.Iterable):
        return get_window(window=numpy.array(window), overlap=overlap, sampling_rate=sampling_rate)
    else:
        return window


def sanitize_labels(labels, number):
    """Sanitizes the labels for the channels of data sets such as signals, spectrums
    or filters:

    * the returned labels are stored in a tuple
    * the length of the tuple will be the same as the given number
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
