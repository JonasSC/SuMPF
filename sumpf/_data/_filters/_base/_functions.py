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

"""Contains helper functions for defining filters"""

import math

__all__ = ("frequency_scaling", "copy_to_out")


def frequency_scaling(cutoff_frequency, highpass):
    """Computes the frequency scaling to map the prototype filters of IIR filters
    to filters with the desired cutoff frequency.

    :param cutoff_frequency: the cutoff frequency of the filter in Hz
    :param highpass: if True, a lowpass-to-highpass-transform will be performed
    """
    if highpass:
        return 2.0 * math.pi * cutoff_frequency
    else:
        return 1.0 / (2.0 * math.pi * cutoff_frequency)


def copy_to_out(result, out):
    """A helper function, that copies a computation result into an array, that
    is passed for returning a value through call by reference.
    This is used in the terms, if they use a :mod:`numpy` function, that does not have
    a ``out`` parameter.

    :param result: the computation result
    :param out: None or an :func:`numpy.array`, into which the result shall be copied
    :returns: ``out``, if the result has been copied, ``result`` otherwise
    """
    if out is None:
        return result
    else:
        out[:] = result
        return out
