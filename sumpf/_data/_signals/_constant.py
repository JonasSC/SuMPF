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

"""Contains the :class:`~sumpf.ConstantSignal` class."""

import numpy
import sumpf._internal as sumpf_internal
from ._signal import Signal

__all__ = ("ConstantSignal",)


class ConstantSignal(Signal):
    """A class for generating a signal, where each sample has the same constant value."""

    def __init__(self, value=0.0, sampling_rate=48000.0, length=2 ** 16):
        """
        :param value: the float value of the samples
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the signal
        """
        channels = sumpf_internal.allocate_array(shape=(1, length), dtype=numpy.float64)
        channels[:] = value
        Signal.__init__(self,
                        channels=channels,
                        sampling_rate=sampling_rate,
                        offset=0,
                        labels=("Constant",))
