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

"""Tests the functionality of the Bands class"""

import hypothesis.extra.numpy
import numpy
import pytest
import sumpf
import sumpf._internal as sumpf_internal
import tests


def test_constructor():
    """Tests if the constructor can handle its parameters both for single- and
    for multi-channel bands filter.
    """
    b0 = {100.0: 93.93}
    b1 = [b0]
    b2 = (b0, {150: 44.27, 200:12.8})
    b3 = [b0, b2[1], {250: 473.2}]
    i0 = sumpf.Bands.interpolations.ZERO
    i1 = (i0,)
    i2 = [i0, sumpf.Bands.interpolations.ONE]
    i3 = (i0, i2[1], i2[1])
    assert sumpf.Bands() == sumpf.Bands({}, sumpf.Bands.interpolations.LINEAR, sumpf.Bands.interpolations.STAIRS_LIN, ("Bands",))
    assert sumpf.Bands(b0, i0, i0, ("Bands",)) == sumpf.Bands(bands=b1, interpolations=i1, extrapolations=i1)
    assert sumpf.Bands(b2, i0, i0) == sumpf.Bands(bands=b2, interpolations=(i0, i0), extrapolations=(i0, i0))
    assert sumpf.Bands(b2, i1, i1) == sumpf.Bands(bands=b2, interpolations=(i0, i0), extrapolations=(i0, i0))
    assert sumpf.Bands(b3, i2, i2) == sumpf.Bands(bands=b3, interpolations=i3, extrapolations=i3, labels=("Bands",) * 3)


@hypothesis.given(bands=tests.strategies.bands)
def test_equality_with_filter(bands):
    """Tests if a bands filter is recognized to be equal to a generic filter with
    the same transfer functions.
    """
    filter_ = sumpf.Filter(transfer_functions=bands.transfer_functions(), labels=bands.labels())
    assert filter_ == bands
    assert bands == filter_


@pytest.mark.filterwarnings("ignore:divide by zero")
@hypothesis.given(xs=hypothesis.extra.numpy.arrays(dtype=numpy.float64, shape=2, elements=hypothesis.strategies.floats(min_value=0.0, max_value=1e15), unique=True),
                  ys=hypothesis.extra.numpy.arrays(dtype=numpy.complex128, shape=2, elements=hypothesis.strategies.complex_numbers(min_magnitude=0.0, max_magnitude=1e15)),
                  interpolation=hypothesis.strategies.sampled_from(sumpf.Bands.interpolations),
                  k=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_interpolations(xs, ys, interpolation, k):
    """Tests the functionality of the interpolation functions."""
    xs = sorted(xs)
    bands = sumpf.Bands(bands={x:y for x, y in zip(xs, ys)}, interpolations=interpolation)
    x = xs[0] + k * (xs[1] - xs[0])
    if x == xs[0]:
        assert bands(x)[0] == ys[0]
    elif x == xs[1]:
        assert bands(x)[0] == ys[1]
    else:
        if interpolation is sumpf.Bands.interpolations.ZERO:
            assert bands(x)[0] == 0.0
        elif interpolation is sumpf.Bands.interpolations.ONE:
            assert bands(x)[0] == 1.0
        elif interpolation is sumpf.Bands.interpolations.LINEAR:
            assert bands(x)[0] == pytest.approx(numpy.interp(x, xs, ys))
        elif interpolation is sumpf.Bands.interpolations.LOG_X:
            log_xs = numpy.log2(xs)
            assert bands(x)[0] == pytest.approx(numpy.interp(numpy.log2(x), log_xs, ys), nan_ok=True)
        elif interpolation is sumpf.Bands.interpolations.LOG_Y:
            bands = sumpf.Bands(bands={x:abs(y) for x, y in zip(xs, ys)}, interpolations=interpolation)
            log_ys = numpy.log(numpy.abs(ys))
            assert bands(x)[0] == pytest.approx(numpy.exp(numpy.interp(x, xs, log_ys)), nan_ok=True)
        elif interpolation is sumpf.Bands.interpolations.STAIRS_LIN:
            if k < 0.5:
                assert bands(x)[0] == ys[0]
            else:
                assert bands(x)[0] == ys[1]
        elif interpolation is sumpf.Bands.interpolations.STAIRS_LOG:
            if numpy.log(x) - numpy.log(xs[0]) < numpy.log(xs[1]) - numpy.log(x):
                assert bands(x)[0] == ys[0]
            else:
                assert bands(x)[0] == ys[1]
        else:
            raise ValueError(f"Unknown interpolation: {interpolation}.")


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(xs=hypothesis.extra.numpy.arrays(dtype=numpy.float64, shape=2, elements=hypothesis.strategies.floats(min_value=0.0, max_value=1e12), unique=True),
                  ys=hypothesis.extra.numpy.arrays(dtype=numpy.complex128, shape=2, elements=hypothesis.strategies.complex_numbers(min_magnitude=0.0, max_magnitude=1e15)),
                  extrapolation=hypothesis.strategies.sampled_from(sumpf.Bands.interpolations),
                  delta_x=hypothesis.strategies.floats(min_value=0.0, max_value=1e15))
def test_extrapolations(xs, ys, extrapolation, delta_x):
    """Tests the functionality of the extrapolation functions."""
    xs = sorted(xs)
    assert xs[1] - xs[0]
    bands = sumpf.Bands(bands={x:y for x, y in zip(xs, ys)}, extrapolations=extrapolation)
    if delta_x == 0.0:
        assert bands(xs[0])[0] == ys[0]
        assert bands(xs[1])[0] == ys[1]
    else:
        x0 = xs[0] - delta_x
        x1 = xs[1] + delta_x
        if extrapolation is sumpf.Bands.interpolations.ZERO:
            assert bands(x0)[0] == 0.0
            assert bands(x1)[0] == 0.0
        elif extrapolation is sumpf.Bands.interpolations.ONE:
            assert bands(x0)[0] == 1.0
            assert bands(x1)[0] == 1.0
        elif extrapolation is sumpf.Bands.interpolations.LINEAR:
            m = (ys[1] - ys[0]) / (xs[1] - xs[0])
            n0 = ys[0] - m * xs[0]
            n1 = ys[1] - m * xs[1]
            assert bands(x0)[0] == pytest.approx(m * x0 + n0)
            assert bands(x1)[0] == pytest.approx(m * x1 + n1)
        elif extrapolation is sumpf.Bands.interpolations.LOG_X:
            log_xs = numpy.log2(xs)
            m = (ys[1] - ys[0]) / (log_xs[1] - log_xs[0])
            r0 = m * numpy.log2(x0) + ys[0] - m * log_xs[0]
            r1 = m * numpy.log2(x1) + ys[1] - m * log_xs[1]
            assert (numpy.isnan(bands(x0)[0]) and numpy.isnan(r0)) or (bands(x0)[0] == pytest.approx(r0))
            assert (numpy.isnan(bands(x1)[0]) and numpy.isnan(r1)) or (bands(x1)[0] == pytest.approx(r1))
        elif extrapolation is sumpf.Bands.interpolations.LOG_Y:
            bands = sumpf.Bands(bands={x:abs(y) for x, y in zip(xs, ys)}, extrapolations=extrapolation)
            log_ys = numpy.log2(numpy.abs(ys))
            m = (log_ys[1] - log_ys[0]) / (xs[1] - xs[0])
            n0 = log_ys[0] - m * xs[0]
            n1 = log_ys[1] - m * xs[1]
            assert bands(x0)[0] == pytest.approx(numpy.exp2(m * x0 + n0), nan_ok=True)
            assert bands(x1)[0] == pytest.approx(numpy.exp2(m * x1 + n1), nan_ok=True)
        elif extrapolation is sumpf.Bands.interpolations.STAIRS_LIN:
            assert bands(x0)[0] == ys[0]
            assert bands(x1)[0] == ys[1]
        elif extrapolation is sumpf.Bands.interpolations.STAIRS_LOG:
            assert bands(x0)[0] == ys[0]
            assert bands(x1)[0] == ys[1]
        else:
            raise ValueError(f"Unknown extrapolation: {extrapolation}.")


@pytest.mark.filterwarnings("ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(bands=tests.strategies.bands,
                  reference=hypothesis.strategies.floats(min_value=1e-12, max_value=1e12),
                  factor=hypothesis.strategies.floats(min_value=-1e12, max_value=1e12))
def test_db_conversion(bands, reference, factor):
    """Tests the methods for converting to dB and back."""
    # compare the conversion to dB
    db = bands.to_db(reference=reference, factor=factor)
    assert len(bands) == len(db)
    for t, d in zip(bands.transfer_functions(), db.transfer_functions()):
        assert numpy.array_equal(t.xs, d.xs)
        assert len(t.xs) == len(d.xs) == len(t.ys) == len(d.ys)
        for y1, y2 in zip(t.ys, d.ys):
            if y1 == 0.0:
                assert numpy.isnan(y2)
            else:
                assert y2 == pytest.approx(factor * numpy.log10(y1 / reference))
        assert d.interpolation == t.interpolation
        assert d.extrapolation == t.extrapolation
    assert db.labels() == bands.labels()
    # compare the conversion back to linear
    lin = db.from_db(reference=reference, factor=factor)
    assert len(bands) == len(lin)
    for t, l in zip(bands.transfer_functions(), lin.transfer_functions()):
        assert numpy.array_equal(t.xs, l.xs)
        assert len(t.xs) == len(l.xs) == len(t.ys) == len(l.ys)
        for y1, y2 in zip(t.ys, l.ys):
            if y1 != 0.0 and factor != 0.0:
                assert y2 == pytest.approx(y1)
        assert l.interpolation == t.interpolation
        assert l.extrapolation == t.extrapolation
    assert lin.labels() == bands.labels()
    # test the methods' default parameters and parameter order
    if not any((tf.ys == 0.0).any() for tf in bands.transfer_functions()):
        db2 = bands.to_db()
        assert db2 == bands.to_db(1.0, 20.0)
        assert db2.from_db() == db2.from_db(1.0, 20.0)
        if factor != 0.0:
            assert bands.to_db(reference, factor) == db
            assert db.from_db(reference, factor) == lin
