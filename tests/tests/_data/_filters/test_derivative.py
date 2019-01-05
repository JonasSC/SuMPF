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

"""Tests for the DerivativeFilter class"""

import math
import hypothesis
import sumpf
import tests


@hypothesis.given(resolution=tests.strategies.resolutions)
def test_derivative_filter(resolution):
    """Tests if a DerivativeFilter's transfer function increases proportional to ``s = 2pi * f``"""
    filter_ = sumpf.DerivativeFilter()
    transfer_function = filter_.spectrum(resolution=resolution, length=9)
    for f, s in zip(transfer_function.frequency_samples(), transfer_function.channels()[0]):
        assert s == 2.0j * math.pi * f
