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

"""Contains the :class:`~sumpf.ConstantSpectrogram` class."""

import numpy
import sumpf._internal as sumpf_internal
from ._spectrogram import Spectrogram

__all__ = ("ConstantSpectrogram",)


class ConstantSpectrogram(Spectrogram):
    """A class for generating a spectrogram, where each sample has the same constant value."""

    def __init__(self,
                 value=0.0,
                 resolution=24000.0 / 2048,
                 sampling_rate=48000.0 / 4096,
                 number_of_frequencies=2049,
                 length=32):
        """
        :param value: the complex value of the samples
        :param resolution: the frequency resolution of the spectrogram as a float
        :param sampling_rate: the sampling rate of the spectrogram in Hz as an integer or a float
        :param number_of_frequencies: the number of frequency bins of the spectrogram
        :param length: the number of time bins of the spectrogram
        """
        channels = sumpf_internal.allocate_array(shape=(1, number_of_frequencies, length), dtype=numpy.complex128)
        channels[:] = value
        Spectrogram.__init__(self,
                             channels=channels,
                             resolution=resolution,
                             sampling_rate=sampling_rate,
                             offset=0,
                             labels=("Constant",))
