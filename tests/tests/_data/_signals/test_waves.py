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

"""Contains tests for the sine wave class"""

import math
import hypothesis
import numpy
import pytest
import sumpf
import tests


@hypothesis.given(frequency=tests.strategies.frequencies,
                  phase=hypothesis.strategies.floats(min_value=-2.0 * math.pi, max_value=2.0 * math.pi),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_sine(frequency, phase, sampling_rate, length):
    """Tests the general properties of the sine wave class."""
    sine = sumpf.SineWave(frequency, phase, sampling_rate, length)
    # test the metadata
    assert sine.sampling_rate() == sampling_rate
    assert sine.length() == length
    assert sine.shape() == (1, length)
    assert sine.labels() == ("Sine",)
    # test the periods method
    assert sine.periods() == frequency * sine.duration()
    # test the channels
    if frequency / sampling_rate < 100.0:   # if the ratio is too large, the limited floating point precision can lead to very different result values
        omega = 2.0 * math.pi * frequency
        t = sine.time_samples()
        reference = numpy.sin(omega * t + phase)
        assert sine.channels()[0] == pytest.approx(reference)


@hypothesis.given(frequency=tests.strategies.frequencies,
                  phase=hypothesis.strategies.floats(min_value=-2.0 * math.pi, max_value=2.0 * math.pi),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_cosine(frequency, phase, sampling_rate, length):
    """Tests if the phase term is implemented correctly by comparing the sine wave to a cosine."""
    sine = sumpf.SineWave(frequency, phase + math.pi / 2.0, sampling_rate, length)
    # test the channels
    if frequency / sampling_rate < 100.0:   # if the ratio is too large, the limited floating point precision can lead to very different result values
        omega = 2.0 * math.pi * frequency
        t = sine.time_samples()
        reference = numpy.cos(omega * t + phase)
        assert sine.channels()[0] == pytest.approx(reference)


@hypothesis.given(frequency=tests.strategies.frequencies,
                  phase=hypothesis.strategies.floats(min_value=-2.0 * math.pi, max_value=2.0 * math.pi),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_square_wave(frequency, phase, sampling_rate, length):
    """Tests the general properties of the square wave class."""
    sine = sumpf.SquareWave(frequency, phase, sampling_rate, length)
    # test the metadata
    assert sine.sampling_rate() == sampling_rate
    assert sine.length() == length
    assert sine.shape() == (1, length)
    assert sine.labels() == ("Square wave",)
    # test the periods method
    assert sine.periods() == frequency * sine.duration()
    # test the channels
    if frequency / sampling_rate < 100.0:   # if the ratio is too large, the limited floating point precision can lead to very different result values
        omega = 2.0 * math.pi * frequency
        t = sine.time_samples()
        reference = numpy.sign(numpy.sin(omega * t + phase))
        assert sine.channels()[0] == pytest.approx(reference)
