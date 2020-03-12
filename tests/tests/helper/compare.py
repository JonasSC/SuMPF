# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2020 Jonas Schulte-Coerne
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

"""Contains helper functions for the comparison of SuMPF's data classes"""

import numpy
import pytest

__all__ = ("compare_signals_approx", "compare_spectrograms_approx")


def fix_nan(array):
    result = array.copy()
    result[~numpy.isfinite(array)] = 2 ** 31
    return result


def compare_signals_approx(signal1, signal2):
    """compares two signals, with using pytest's approx function for the channel comparison"""
    return (signal1.channels() == pytest.approx(signal2.channels()) and
            signal1.sampling_rate() == signal2.sampling_rate() and
            signal1.offset() == signal2.offset() and
            signal1.labels() == signal2.labels())


def compare_spectrograms_approx(spectrogram1, spectrogram2):
    """compares two spectrograms, with using pytest's approx function for the channel comparison.
    It also avoids issues with inf and nan values.
    """
    return (fix_nan(spectrogram1.channels()) == pytest.approx(fix_nan(spectrogram2.channels())) and
            spectrogram1.resolution() == spectrogram2.resolution() and
            spectrogram1.sampling_rate() == spectrogram2.sampling_rate() and
            spectrogram1.offset() == spectrogram2.offset() and
            spectrogram1.labels() == spectrogram2.labels())
