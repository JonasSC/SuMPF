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

"""Tests the interpolation functions"""

import hypothesis.extra.numpy
import numpy
import pytest
import sumpf._internal as sumpf_internal


def xs_ys(data, interpolation):
    """A helper function, that creates arrays of x and y values from the data pairs,
    that have been created by hypothesis.
    """
    if data:
        xs, ys = map(numpy.array, zip(*sorted(data)))
    else:
        xs = numpy.empty(0)
        ys = numpy.empty(0)
    if interpolation in (sumpf_internal.Interpolations.LOG_X, sumpf_internal.Interpolations.STAIRS_LOG):
        if (xs <= 0).any():
            xs -= xs.min()
            xs += 1e-15
    elif interpolation is sumpf_internal.Interpolations.LOG_Y:
        ys = numpy.abs(ys) + 1e-15
    return xs, ys


@hypothesis.given(interpolation=hypothesis.strategies.sampled_from(sumpf_internal.Interpolations),
                  data=hypothesis.strategies.lists(elements=hypothesis.strategies.tuples(hypothesis.strategies.floats(min_value=-1e15, max_value=1e15),                     # pylint: disable=line-too-long
                                                                                         hypothesis.strategies.complex_numbers(min_magnitude=0.0, max_magnitude=1e15)),     # pylint: disable=line-too-long
                                                   min_size=0, max_size=2 ** 12,
                                                   unique_by=lambda t: t[0]))
def test_supporting_points(interpolation, data):
    """Tests if the interpolation at a supporting point is exactly the given y value"""
    func = sumpf_internal.interpolation.get(interpolation)
    xs, ys = xs_ys(data, interpolation)
    assert (func(xs, xs, ys) == ys).all()


@hypothesis.given(interpolation=hypothesis.strategies.sampled_from(sumpf_internal.Interpolations),
                  data=hypothesis.strategies.lists(elements=hypothesis.strategies.tuples(hypothesis.strategies.floats(min_value=-1e15, max_value=1e15),                     # pylint: disable=line-too-long
                                                                                         hypothesis.strategies.complex_numbers(min_magnitude=0.0, max_magnitude=1e15)),     # pylint: disable=line-too-long
                                                   min_size=1, max_size=2 ** 12,
                                                   unique_by=lambda t: t[0]),
                  x=hypothesis.strategies.lists(elements=hypothesis.strategies.floats(min_value=-1e15, max_value=1e15), min_size=0, max_size=2 ** 12))                      # pylint: disable=line-too-long
def test_x_as_scalar_and_vector(interpolation, data, x):
    """Tests if running a vectorized interpolation returns the same result as the scalar version."""
    func = sumpf_internal.interpolation.get(interpolation)
    xs, ys = xs_ys(data, interpolation)
    x = numpy.array(x)
    if interpolation in (sumpf_internal.Interpolations.LOG_X, sumpf_internal.Interpolations.STAIRS_LOG):
        if (x <= 0).any():
            x -= x.min()
            x += 1e-15
    scalar = [func(s, xs, ys) for s in x]
    vector = list(func(x, xs, ys))
    assert scalar == pytest.approx(vector)


@pytest.mark.filterwarnings("ignore:divide by zero")    # noqa: C901; the method is not complex, it's just a long switch case
@hypothesis.given(interpolation=hypothesis.strategies.sampled_from(sumpf_internal.Interpolations),
                  xs=hypothesis.extra.numpy.arrays(dtype=numpy.float64, shape=2, elements=hypothesis.strategies.floats(min_value=-1e15, max_value=1e15), unique=True),          # pylint: disable=line-too-long
                  ys=hypothesis.extra.numpy.arrays(dtype=numpy.complex128, shape=2, elements=hypothesis.strategies.complex_numbers(min_magnitude=0.0, max_magnitude=1e15)),     # pylint: disable=line-too-long
                  k=hypothesis.strategies.floats(min_value=1e-15, max_value=1.0 - 1e-15))
def test_interpolation(interpolation, xs, ys, k):       # pylint: disable=too-many-branches
    """Tests the computation of an interpolated value."""
    func = sumpf_internal.interpolation.get(interpolation)
    xs = numpy.array(sorted(xs))
    if interpolation in (sumpf_internal.Interpolations.LOG_X, sumpf_internal.Interpolations.STAIRS_LOG) and min(xs) < 0.0:  # pylint: disable=line-too-long
        xs -= min(xs)
    elif interpolation is sumpf_internal.Interpolations.LOG_Y:
        ys = numpy.abs(ys)
    x = xs[0] + k * (xs[1] - xs[0])
    hypothesis.assume(x not in xs)  # due to the limited precision of floating point numbers, this can still happen
    if interpolation is sumpf_internal.Interpolations.ZERO:
        assert func(x, xs, ys) == 0.0
    elif interpolation is sumpf_internal.Interpolations.ONE:
        assert func(x, xs, ys) == 1.0
    elif interpolation is sumpf_internal.Interpolations.LINEAR:
        assert func(x, xs, ys) == pytest.approx(numpy.interp(x, xs, ys))
    elif interpolation is sumpf_internal.Interpolations.LOG_X:
        log_xs = numpy.log2(xs)
        if 0.0 in xs and numpy.log2(x) not in log_xs:
            assert numpy.isnan(func(x, xs, ys))
        else:
            assert func(x, xs, ys) == pytest.approx(numpy.interp(numpy.log2(x), log_xs, ys))
    elif interpolation is sumpf_internal.Interpolations.LOG_Y:
        if ys[0] == 0.0:
            assert numpy.isnan(func(x, xs, ys))
        elif ys[1] == 0.0:
            assert func(x, xs, ys) == 0.0
        else:
            log_ys = numpy.log(numpy.abs(ys))
            assert func(x, xs, ys) == pytest.approx(numpy.exp(numpy.interp(x, xs, log_ys)))
    elif interpolation is sumpf_internal.Interpolations.STAIRS_LIN:
        if k < 0.5:
            assert func(x, xs, ys) == ys[0]
        else:
            assert func(x, xs, ys) == ys[1]
    elif interpolation is sumpf_internal.Interpolations.STAIRS_LOG:
        if numpy.log(x) - numpy.log(xs[0]) < numpy.log(xs[1]) - numpy.log(x):
            assert func(x, xs, ys) == ys[0]
        else:
            assert func(x, xs, ys) == ys[1]
    else:
        raise ValueError(f"Unknown interpolation: {interpolation}.")


@pytest.mark.filterwarnings("ignore:divide by zero encountered in log", "ignore:invalid value encountered", "ignore:overflow encountered in exp")                               # pylint: disable=line-too-long
@hypothesis.given(xs=hypothesis.extra.numpy.arrays(dtype=numpy.float64, shape=2, elements=hypothesis.strategies.floats(min_value=0.0, max_value=1e12), unique=True),            # pylint: disable=line-too-long
                  ys=hypothesis.extra.numpy.arrays(dtype=numpy.complex128, shape=2, elements=hypothesis.strategies.complex_numbers(min_magnitude=0.0, max_magnitude=1e15)),     # pylint: disable=line-too-long
                  interpolation=hypothesis.strategies.sampled_from(sumpf_internal.Interpolations),
                  delta_x=hypothesis.strategies.floats(min_value=1e-15, max_value=1e15))
def test_extrapolation(xs, ys, interpolation, delta_x):
    """Tests the computation of an extrapolated value."""
    func = sumpf_internal.interpolation.get(interpolation)
    xs = numpy.array(sorted(xs))
    if interpolation in (sumpf_internal.Interpolations.LOG_X, sumpf_internal.Interpolations.STAIRS_LOG) and min(xs) < 0.0:  # pylint: disable=line-too-long
        xs -= min(xs)
    elif interpolation is sumpf_internal.Interpolations.LOG_Y:
        ys = numpy.abs(ys)
    x0 = xs[0] * (1.0 - delta_x) - delta_x
    x1 = xs[1] * (1.0 + delta_x) + delta_x
    if interpolation is sumpf_internal.Interpolations.ZERO:
        assert func(x0, xs, ys) == 0.0
        assert func(x1, xs, ys) == 0.0
    elif interpolation is sumpf_internal.Interpolations.ONE:
        assert func(x0, xs, ys) == 1.0
        assert func(x1, xs, ys) == 1.0
    elif interpolation is sumpf_internal.Interpolations.LINEAR:
        m = (ys[1] - ys[0]) / (xs[1] - xs[0])
        n0 = ys[0] - m * xs[0]
        n1 = ys[1] - m * xs[1]
        assert func(x0, xs, ys) == pytest.approx(m * x0 + n0)
        assert func(x1, xs, ys) == pytest.approx(m * x1 + n1)
    elif interpolation is sumpf_internal.Interpolations.LOG_X:
        log_xs = numpy.log2(xs)
        m = (ys[1] - ys[0]) / (log_xs[1] - log_xs[0])
        r0 = m * numpy.log2(x0) + ys[0] - m * log_xs[0]
        r1 = m * numpy.log2(x1) + ys[1] - m * log_xs[1]
        assert (numpy.isnan(func(x0, xs, ys)) and numpy.isnan(r0)) or (func(x0, xs, ys) == pytest.approx(r0))
        assert (numpy.isnan(func(x1, xs, ys)) and numpy.isnan(r1)) or (func(x1, xs, ys) == pytest.approx(r1))
    elif interpolation is sumpf_internal.Interpolations.LOG_Y:
        if 0.0 in ys:
            assert numpy.isnan(func(x0, xs, ys))
            assert numpy.isnan(func(x1, xs, ys))
        else:
            log_ys = numpy.log2(ys)
            m = (log_ys[1] - log_ys[0]) / (xs[1] - xs[0])
            n0 = log_ys[0] - m * xs[0]
            n1 = log_ys[1] - m * xs[1]
            assert func(x0, xs, ys) == pytest.approx(numpy.exp2(m * x0 + n0))
            assert func(x1, xs, ys) == pytest.approx(numpy.exp2(m * x1 + n1))
    elif interpolation is sumpf_internal.Interpolations.STAIRS_LIN:
        assert func(x0, xs, ys) == ys[0]
        assert func(x1, xs, ys) == ys[1]
    elif interpolation is sumpf_internal.Interpolations.STAIRS_LOG:
        assert func(x0, xs, ys) == ys[0]
        assert func(x1, xs, ys) == ys[1]
    else:
        raise ValueError(f"Unknown interpolation: {interpolation}.")
