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

"""Contains helper functions for common functionalities."""

import collections
import ctypes
from multiprocessing import sharedctypes
import numpy
import sumpf
from ._indexing import index

__all__ = ("allocate_array", "get_window", "sanitize_labels", "scaling_factor")


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
            return sumpf.Signal(channels=window, sampling_rate=sampling_rate, labels=("Window",) * len(window))
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


def scaling_factor(signal, overlap):
    """Is similar to the :meth:`~sumpf.HannWindow.scaling_factor` method of the
    window signals. The following things are different:

    * it works with any signal
    * it returns an :func:`~numpy.array` with one value for each channel
    * the overlap must be a scalar value.

    Computes a correction factor for block-wise processed signals, that are
    split and weighted with the given signal, that maintains the original signal's
    amplitude in the processed signal.

    :param overlap: the overlap of the weighted segments as an integer of samples,
                    a float factor of the window's length.
    :returns: the scaling factors for the channels as an :func:`~numpy.array`
    """
    length = signal.length()
    overlap = index(overlap, length)
    step = length - overlap
    if step == 0:
        return numpy.zeros(len(signal))
    channels = signal.channels()
    added = numpy.sum(channels, axis=1)
    for shift in range(step, length, step):
        added += numpy.sum(channels[:, 0:length - shift], axis=1)
        added += numpy.sum(channels[:, shift:], axis=1)
    return length / added
