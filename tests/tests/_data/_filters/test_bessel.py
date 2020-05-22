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

"""Tests for the BesselFilter class"""

import math
import hypothesis
import pytest
import sumpf


@hypothesis.given(cutoff_frequency=hypothesis.strategies.floats(min_value=1, max_value=1e12),
                  order=hypothesis.strategies.integers(min_value=1, max_value=16))
def test_lowpass_properties(cutoff_frequency, order):
    """Checks the properties of a Bessel lowpass"""
    f = sumpf.BesselFilter(cutoff_frequency=cutoff_frequency,
                           order=order,
                           highpass=False)
    # check the parameters
    assert f.cutoff_frequency() == cutoff_frequency
    assert f.order() == order
    assert not f.is_highpass()
    assert f.labels() == ("Bessel",)
    # check the unity gain at zero frequency
    assert f(0.0)[0] == 1.0
    # check the attenuation of high frequencies
    assert abs(f(cutoff_frequency / 2)[0]) > abs(f(cutoff_frequency)[0]) > abs(f(cutoff_frequency * 2)[0])
    # check the spectrum generation
    spectrum = f.spectrum(resolution=cutoff_frequency / 5.0, length=10)
    assert (spectrum.channels()[0] == f(spectrum.frequency_samples())[0]).all()


@hypothesis.given(cutoff_frequency=hypothesis.strategies.floats(min_value=1e-15, max_value=1e12),
                  order=hypothesis.strategies.integers(min_value=1, max_value=16))
def test_lowpass_with_scipy(cutoff_frequency, order):
    """Compares the Bessel lowpass with that in SciPy"""
    scipy_signal = pytest.importorskip("scipy.signal")
    b, a = scipy_signal.bessel(order, 2 * math.pi * cutoff_frequency, analog=True, btype="lowpass", norm="delay")
    s, h2 = scipy_signal.freqs(b, a)
    f = s / (2 * math.pi)
    c = sumpf.BesselFilter(cutoff_frequency=cutoff_frequency, order=order, highpass=False)
    h1 = c(f)[0]
    assert h1 == pytest.approx(h2)


@hypothesis.given(cutoff_frequency=hypothesis.strategies.floats(min_value=1e-15, max_value=1e12),
                  order=hypothesis.strategies.integers(min_value=1, max_value=16))
def test_highpass_properties(cutoff_frequency, order):
    """Checks the properties of a Bessel highpass"""
    f = sumpf.BesselFilter(cutoff_frequency=cutoff_frequency,
                           order=order,
                           highpass=True)
    # check the parameters
    assert f.cutoff_frequency() == cutoff_frequency
    assert f.order() == order
    assert f.is_highpass()
    assert f.labels() == ("Bessel",)
    # check the zero gain at zero frequency
    assert f(0.0)[0] == 0.0
    # check the attenuation of low frequencies
    assert abs(f(cutoff_frequency / 2)[0]) < abs(f(cutoff_frequency)[0]) < abs(f(cutoff_frequency * 2)[0])
    # check the spectrum generation
    spectrum = f.spectrum(resolution=cutoff_frequency / 5.0, length=10)
    assert (spectrum.channels()[0] == f(spectrum.frequency_samples())[0]).all()


@hypothesis.given(cutoff_frequency=hypothesis.strategies.floats(min_value=1e-15, max_value=1e12),
                  order=hypothesis.strategies.integers(min_value=1, max_value=16))
def test_highpass_with_scipy(cutoff_frequency, order):
    """Compares the Bessel highpass with that in SciPy"""
    scipy_signal = pytest.importorskip("scipy.signal")
    b, a = scipy_signal.bessel(order, 2 * math.pi * cutoff_frequency, analog=True, btype="highpass", norm="delay")
    s, h2 = scipy_signal.freqs(b, a)
    f = s / (2 * math.pi)
    c = sumpf.BesselFilter(cutoff_frequency=cutoff_frequency, order=order, highpass=True)
    h1 = c(f)[0]
    assert h1 == pytest.approx(h2)
