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

"""Tests for the Chebyshev filter classes"""

import math
import hypothesis
import pytest
import sumpf


@hypothesis.given(cutoff_frequency=hypothesis.strategies.floats(min_value=1e-15, max_value=1e12),
                  order=hypothesis.strategies.integers(min_value=1, max_value=100),
                  ripple=hypothesis.strategies.floats(min_value=0.0, max_value=10.0))
def test_lowpass1_properties(cutoff_frequency, order, ripple):
    """Checks the properties of a Chebyshev Type 1 lowpass"""
    f = sumpf.Chebyshev1Filter(cutoff_frequency=cutoff_frequency,
                               ripple=ripple,
                               order=order,
                               highpass=False)
    # check the parameters
    assert f.cutoff_frequency() == cutoff_frequency
    assert f.order() == order
    assert not f.is_highpass()
    assert f.labels() == ("Chebyshev 1",)
    # check the magnitude at the cutoff frequency
    if ripple == 0.0:   # now the filter is a Butterworth filter
        assert abs(f(cutoff_frequency)[0]) == pytest.approx(0.5 ** 0.5)                         # Butterworth filters have a magnitude of 1/sqrt(2) at the cutoff frequency
    else:
        if order % 2:
            assert abs(f(cutoff_frequency)[0]) == pytest.approx(10 ** (-abs(ripple) / 20.0))    # uneven order filters have the minimum of the ripple at the cutoff frequency
        else:
            assert abs(f(cutoff_frequency)[0]) == pytest.approx(1.0)                            # even order filters have a magnitude of one at the cutoff frequency
    # check the unity gain at zero frequency
    assert f(0.0)[0] == 1.0
    # check the attenuation at a high frequency
    if cutoff_frequency > 1 and ripple > 1:     # for low cutoff frequencies and low ripple, the filter computation is numerically unstable
        margin = 2.0    # a safety margin, so that the filter is evaluated at a higher frequency than that for the computed attenuation
        frequency_factor = 100
        db_attenuation = math.log10(frequency_factor) * 20 * order
        assert abs(f(margin * frequency_factor * cutoff_frequency)[0]) < 10.0 ** (-db_attenuation / 20.0)
    # check the magnitude of the ripple
    if ripple and order % 2 == 0:   # only check for even order filters, since the ripple of uneven order filters is checked with the cutoff frequency
        spectrum = f.spectrum(resolution=cutoff_frequency / 50.0, length=100)
        assert max(spectrum.magnitude()[0]) == pytest.approx(10 ** (abs(ripple) / 20.0), rel=0.005 * order)
    # check the spectrum generation
    spectrum = f.spectrum(resolution=cutoff_frequency / 5.0, length=10)
    assert (spectrum.channels()[0] == f(spectrum.frequency_samples())[0]).all()


@hypothesis.given(cutoff_frequency=hypothesis.strategies.floats(min_value=1e-15, max_value=1e12),
                  order=hypothesis.strategies.integers(min_value=1, max_value=100),
                  ripple=hypothesis.strategies.floats(min_value=0.0, max_value=10.0))
def test_highpass1_properties(cutoff_frequency, order, ripple):
    """Checks the properties of a Chebyshev Type 1 highpass"""
    f = sumpf.Chebyshev1Filter(cutoff_frequency=cutoff_frequency,
                               ripple=ripple,
                               order=order,
                               highpass=True)
    # check the parameters
    assert f.cutoff_frequency() == cutoff_frequency
    assert f.order() == order
    assert f.is_highpass()
    assert f.labels() == ("Chebyshev 1",)
    # check the magnitude at the cutoff frequency
    if ripple == 0.0:   # now the filter is a Butterworth filter
        assert abs(f(cutoff_frequency)[0]) == pytest.approx(0.5 ** 0.5)                        # Butterworth filters have a magnitude of 1/sqrt(2) at the cutoff frequency
    else:
        if order % 2:
            assert abs(f(cutoff_frequency)[0]) == pytest.approx(10 ** (-abs(ripple) / 20.0))    # uneven order filters have the minimum of the ripple at the cutoff frequency
        else:
            assert abs(f(cutoff_frequency)[0]) == pytest.approx(1.0)                            # even order filters have a magnitude of one at the cutoff frequency
    # check the zero gain at zero frequency
    assert f(0.0)[0] == 0.0
    # check the magnitude of the ripple
    if ripple and order % 2 == 0:   # only check for even order filters, since the ripple of uneven order filters is checked with the cutoff frequency
        spectrum = f.spectrum(resolution=cutoff_frequency / 50.0, length=100)
        assert max(spectrum.magnitude()[0]) == pytest.approx(10 ** (abs(ripple) / 20.0), rel=0.005 * order)
    # check the spectrum generation
    spectrum = f.spectrum(resolution=cutoff_frequency / 5.0, length=10)
    assert (spectrum.channels()[0] == f(spectrum.frequency_samples())[0]).all()
