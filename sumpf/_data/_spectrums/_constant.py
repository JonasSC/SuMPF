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

"""Contains the :class:`~sumpf.ConstantSpectrum` class."""

import numpy
import sumpf._internal as sumpf_internal
from ._spectrum import Spectrum

__all__ = ("ConstantSpectrum",)


class ConstantSpectrum(Spectrum):
    """A class for generating a spectrum, where each sample has the same constant value."""

    def __init__(self, value=0.0, resolution=1.0, length=1):
        """
        :param value: the complex value of the samples
        :param resolution: the frequency resolution of the spectrum as a float
        :param length: the number of samples of the spectrum
        """
        channels = sumpf_internal.allocate_array(shape=(1, length), dtype=numpy.complex128)
        channels[:] = value
        Spectrum.__init__(self,
                          channels=channels,
                          resolution=resolution,
                          labels=("Constant",))
