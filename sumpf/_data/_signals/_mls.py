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

"""Contains the :class:`~sumpf.MaximumLengthSequence` class."""

import math
import numpy
import scipy.signal
import sumpf._internal as sumpf_internal
from ._signal import Signal

__all__ = ("MaximumLengthSequence",)


class MaximumLengthSequence(Signal):
    """A class for maximum length sequence signals (MLS).

    Two of the constructor parameters are the ``bits`` and the ``length`` parameter.
    ``bits`` is the size of the shift register, with which the MLS is generated.
    It controls the length of the sequence, which is ``2**bits - 1``. ``length``
    on the other hand controls the length of the signal. These two parameters interact
    in the following way:

    * if both are given and ``length`` is greater than the sequence length, the
      sequence will be repeated until the given length is reached. The last repetition
      may be cropped.
    * if both are given and ``length`` is smaller than the sequence length, the
      sequence will be cropped.
    * if only ``bits`` is given, the signal length will be ``2**bits - 1``.
    * if only ``length`` is given, the sequence length will be equal to the given
      length, if possible. If not, the sequence length will be the smallest one,
      that is larger than the given length.
    """

    def __init__(self, bits=None, seed=None, sampling_rate=48000.0, length=None):
        """
        :param bits: the integer size of the shift register, with which the MLS is generated
        :param seed: a seed for the random initialization of the shift register
        :param sampling_rate: the sampling rate of the MLS as a float
        :param length: the length of the signal
        """
        if length is None:
            if bits is None:
                bits = 16
            length = 2 ** bits - 1
        elif bits is None:
            bits = int(math.ceil(math.log2(length + 1)))
        random = numpy.random.default_rng(seed)
        state = random.choice((False, True), size=bits)
        if True not in state:
            state[random.integers(low=0, high=len(state) - 1)] = True
        sequence = scipy.signal.max_len_seq(bits, state, length)[0]
        channels = sumpf_internal.allocate_array(shape=(1, len(sequence)))
        channels[0, :] = sequence
        channels *= 2.0
        channels -= 1.0
        Signal.__init__(self, channels=channels, sampling_rate=sampling_rate, offset=0, labels=("MLS",))
        self.__bits = bits

    def bits(self):
        """
        Returns the size of the shift register, with which the MLS was generated.

        :returns: an integer
        """
        return self.__bits

    def period_length(self):
        """
        Returns the length of a single repetition of the MLS (``2**bits - 1``).

        :returns: an integer
        """
        return 2 ** self.__bits - 1

    def periods(self):
        """
        Returns the number of repetitions of the MLS in this signal.

        :returns: a float
        """
        return self._length / self.period_length()
