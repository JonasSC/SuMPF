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

"""Tests for the DelayFilter class"""

import hypothesis
import pytest
import sumpf


@hypothesis.given(delay=hypothesis.strategies.floats(min_value=-1e5, max_value=1e5),
                  impulse_shift=hypothesis.strategies.integers(min_value=1, max_value=14))
def test_delay_filter(delay, impulse_shift):
    """Checks the properties of the DelayFilter class by checking its impulse response."""
    # create the filter and compute its impulse response
    filter_ = sumpf.DelayFilter(delay=delay)
    transfer_function = filter_.spectrum(resolution=1.0 if delay == 0.0 else abs(impulse_shift / delay / 16),     # scaling the resolution with the delay and the impulse response's length makes the impulse fall on a single sample of the impulse response
                                         length=9)  # this length leads to an impulse response length of 16
    impulse_response = transfer_function.inverse_fourier_transform()
    # check if the impulse is at the expected index:
    if delay == 0.0:
        impulse_index = 0
    elif delay < 0.0:
        impulse_index = impulse_response.length() - impulse_shift
    else:
        impulse_index = impulse_shift
    for i, s in enumerate(impulse_response.channels()[0]):
        if i == impulse_index:
            assert s == pytest.approx(1.0)
        else:
            assert s == pytest.approx(0.0)
