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

"""Tests for the :class:`~sumpf.MaximumLengthSequence` class"""

import math
import hypothesis
import numpy
import pytest
import sumpf
import tests


def test_constructor_defaults():
    """Tests the default values for the length and the bits arguments in the constructor."""
    pytest.importorskip("scipy")
    mls = sumpf.MaximumLengthSequence()
    assert mls.bits() == 16
    assert mls.sampling_rate() == 48000.0
    assert mls.length() == 2 ** 16 - 1
    mls = sumpf.MaximumLengthSequence(length=2 ** 13 - 1)
    assert mls.bits() == 13
    assert mls.sampling_rate() == 48000.0
    assert mls.length() == 2 ** 13 - 1
    mls = sumpf.MaximumLengthSequence(bits=10)
    assert mls.bits() == 10
    assert mls.sampling_rate() == 48000.0
    assert mls.length() == 2 ** 10 - 1


@hypothesis.given(seed=hypothesis.strategies.integers(),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=hypothesis.strategies.integers(min_value=3, max_value=2 ** 16))
def test_default_bits(seed, sampling_rate, length):
    """Tests the determination of the default value for the bits argument of the constructor."""
    pytest.importorskip("scipy")
    mls = sumpf.MaximumLengthSequence(seed=seed, sampling_rate=sampling_rate, length=length)
    bits = int(math.ceil(math.log2(length + 1)))
    reference = sumpf.MaximumLengthSequence(bits=bits, seed=seed, sampling_rate=sampling_rate, length=length)
    assert mls == reference


@hypothesis.given(bits=hypothesis.strategies.integers(min_value=2, max_value=16),
                  seed=hypothesis.strategies.integers(),
                  sampling_rate=tests.strategies.sampling_rates)
def test_seed(bits, seed, sampling_rate):
    """Tests if seeding the initial state of the MLS generator works as expected."""
    pytest.importorskip("scipy")
    length = 2 ** bits - 1
    mls1 = sumpf.MaximumLengthSequence(bits=bits, seed=seed, sampling_rate=sampling_rate, length=length)
    mls2 = sumpf.MaximumLengthSequence(bits, seed, sampling_rate, length)
    mls3 = sumpf.MaximumLengthSequence(bits, seed + 1, sampling_rate, length)
    assert mls1 is not mls2
    assert mls1 == mls2
    hypothesis.assume(mls2 != mls3)     # if all generated MLS with different seeds are the same, this line will make the test fail


@hypothesis.given(bits=hypothesis.strategies.integers(min_value=2, max_value=16),
                  seed=hypothesis.strategies.integers(),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=hypothesis.strategies.integers(min_value=0, max_value=2 ** 16))
def test_properties(bits, seed, sampling_rate, length):
    """Tests the methods for getting of derived parameters."""
    pytest.importorskip("scipy")
    mls = sumpf.MaximumLengthSequence(bits=bits, seed=seed, sampling_rate=sampling_rate, length=length)
    assert mls.bits() == bits
    assert mls.period_length() == 2 ** bits - 1
    assert mls.periods() == mls.length() / mls.period_length()
    assert set(mls.channels().flat) <= {-1.0, 1.0}


@hypothesis.given(bits=hypothesis.strategies.integers(min_value=2, max_value=12),
                  seed=hypothesis.strategies.integers(),
                  sampling_rate=tests.strategies.sampling_rates)
def test_auto_correlation(bits, seed, sampling_rate):
    """Tests if the auto-correlation of the MLS is an impulse."""
    pytest.importorskip("scipy")
    length = 2 ** bits - 1
    mls = sumpf.MaximumLengthSequence(bits=bits, seed=seed, sampling_rate=sampling_rate, length=length)
    spectrum = mls.fourier_transform()
    auto_spectral_density = spectrum * spectrum.conjugate()
    auto_correlation = auto_spectral_density.inverse_fourier_transform()
    correction = 1.0 / (length - 1)
    reference = numpy.empty(length - 1)
    reference[0] = length - correction
    reference[1:] = -1.0 - correction
    assert auto_correlation.channels()[0] == pytest.approx(reference)


@hypothesis.given(bits=hypothesis.strategies.integers(min_value=2, max_value=15),
                  seed=hypothesis.strategies.integers(),
                  sampling_rate=tests.strategies.sampling_rates)
def test_magnitude(bits, seed, sampling_rate):
    """Tests if the magnitude of the MLS' spectrum is constant except for f=0."""
    pytest.importorskip("scipy")
    length = 2 ** bits - 1
    mls = sumpf.MaximumLengthSequence(bits=bits, seed=seed, sampling_rate=sampling_rate, length=length)
    spectrum = mls.fourier_transform()
    reference = numpy.empty(spectrum.length())
    reference[0] = 1.0
    reference[1:] = math.sqrt(2 * spectrum.length())
    assert spectrum.magnitude()[0] == pytest.approx(reference)


@hypothesis.given(bits=hypothesis.strategies.integers(min_value=2, max_value=11),
                  seed=hypothesis.strategies.integers(),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=hypothesis.strategies.integers(min_value=0, max_value=2 ** 16))
def test_periodicity(bits, seed, sampling_rate, length):
    """Tests if a signal with repeated MLS can be generated as expected."""
    pytest.importorskip("scipy")
    mls = sumpf.MaximumLengthSequence(bits=bits, seed=seed, sampling_rate=sampling_rate, length=2 ** bits - 1)
    assert mls.period_length() == mls.length()
    periodic = sumpf.MaximumLengthSequence(bits=bits, seed=seed, sampling_rate=sampling_rate, length=length)
    assert periodic.period_length() == mls.length()
    i = 0
    start = 0
    stop = mls.length()
    while stop <= periodic.length():
        assert (periodic.channels()[:, start:stop] == mls.channels()).all()
        start = stop
        stop += mls.length()
        i += 1
    if start != periodic.length():
        remainder = periodic.length() - start
        if remainder == 1:
            assert periodic.channels()[0, start] == mls.channels()[0, 0]
        else:
            assert (periodic.channels()[0, start:] == mls.channels()[0, 0:remainder]).all()
        assert periodic.periods() == pytest.approx(i + remainder / mls.length())
    else:
        assert periodic.periods() == i
