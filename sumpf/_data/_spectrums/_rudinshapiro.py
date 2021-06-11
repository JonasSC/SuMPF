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

"""Contains the :class:`RudinShapiroNoiseSpectrum`-class."""

import numpy
import sumpf._internal as sumpf_internal
from ._spectrum import Spectrum

__all__ = ("RudinShapiroNoiseSpectrum",)


class RudinShapiroNoiseSpectrum(Spectrum):
    """A class for generating the spectrum of a white pseudo noise with a low
    crest factor.

    The noise is generated in the frequency domain by defining the sign (phase)
    of the respective samples according to a Rudin-Shapiro sequence. This procedure
    is well described in the paper "Multitone Signals with Low Crest Factor" by
    Stephen Boyd (IEEE Transactions on circuits and systems, October 1986).
    If the length of the Rudin-Shapiro sequence is a power of two, the crest factor
    of the generated pseudo noise is near its theoretical minimum of 6dB.
    """

    def __init__(self, start_frequency=0.0, stop_frequency=None, resolution=1.0, length=1):
        """
        :param start_frequency: the start frequency in Hz. All frequencies below
                                this will have zero magnitude.
        :param stop_frequency: the stop frequency in Hz or None to take the
                               spectrum's maximum frequency. All frequencies
                               above this will have zero magnitude.
        :param resolution: the resolution of the spectrum as a float
        :param length: the length of the spectrum
        """
        # interpret the start and stop frequency
        offset = min(int(round(start_frequency / resolution)), length)
        if stop_frequency is None:
            sequence_length = length - offset
        else:
            sequence_length = min(int(round(stop_frequency / resolution)), length) - offset
        # generate the channel
        channels = sumpf_internal.allocate_array(shape=(1, length), dtype=numpy.complex128)
        channel = channels[0]
        channel[0:offset] = 0.0
        if offset < length and sequence_length > 0:
            channel[offset] = 1.0
            if offset + 1 < length and sequence_length > 1:
                channel[offset + 1] = 1.0
                i = 2
                while i < sequence_length:
                    j = min(i // 2, sequence_length - i)
                    channel[offset + i:offset + i + j] = channel[offset:offset + j]
                    if i + i // 2 < sequence_length:
                        j = min(i, sequence_length - i)
                        channel[offset + i + i // 2:offset + i + j] = -channel[offset + i // 2:offset + j]
                    i *= 2
        channel[offset + sequence_length:] = 0.0
        # store the parameters
        Spectrum.__init__(self, channels=channels, resolution=resolution, labels=("Noise",))
        self.__sequence_length = sequence_length

    def sequence_length(self):
        """Returns the length of the Rudin-Shapiro-sequence, with which the phase
        of the spectrum has been generated. If this length is a power of two, the
        crest factor of the noise signal is near its theoretical minimum of 6dB.

        :returns: the sequence length as an integer
        """
        return self.__sequence_length
