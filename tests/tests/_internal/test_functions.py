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

"""Tests internal functions"""

import hypothesis
import numpy
import sumpf
import sumpf._internal as sumpf_internal
import tests

_windows = (sumpf.RectangularWindow, sumpf.BartlettWindow, sumpf.HannWindow,
            sumpf.HammingWindow, sumpf.BlackmanWindow, sumpf.KaiserWindow)


@hypothesis.given(window_classes=hypothesis.strategies.lists(elements=hypothesis.strategies.sampled_from(_windows), min_size=1),    # pylint: disable=line-too-long
                  plateau=tests.strategies.indices,
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=tests.strategies.indices)
def test_scaling_factor(window_classes, plateau, sampling_rate, length, symmetric, overlap):
    """tests the internal scaling_factor function by comparing it to the
    scaling_factor method of the window signals."""
    overlap = overlap(length)
    windows = [c(plateau=plateau(length),
                 sampling_rate=sampling_rate,
                 length=length,
                 symmetric=symmetric) for c in window_classes]
    signal = sumpf.MergeSignals(windows).output()
    reference = numpy.array([w.scaling_factor(overlap) for w in windows])
    assert numpy.array_equal(sumpf_internal.scaling_factor(signal, overlap), reference)
