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

import pytest

__all__ = ("compare_signals_approx",)


def compare_signals_approx(signal1, signal2):
    """compares two signals, with using pytest's approx function for the channel comparison"""
    return (signal1.channels() == pytest.approx(signal2.channels()) and
            signal1.sampling_rate() == signal2.sampling_rate() and
            signal1.offset() == signal2.offset() and
            signal1.labels() == signal2.labels())
