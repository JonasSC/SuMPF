# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2021 Jonas Schulte-Coerne
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
import math
import hypothesis
import numpy
import pytest
import sumpf
import sumpf._internal as sumpf_internal
import tests

try:
    import scipy
except ImportError:
    scipy = None
else:
    import scipy.signal


def test_bandwidth():
    """Tests the bandwidth of the window functions, for which it is known from literature."""
    bandwidths = {sumpf.RectangularWindow(): 0.8845,
                  sumpf.BartlettWindow(): 1.2736,
                  sumpf.HannWindow(): 1.4382,
                  sumpf.HammingWindow(): 1.3008,
                  sumpf.KaiserWindow(2.0 * math.pi): 1.4270,
                  sumpf.KaiserWindow(2.5 * math.pi): 1.5700,
                  sumpf.KaiserWindow(3.0 * math.pi): 1.7025,
                  sumpf.KaiserWindow(3.5 * math.pi): 1.8262,
                  sumpf.KaiserWindow(4.0 * math.pi): 1.9417,
                  sumpf.KaiserWindow(4.5 * math.pi): 2.0512,
                  sumpf.KaiserWindow(5.0 * math.pi): 2.1553,
                  sumpf.KaiserWindow(5.5 * math.pi): 2.2546,
                  sumpf.KaiserWindow(6.0 * math.pi): 2.3499,
                  sumpf.KaiserWindow(6.5 * math.pi): 2.4414,
                  sumpf.KaiserWindow(7.0 * math.pi): 2.5297}
    if scipy:
        bandwidths.update({sumpf.BlackmanHarrisWindow(): 1.8962,
                           sumpf.NuttallWindow(sumpf.NuttallWindow.functions.NUTTALL3): 1.8496,
                           sumpf.NuttallWindow(sumpf.NuttallWindow.functions.NUTTALL3A): 1.6828,
                           sumpf.NuttallWindow(sumpf.NuttallWindow.functions.NUTTALL3B): 1.6162,
                           sumpf.NuttallWindow(sumpf.NuttallWindow.functions.NUTTALL4): 2.1884,
                           sumpf.NuttallWindow(sumpf.NuttallWindow.functions.NUTTALL4A): 2.0123,
                           sumpf.NuttallWindow(sumpf.NuttallWindow.functions.NUTTALL4B): 1.9122,
                           sumpf.NuttallWindow(sumpf.NuttallWindow.functions.NUTTALL4C): 1.8687,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.SFT3F): 3.1502,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.SFT4F): 3.7618,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.SFT5F): 4.2910,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.SFT3M): 2.9183,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.SFT4M): 3.3451,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.SFT5M): 3.8340,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.FTNI): 2.9355,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.FTHP): 3.3846,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.FTSRS): 3.7274,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT70): 3.3720,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT90D): 3.8320,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT95): 3.7590,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT116D): 4.1579,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT144D): 4.4697,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT169D): 4.7588,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT196D): 5.0308,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT223D): 5.3000,
                           sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT248D): 5.5567})
    for window in bandwidths:
        resolution = window.fourier_transform().resolution()
        bandwidth = bandwidths[window] * resolution
        assert window.bandwidth() == pytest.approx(bandwidth, rel=0.01)
        assert window.bandwidth(oversampling=32) == pytest.approx(bandwidth, rel=0.0025)


def test_scalloping_loss():
    """Tests the scalloping loss of the window functions, for which it is known from literature."""
    scalloping_losses = {sumpf.RectangularWindow(): 3.9224,
                         sumpf.BartlettWindow(): 1.8242,
                         sumpf.HannWindow(): 1.4236,
                         sumpf.HammingWindow(): 1.7514,
                         sumpf.KaiserWindow(2.0 * math.pi): 1.4527,
                         sumpf.KaiserWindow(2.5 * math.pi): 1.2010,
                         sumpf.KaiserWindow(3.0 * math.pi): 1.0226,
                         sumpf.KaiserWindow(3.5 * math.pi): 0.8900,
                         sumpf.KaiserWindow(4.0 * math.pi): 0.7877,
                         sumpf.KaiserWindow(4.5 * math.pi): 0.7064,
                         sumpf.KaiserWindow(5.0 * math.pi): 0.6403,
                         sumpf.KaiserWindow(5.5 * math.pi): 0.5854,
                         sumpf.KaiserWindow(6.0 * math.pi): 0.5392,
                         sumpf.KaiserWindow(6.5 * math.pi): 0.4998,
                         sumpf.KaiserWindow(7.0 * math.pi): 0.4657}
    if scipy:
        scalloping_losses.update({sumpf.BlackmanHarrisWindow(): 0.8256,
                                  sumpf.NuttallWindow(sumpf.NuttallWindow.functions.NUTTALL3): 0.8630,
                                  sumpf.NuttallWindow(sumpf.NuttallWindow.functions.NUTTALL3A): 1.0453,
                                  sumpf.NuttallWindow(sumpf.NuttallWindow.functions.NUTTALL3B): 1.1352,
                                  sumpf.NuttallWindow(sumpf.NuttallWindow.functions.NUTTALL4): 0.6184,
                                  sumpf.NuttallWindow(sumpf.NuttallWindow.functions.NUTTALL4A): 0.7321,
                                  sumpf.NuttallWindow(sumpf.NuttallWindow.functions.NUTTALL4B): 0.8118,
                                  sumpf.NuttallWindow(sumpf.NuttallWindow.functions.NUTTALL4C): 0.8506,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.SFT3F): 0.0082,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.SFT4F): 0.0041,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.SFT5F): 0.0025,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.SFT3M): 0.0115,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.SFT4M): 0.0067,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.SFT5M): 0.0039,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.FTSRS): 0.0156,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT70): 0.0065,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT90D): 0.0039,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT95): 0.0044,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT116D): 0.0028,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT144D): 0.0021,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT169D): 0.0017,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT196D): 0.0013,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT223D): 0.0011,
                                  sumpf.FlatTopWindow(sumpf.FlatTopWindow.functions.HFT248D): 0.0009})
    for window in scalloping_losses:
        linear = 10 ** (-scalloping_losses[window] / 20.0)
        assert window.scalloping_loss() == pytest.approx(linear, rel=1e-4)


def __check_window(window, function, plateau, sampling_rate, length, symmetric, overlap, shape_consistency):
    """A helper function, that tests general features of a window function."""
    __check_metadata(window, sampling_rate, length, symmetric)
    __check_samples(window, function, plateau, length, symmetric)
    __check_sample_range(window, symmetric)
    __check_shape_consistency(window, function, plateau, symmetric, shape_consistency)
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
        return numpy.ones(shape=(1, length))
    else:
        step = length - overlap
        channel = tuple(window.channels()[0])
        matrix = [channel]
        for i in range(step, length, step):
            matrix.append(channel[i:] + (0.0,) * i)
            matrix.append((0.0,) * i + channel[0:-i])
        return numpy.array(matrix, dtype=numpy.float64)


def __check_metadata(window, sampling_rate, length, symmetric):
    """Checks the metadata."""
    assert window.sampling_rate() == sampling_rate
    assert window.length() == length
    assert window.shape() == (1, length)
    assert window.symmetric() == symmetric
    assert window.labels()[0].endswith("window")


def __check_samples(window, function, plateau, length, symmetric):
    """Checks of the window instances samples are equal to those, that are generated with the function."""
    plateau = int(round(plateau * length))
    assert window.plateau() == plateau
    if plateau == 0:
        # check if the signal equals the window function
        if symmetric:
            assert (window.channels()[0] == function(length)).all()
        else:
            assert (window.channels()[0] == function(length + 1)[0:-1]).all()
    else:
        # cut out the plateau and check, that its samples are 1.0
        window_length = 2 * ((length - plateau) // 2)
        plateau_start = window_length // 2
        plateau_stop = length - plateau_start
        assert (window.channels()[0, plateau_start:plateau_stop] == 1.0).all()
        # cut out the fade in and fade out and compare that to the given function
        channel = numpy.empty(window_length)
        channel[0:plateau_start] = window.channels()[0, 0:plateau_start]
        channel[plateau_start:] = window.channels()[0, plateau_stop:]
        if symmetric:
            assert (channel == function(window_length)).all()
        else:
            assert (channel == function(window_length + 1)[0:-1]).all()


def __check_sample_range(window, symmetric):
    """Checks, that the window function does not exceed 1.0"""
    if window.length() > 2:
        length = window.length() + (0 if symmetric else 1)
        if length % 2:
            assert window.channels()[0, length // 2] == pytest.approx(1.0, rel=1e-4)
        else:
            assert window.channels()[0, length // 2] <= 1.0 + 1e-6
        assert min(window.channels()[0]) > -1.0


def __check_shape_consistency(window, function, plateau, symmetric, consistency_constraint):
    """Checks if a window with the same duration, but a different sampling rate has the same shape"""
    length = window.length()
    plateau = int(round(plateau * length))
    window_length = 2 * ((length - plateau) // 2)
    if window_length > 2:
        if length - plateau:
            if plateau == 0:
                channel = window.channels()[0]
            else:
                plateau_start = window_length // 2
                plateau_stop = length - plateau_start
                channel = numpy.empty(window_length)
                channel[0:plateau_start] = window.channels()[0, 0:plateau_start]
                channel[plateau_start:] = window.channels()[0, plateau_stop:]
            if symmetric:
                reference2 = function(len(channel) * 2 - 1)
                reference4 = function(len(channel) * 4 - 3)
                reference8 = function(len(channel) * 8 - 7)
            else:
                reference2 = function(len(channel) * 2 + 1)[0:-2]
                reference4 = function(len(channel) * 4 + 1)[0:-4]
                reference8 = function(len(channel) * 8 + 1)[0:-8]
            if consistency_constraint == "complete":
                assert channel == pytest.approx(reference2[0::2])
                assert channel == pytest.approx(reference4[0::4])
                assert channel == pytest.approx(reference8[0::8])
            elif consistency_constraint == "asymptotic":
                diff12 = max(numpy.abs(channel[1:-1] - reference2[2:-2:2]))
                diff24 = max(numpy.abs(reference2[1:-1] - reference4[2:-2:2]))
                diff48 = max(numpy.abs(reference4[1:-1] - reference8[2:-2:2]))
                assert diff12 < 1.0 / len(channel) or diff24 < diff12
                assert diff24 < 0.1 / len(channel) or diff48 < diff24
            else:
                raise ValueError(f"unknown shape consistency constraint: {consistency_constraint}")


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
        assert window.amplitude_flatness(overlap) == pytest.approx(min(column_sums) / maximum)
    else:
        assert not numpy.isfinite(window.amplitude_flatness(overlap))


def __check_power_flatness(window, overlap, matrix):
    """Checks the power flatness."""
    squared_column_sums = numpy.sum(numpy.square(matrix), axis=0)
    maximum = max(squared_column_sums)
    if maximum != 0.0:
        assert window.power_flatness(overlap) == pytest.approx(min(squared_column_sums) / maximum)
    else:
        assert not numpy.isfinite(window.power_flatness(overlap))


def __check_overlap_correlation(window, overlap):
    """Does trivial checks of the overlap correlation."""
    if numpy.sum(window.channels()[0]) == 0.0:
        assert window.overlap_correlation(0) == 1.0
    else:
        assert window.overlap_correlation(0) == 0.0
    assert window.overlap_correlation(1.0) == 1.0
    if (window.channels() >= 0.0).all():
        assert 0.0 <= round(window.overlap_correlation(overlap), 15) <= 1.0

######################################################
# tests for the window signals, that come with NumPy #
######################################################


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
@hypothesis.settings(deadline=None)
def test_rectangular_window(plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the rectangular window."""
    window = sumpf.RectangularWindow(plateau, sampling_rate, length, symmetric)
    assert window.labels() == ("Rectangular window",)
    __check_window(window=window,
                   function=numpy.ones,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="complete")
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
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
@hypothesis.settings(deadline=None)
def test_bartlett_window(plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the Bartlett window."""
    window = sumpf.BartlettWindow(plateau, sampling_rate, length, symmetric)
    assert window.labels() == ("Bartlett window",)
    __check_window(window=window,
                   function=numpy.bartlett,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="complete")
    if length:
        plateau = int(round(length * plateau))
        assert abs(window.recommended_overlap() - (length - plateau) / 2) <= 1.0


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
@hypothesis.settings(deadline=None)
def test_hann_window(plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the Hann window."""
    window = sumpf.HannWindow(plateau, sampling_rate, length, symmetric)
    assert window.labels() == ("Hann window",)
    __check_window(window=window,
                   function=numpy.hanning,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="complete")
    if length:
        plateau = int(round(length * plateau))
        assert abs(window.recommended_overlap() - (length - plateau) / 2) <= 1.0


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
@hypothesis.settings(deadline=None)
def test_hamming_window(plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the Hamming window."""
    window = sumpf.HammingWindow(plateau, sampling_rate, length, symmetric)
    assert window.labels() == ("Hamming window",)
    __check_window(window=window,
                   function=numpy.hamming,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="complete")
    window_length = 2 * (length - int(round(length * plateau))) // 2
    if window_length:
        threshold = 1.0 + 0.05 * length
        assert abs(window.recommended_overlap() - window_length / 2) <= threshold


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_blackman_window(plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the Blackman window."""
    window = sumpf.BlackmanWindow(plateau, sampling_rate, length, symmetric)
    assert window.labels() == ("Blackman window",)
    __check_window(window=window,
                   function=numpy.blackman,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="complete")


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(beta=hypothesis.strategies.floats(min_value=0.0, max_value=100.0),
                  plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_kaiser_window(beta, plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the Kaiser window."""
    window = sumpf.KaiserWindow(beta, plateau, sampling_rate, length, symmetric)
    assert window.labels() == ("Kaiser window",)
    __check_window(window=window,
                   function=functools.partial(numpy.kaiser, beta=beta),
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="complete")

######################################################
# tests for the window signals, that come with SciPy #
######################################################


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_bartlett_hann_window(plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the Bartlett-Hann window."""
    pytest.importorskip("scipy")
    window = sumpf.BartlettHannWindow(plateau, sampling_rate, length, symmetric)
    assert window.labels() == ("Bartlett-Hann window",)
    __check_window(window=window,
                   function=scipy.signal.windows.barthann,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="complete")


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_blackman_harris_window(plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the Blackman-Harris window."""
    pytest.importorskip("scipy")
    window = sumpf.BlackmanHarrisWindow(plateau, sampling_rate, length, symmetric)
    assert window.labels() == ("Blackman-Harris window",)
    __check_window(window=window,
                   function=scipy.signal.windows.blackmanharris,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="complete")


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_bohman_window(plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the Bohman window."""
    pytest.importorskip("scipy")
    window = sumpf.BohmanWindow(plateau, sampling_rate, length, symmetric)
    assert window.labels() == ("Bohman window",)
    __check_window(window=window,
                   function=scipy.signal.windows.bohman,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="complete")


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(attenuation=hypothesis.strategies.floats(min_value=45.0, max_value=160.0),
                  plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_dolph_chebyshev_window(attenuation, plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the Dolph-Chebyshev window."""
    pytest.importorskip("scipy")
    window = sumpf.DolphChebyshevWindow(attenuation, plateau, sampling_rate, length, symmetric)
    assert window.labels() == ("Dolph-Chebyshev window",)
    __check_window(window=window,
                   function=functools.partial(__dolph_chebyshev_window, attenuation=attenuation),
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="asymptotic")
    # test the attenuation (with a symmetric window without plateau)
    window_length = 2 * (length - int(round(length * plateau))) // 2 + (0 if symmetric else 1)
    if window_length >= 8:
        window = sumpf.DolphChebyshevWindow(attenuation=attenuation,
                                            plateau=0,
                                            sampling_rate=sampling_rate,
                                            length=window_length,
                                            symmetric=True)
        padded = window.pad(2 ** 16)
        spectrum = padded.fourier_transform()
        magnitude = spectrum.magnitude()[0]
        start = int(math.ceil(math.pi * window.bandwidth(32) / spectrum.resolution()))
        side_lobes = magnitude[start:]
        threshold = window.length() / 2.0 * 10.0 ** ((-attenuation + 1.0) / 20.0)   # allow one dB more
        if len(side_lobes):     # pylint: disable=len-as-condition; an empty numpy array is not mapped to False
            assert max(side_lobes) <= threshold


def __dolph_chebyshev_window(length, attenuation):
    if length == 0:
        return numpy.empty(0)
    elif length <= 2:
        return numpy.ones(length)
    else:
        non_normalized = scipy.signal.windows.chebwin(length, at=attenuation)
        return non_normalized / non_normalized[length // 2]


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(decay=hypothesis.strategies.floats(min_value=1.0, max_value=160.0),
                  plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_exponential_window(decay, plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the exponential window."""
    pytest.importorskip("scipy")
    window = sumpf.ExponentialWindow(decay, plateau, sampling_rate, length, symmetric)
    window_length = length - int(round(length * plateau))
    assert window.labels() == ("Exponential window",)
    if window_length == 0 or decay == 0.0:
        function = numpy.ones
    else:

        def function(length):
            return scipy.signal.windows.exponential(length, tau=-10.0 * (length - 1) / (math.log(10) * -decay))

    __check_window(window=window,
                   function=function,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="complete")
    if window_length > 1:
        corner = 10 ** (-decay / 20.0)
        assert window.channels()[0, 0] == pytest.approx(corner)


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(function=hypothesis.strategies.sampled_from(sumpf_internal.FlatTopWindows),
                  plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_flattop_window(function, plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the flat top window."""
    # pylint: disable=line-too-long
    pytest.importorskip("scipy")
    window = sumpf.FlatTopWindow(function, plateau, sampling_rate, length, symmetric)
    assert window.labels() == ("Flat top window",)
    functions = {sumpf.FlatTopWindow.functions.DEFAULT: scipy.signal.windows.flattop,
                 sumpf.FlatTopWindow.functions.SFT3F: functools.partial(__normalized_flat_top_window, a=(0.26526, 0.5, 0.23474)),
                 sumpf.FlatTopWindow.functions.SFT4F: functools.partial(__normalized_flat_top_window, a=(0.21706, 0.42103, 0.28294, 0.07897)),
                 sumpf.FlatTopWindow.functions.SFT5F: functools.partial(__normalized_flat_top_window, a=(0.1881, 0.36923, 0.28702, 0.13077, 0.02488)),
                 sumpf.FlatTopWindow.functions.SFT3M: functools.partial(__normalized_flat_top_window, a=(0.28235, 0.52105, 0.19659)),
                 sumpf.FlatTopWindow.functions.SFT4M: functools.partial(__normalized_flat_top_window, a=(0.241906, 0.460841, 0.255381, 0.041872)),
                 sumpf.FlatTopWindow.functions.SFT5M: functools.partial(__normalized_flat_top_window, a=(0.209671, 0.407331, 0.281225, 0.092669, 0.0091036)),
                 sumpf.FlatTopWindow.functions.FTNI: functools.partial(__normalized_flat_top_window, a=(0.2810639, 0.5208972, 0.1980399)),
                 sumpf.FlatTopWindow.functions.FTHP: functools.partial(__normalized_flat_top_window, a=(1.0, 1.912510941, 1.079173272, 0.1832630879), normalization=4.1749473009),
                 sumpf.FlatTopWindow.functions.FTSRS: functools.partial(__normalized_flat_top_window, a=(1.0, 1.93, 1.29, 0.388, 0.028), normalization=4.635999999999999),
                 sumpf.FlatTopWindow.functions.HFT70: functools.partial(__normalized_flat_top_window, a=(1.0, 1.90796, 1.07349, 0.18199), normalization=4.1634400000000005),
                 sumpf.FlatTopWindow.functions.HFT90D: functools.partial(__normalized_flat_top_window, a=(1.0, 1.942604, 1.340318, 0.440811, 0.043097), normalization=4.766830000000001),
                 sumpf.FlatTopWindow.functions.HFT95: functools.partial(__normalized_flat_top_window, a=(1.0, 1.9383379, 1.3045202, 0.4028270, 0.0350665), normalization=4.680751600000001),
                 sumpf.FlatTopWindow.functions.HFT116D: functools.partial(__normalized_flat_top_window, a=(1.0, 1.9575375, 1.4780705, 0.6367431, 0.1228389, 0.0066288), normalization=5.2018188),
                 sumpf.FlatTopWindow.functions.HFT144D: functools.partial(__normalized_flat_top_window, a=(1.0, 1.96760033, 1.57983607, 0.81123644, 0.22583558, 0.02773848, 0.00090360), normalization=5.6131505),
                 sumpf.FlatTopWindow.functions.HFT169D: functools.partial(__normalized_flat_top_window, a=(1.0, 1.97441842, 1.65409888, 0.95788186, 0.33673420, 0.06364621, 0.00521942, 0.00010599), normalization=5.99210498),
                 sumpf.FlatTopWindow.functions.HFT196D: functools.partial(__normalized_flat_top_window, a=(1.0, 1.979280420, 1.710288951, 1.081629853, 0.448734314, 0.112376628, 0.015122992, 0.000871252, 0.000011896), normalization=6.348316306),
                 sumpf.FlatTopWindow.functions.HFT223D: functools.partial(__normalized_flat_top_window, a=(1.0, 1.98298997309, 1.75556083063, 1.19037717712, 0.56155440797, 0.17296769663, 0.03233247087, 0.00324954578, 0.00013801040, 0.00000132725), normalization=6.69917143974),
                 sumpf.FlatTopWindow.functions.HFT248D: functools.partial(__normalized_flat_top_window, a=(1.0, 1.985844164102, 1.791176438506, 1.282075284005, 0.667777530266, 0.240160796576, 0.056656381764, 0.008134974479, 0.000624544650, 0.000019808998, 0.000000132974), normalization=7.032470056319999)}
    __check_window(window=window,
                   function=functions[function],
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="complete")


def __normalized_flat_top_window(length, a, normalization=1.0):
    return scipy.signal.windows.general_cosine(length, a=a) / normalization


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(standard_deviation=hypothesis.strategies.floats(min_value=0.1, max_value=10.0),
                  plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_gaussian_window(standard_deviation, plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the Gaussian window."""
    pytest.importorskip("scipy")
    window = sumpf.GaussianWindow(standard_deviation, plateau, sampling_rate, length, symmetric)
    assert window.labels() == ("Gaussian window",)
    __check_window(window=window,
                   function=lambda length: scipy.signal.windows.gaussian(length, std=standard_deviation * (length - 1) / 2.0),  # pylint: disable=line-too-long
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="complete")


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(function=hypothesis.strategies.sampled_from(sumpf_internal.NuttallWindows),
                  plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_nuttall_window(function, plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the Nuttall window."""
    # pylint: disable=line-too-long
    pytest.importorskip("scipy")
    window = sumpf.NuttallWindow(function, plateau, sampling_rate, length, symmetric)
    assert window.labels() == ("Nuttall window",)
    functions = {sumpf.NuttallWindow.functions.NUTTALL3: functools.partial(scipy.signal.windows.general_cosine, a=(0.375, 0.5, 0.125)),
                 sumpf.NuttallWindow.functions.NUTTALL3A: functools.partial(scipy.signal.windows.general_cosine, a=(0.40897, 0.5, 0.09103)),
                 sumpf.NuttallWindow.functions.NUTTALL3B: functools.partial(scipy.signal.windows.general_cosine, a=(0.4243801, 0.4973406, 0.0782793)),
                 sumpf.NuttallWindow.functions.NUTTALL4: functools.partial(scipy.signal.windows.general_cosine, a=(0.3125, 0.46875, 0.1875, 0.03125)),
                 sumpf.NuttallWindow.functions.NUTTALL4A: functools.partial(scipy.signal.windows.general_cosine, a=(0.338946, 0.481973, 0.161054, 0.018027)),
                 sumpf.NuttallWindow.functions.NUTTALL4B: functools.partial(scipy.signal.windows.general_cosine, a=(0.355768, 0.487396, 0.144232, 0.012604)),
                 sumpf.NuttallWindow.functions.NUTTALL4C: scipy.signal.windows.nuttall}
    __check_window(window=window,
                   function=functions[function],
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="complete")


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_parzen_window(plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the Parzen window."""
    pytest.importorskip("scipy")
    window = sumpf.ParzenWindow(plateau, sampling_rate, length, symmetric)
    assert window.labels() == ("Parzen window",)
    __check_window(window=window,
                   function=scipy.signal.windows.parzen,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="asymptotic")


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(beta=hypothesis.strategies.floats(min_value=1e-15, max_value=100.0),
                  plateau=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths,
                  symmetric=hypothesis.strategies.booleans(),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=1.0))
def test_slepian_window(beta, plateau, sampling_rate, length, symmetric, overlap):
    """Tests the implementation of the Slepian window."""
    pytest.importorskip("scipy")
    half_window_length = (length - int(round(length * plateau))) // 2
    if 2 * half_window_length + (0 if symmetric else 1) > 2:
        alpha = beta / math.pi
        if alpha >= half_window_length:     # make sure NW is smaller than half the window length
            alpha = 0.99 * (alpha % half_window_length)
            beta = alpha * math.pi
        function = functools.partial(scipy.signal.windows.dpss, NW=beta / math.pi, norm="subsample")    # use beta/pi instead of alpha, so the function is bit-exact the same as that of the SlepianWindow class
    else:
        function = numpy.ones
    window = sumpf.SlepianWindow(beta, plateau, sampling_rate, length, symmetric)
    assert window.labels() == ("Slepian window",)
    __check_window(window=window,
                   function=function,
                   plateau=plateau,
                   sampling_rate=sampling_rate,
                   length=length,
                   symmetric=symmetric,
                   overlap=overlap,
                   shape_consistency="asymptotic")
