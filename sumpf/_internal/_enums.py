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

"""Contains enumeration classes."""

import enum

__all__ = ("ConvolutionMode", "MergeMode", "ShiftMode")


class ConvolutionMode(enum.Enum):
    """An enumeration of flags, which define a mode, in which a convolution or
    a correlation shall be computed:

    * ``FULL`` corresponds to the `full` mode of :func:`numpy.convolve` or :func:`numpy.correlate`.
    * ``SAME`` corresponds to the `same` mode of :func:`numpy.convolve`.
    * ``VALID`` corresponds to the `valid` mode of :func:`numpy.convolve` or :func:`numpy.correlate`.
    * ``SPECTRUM`` performs a multiplication in the frequency domain. If one signal
      shorter is shorter than the other, it will be padded with zeros prior to
      the Fourier transformation.
    * ``SPECTRUM_PADDED`` also a multiplication in the frequency domain, but the
      zero padding of both signals will be long enough to avoid the effects of
      circular convolution/correlation.
    """
    FULL = enum.auto()
    SAME = enum.auto()
    VALID = enum.auto()
    SPECTRUM = enum.auto()
    SPECTRUM_PADDED = enum.auto()


class MergeMode(enum.Enum):
    """An enumeration of flags, with which the merging strategy can be defined:

    * with ``FIRST_DATASET_FIRST``, the first channels of the merged data set will
      be the channels of the first data set, that was added to the merger.
    * with ``FIRST_CHANNELS_FIRST``, the first channels of the merged data set will
      be the first channel of each added data set. After that, the second channels
      of each data set will be added and so on, until all channels have been added
      to the result data set.
    """
    FIRST_DATASET_FIRST = enum.auto()
    FIRST_CHANNELS_FIRST = enum.auto()


class ShiftMode(enum.Enum):
    """An enumeration of flags, that define how the :meth:`~sumpf.Signal.shift`
    method shall operate:

    * in mode ``OFFSET``, the shifting will be performed by adjusting the shifted
      signal's offset parameter. The signal's channels remain the same.
    * in mode ``CROP``, the signal's samples will be shifted, while now the empty
      samples at the beginning or the end of the signal will be filled with zeros.
      In this mode, the shape of the signal's channels array remains the same as in
      the original signal, so that the samples, that are shifted over the signal's
      boundaries are cropped. The signal's offset remains the same.
    * in mode ``PAD``, the signal will be shifted and padded, just like in mode
      ``CROP``, but the channel's are extended, so that no samples are cropped.
      The signal's offset also remains the same.
    * in mode ``CYCLE``, the shift will be performed in a cyclic manner, which means,
      that the samples, that are shifted over the signal's boundaries, are inserted
      at the other end. The signal's offset and shape remain the same and no zeros
      are added.
    """
    OFFSET = enum.auto()
    CROP = enum.auto()
    PAD = enum.auto()
    CYCLE = enum.auto()
