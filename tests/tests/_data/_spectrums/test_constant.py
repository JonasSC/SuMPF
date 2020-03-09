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

"""Contains tests for the ConstantSpectrum class."""

import hypothesis
import sumpf
import tests


@hypothesis.given(value=hypothesis.strategies.complex_numbers(allow_nan=False, allow_infinity=False),
                  resolution=tests.strategies.resolutions,
                  length=hypothesis.strategies.integers(min_value=0, max_value=2 ** 18))
def test_constant_spectrum(value, resolution, length):
    """tests the ConstantSpectrum class"""
    constant = sumpf.ConstantSpectrum(value, resolution, length)
    assert constant == sumpf.ConstantSpectrum(value=value, resolution=resolution, length=length)
    assert constant.shape() == (1, length)
    assert (constant.channels() == value).all()
    assert constant.resolution() == resolution
