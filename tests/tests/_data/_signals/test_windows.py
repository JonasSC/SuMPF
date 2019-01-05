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

"""Tests for the window function classes"""

import functools
import hypothesis
import numpy
import pytest
import sumpf
import tests


def test_bandwidth():
    """Tests the bandwidth of the window functions, for which it is known from literature."""
    window = sumpf.RectangularWindow()
    resolution = window.fourier_transform().resolution()
    assert window.bandwidth() == pytest.approx(0.8845 * resolution, rel=0.01)
    window = sumpf.BartlettWindow()
    resolution = window.fourier_transform().resolution()
    assert window.bandwidth() == pytest.approx(1.2736 * resolution, rel=0.01)
    window = sumpf.HannWindow()
    resolution = window.fourier_transform().resolution()
    assert window.bandwidth() == pytest.approx(1.4382 * resolution, rel=0.01)
    window = sumpf.HammingWindow()
    resolution = window.fourier_transform().resolution()
    assert window.bandwidth() == pytest.approx(1.3008 * resolution, rel=0.01)
    # test with higher oversampling
    window = sumpf.RectangularWindow()
    resolution = window.fourier_transform().resolution()
    assert window.bandwidth(oversampling=32) == pytest.approx(0.8845 * resolution, rel=0.0025)
    window = sumpf.BartlettWindow()
    resolution = window.fourier_transform().resolution()
    assert window.bandwidth(oversampling=32) == pytest.approx(1.2736 * resolution, rel=0.0025)
    window = sumpf.HannWindow()
    resolution = window.fourier_transform().resolution()
    assert window.bandwidth(oversampling=32) == pytest.approx(1.4382 * resolution, rel=0.0025)
    window = sumpf.HammingWindow()
    resolution = window.fourier_transform().resolution()
    assert window.bandwidth(oversampling=32) == pytest.approx(1.3008 * resolution, rel=0.0025)


def test_scalloping_loss():
    """Tests the scalloping loss of the window functions, for which it is known from literature."""
    window = sumpf.RectangularWindow()
    assert window.scalloping_loss() == pytest.approx(10 ** (-3.9224 / 20.0), rel=0.0001)
    window = sumpf.BartlettWindow()
    assert window.scalloping_loss() == pytest.approx(10 ** (-1.8242 / 20.0), rel=0.0001)
    window = sumpf.HannWindow()
    assert window.scalloping_loss() == pytest.approx(10 ** (-1.4236 / 20.0), rel=0.0001)
    window = sumpf.HammingWindow()
    assert window.scalloping_loss() == pytest.approx(10 ** (-1.7514 / 20.0), rel=0.0001)


def __check_window(window, function, plateau, sampling_rate, length, overlap):
    """A helper function, that tests general features of a window function."""
    __check_metadata(window, sampling_rate, length)
    __check_samples(window, function, plateau, length)
    if length:
        overlap = int(round(overlap * length))
        matrix = __create_shifted_windows_matrix(window, length, overlap)
        __check_scaling_factor(window, length, overlap, matrix)
        __check_amplitude_flatness(window, overlap, matrix)
        __check_power_flatness(window, overlap, matrix)
        __check_overlap_correlation(window, overlap)


def __create_shifted_windows_matrix(window, length, overlap):
    """Computes a matrix with shifted copy of the window on each row."""
    if overlap == length:
        matrix = numpy.ones(shape=(1, length))
    else:
        step = length - overlap
        matrix = numpy.zeros(shape=((2 * length) // step + 1, length))
        i = 0
        for shift in range(0, length, step):
            matrix[i, shift:] = window.channels()[0, 0:length - shift]
            i += 1
            if shift != 0:
                matrix[i, 0:length - shift] = window.channels()[0, shift:]
                i += 1
    return matrix


def __check_metadata(window, sampling_rate, length):
    """Checks the metadata."""
    assert window.sampling_rate() == sampling_rate
    assert window.length() == length
    assert window.shape() == (1, length)
    assert window.labels()[0].endswith("window")


def __check_samples(window, function, plateau, length):
    """Checks of the window instances samples are equal to those, that are generated with the function."""
    plateau = int(round(plateau * length))
    if plateau == 0:
        # check if the signal equals the window function
        assert (window.channels()[0] == function(length)).all()
    else:
        # cut out the plateau and check, that its samples are 1.0
        window_length = 2 * ((length - plateau) // 2)
        plateau_start = window_length // 2
        plateau_stop = length - plateau_start
        assert (window.channels()[0, plateau_start:plateau_stop] == 1.0).all()
        # cut out the fade in and fade out and compare that to the given function
        channels = numpy.empty(window_length)
        channels[0:plateau_start] = window.channels()[0, 0:plateau_start]
        channels[plateau_start:] = window.channels()[0, plateau_stop:]
        assert (channels == function(window_length)).all()


def __check_scaling_factor(window, length, overlap, matrix):
    """Checks the scaling factor."""
    factor = numpy.sum(matrix)
    if factor != 0.0:
        if overlap != length:
            assert window.scaling_factor(overlap) == pytest.approx(length / factor)
        else:
            assert window.scaling_factor(overlap) == 0.0
    else:
        assert not numpy.isfinite(window.scaling_factor(overlap))


def __check_amplitude_flatness(window, overlap, matrix):
    """Checks the amplitude flatness."""
    column_sums = numpy.sum(matrix, axis=0)
    maximum = max(column_sums)
    if maximum != 0.0:
        assert window.amplitude_flatness(overlap) == pytest.approx(min(column_sums) / max(column_sums))
    else:
        assert not numpy.isfinite(window.amplitude_flatness(overlap))


def __check_power_flatness(window, overlap, matrix):
    """Checks the power flatness."""
    squared_column_sums = numpy.sum(numpy.square(matrix), axis=0)
    maximum = max(squared_column_sums)
    if maximum != 0.0:
        assert window.power_flatness(overlap) == pytest.approx(min(squared_column_sums) / max(squared_column_sums))
    else:
        assert not numpy.isfinite(window.power_flatness(overlap))


def __check_overlap_correlation(window, overlap):
    """Does trivial checks of the overlap correlation."""
    if numpy.sum(window.channels()[0]) == 0.0:
        assert window.overlap_correlation(0) == 1.0
    else:
        assert window.overlap_correlation(0) == 0.0
    assert window.overlap_correlation(1.0) == 1.0
    assert 0.0 <= round(window.overlap_correlation(overlap), 15) <= 1.0


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_rectangular_window(plateau, sampling_rate, length, overlap):
    """Tests the implementation of the rectangular window."""
    window = sumpf.RectangularWindow(plateau, sampling_rate, length)
    assert window.labels() == ("Rectangular window",)
    __check_window(window=window,
                   function=numpy.ones,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   overlap=overlap)
    if length:
        if int(round(overlap * length)) == 0:
            assert window.amplitude_flatness(overlap) == 1.0
            assert window.power_flatness(overlap) == 1.0
        elif int(round(overlap * length)) * 2 < length:
            assert window.amplitude_flatness(overlap) == 0.5
            assert window.power_flatness(overlap) == 0.5
        assert window.overlap_correlation(overlap) == int(round(overlap * length)) / length
        assert window.recommended_overlap() == 0


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_bartlett_window(plateau, sampling_rate, length, overlap):
    """Tests the implementation of the Bartlett window."""
    window = sumpf.BartlettWindow(plateau, sampling_rate, length)
    assert window.labels() == ("Bartlett window",)
    __check_window(window=window,
                   function=numpy.bartlett,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   overlap=overlap)
    if length:
        plateau = int(round(length * plateau))
        assert abs(window.recommended_overlap() - (length - plateau) / 2) <= 1.0


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_hann_window(plateau, sampling_rate, length, overlap):
    """Tests the implementation of the Hann window."""
    window = sumpf.HannWindow(plateau, sampling_rate, length)
    assert window.labels() == ("Hann window",)
    __check_window(window=window,
                   function=numpy.hanning,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   overlap=overlap)
    if length:
        plateau = int(round(length * plateau))
        assert abs(window.recommended_overlap() - (length - plateau) / 2) <= 1.0


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_hamming_window(plateau, sampling_rate, length, overlap):
    """Tests the implementation of the Hamming window."""
    window = sumpf.HammingWindow(plateau, sampling_rate, length)
    assert window.labels() == ("Hamming window",)
    __check_window(window=window,
                   function=numpy.hamming,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   overlap=overlap)
    if length:
        plateau = int(round(length * plateau))
        threshold = 1.0
        if threshold % 2:   # for uneven lengths, there is no peak in the amplitude flatness for an overlap of 50%, so predicting the recommended overlap to be 50% can be inaccurate
            threshold += 0.03 * length
        assert abs(window.recommended_overlap() - (length - plateau) / 2) <= threshold


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_blackman_window(plateau, sampling_rate, length, overlap):
    """Tests the implementation of the Blackman window."""
    window = sumpf.BlackmanWindow(plateau, sampling_rate, length)
    assert window.labels() == ("Blackman window",)
    __check_window(window=window,
                   function=numpy.blackman,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   overlap=overlap)


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(beta=hypothesis.strategies.floats(min_value=0.0, max_value=100.0),
                  plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_kaiser_window(beta, plateau, sampling_rate, length, overlap):
    """Tests the implementation of the Kaiser window."""
    window = sumpf.KaiserWindow(beta, plateau, sampling_rate, length)
    assert window.labels() == ("Kaiser window",)
    __check_window(window=window,
                   function=functools.partial(numpy.kaiser, beta=beta),
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   overlap=overlap)
