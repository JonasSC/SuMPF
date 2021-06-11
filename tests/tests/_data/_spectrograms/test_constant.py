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

"""Contains tests for the ConstantSpectrogram class."""

import hypothesis
import sumpf
import tests


@hypothesis.given(value=hypothesis.strategies.complex_numbers(allow_nan=False, allow_infinity=False),
                  resolution=tests.strategies.resolutions,
                  sampling_rate=tests.strategies.sampling_rates,
                  number_of_frequencies=tests.strategies.short_lengths,
                  length=tests.strategies.short_lengths)
def test_constant_spectrogram(value, resolution, sampling_rate, number_of_frequencies, length):
    """tests the ConstantSpectrogram class"""
    constant = sumpf.ConstantSpectrogram(value, resolution, sampling_rate, number_of_frequencies, length)
    assert constant == sumpf.ConstantSpectrogram(value=value,
                                                 resolution=resolution,
                                                 sampling_rate=sampling_rate,
                                                 number_of_frequencies=number_of_frequencies,
                                                 length=length)
    assert constant.shape() == (1, number_of_frequencies, length)
    assert (constant.channels() == value).all()
    assert constant.resolution() == resolution
    assert constant.sampling_rate() == sampling_rate
    assert constant.offset() == 0
