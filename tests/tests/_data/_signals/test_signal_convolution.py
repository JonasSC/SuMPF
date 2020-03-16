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

"""Tests for the convolution and correlation methods of the Signal class"""

import numpy
import hypothesis
import pytest
import sumpf
import tests


@hypothesis.given(signal=tests.strategies.signals(),
                  number=hypothesis.strategies.floats(min_value=-1e100, max_value=1e100),
                  mode=hypothesis.strategies.sampled_from(sumpf.Signal.convolution_modes))
def test_convolve_with_number(signal, number, mode):
    """Tests the convolve method with a number."""
    assert signal.convolve(number, mode) == signal * number


@hypothesis.given(signal1=tests.strategies.signals(),
                  signal2=tests.strategies.signals(),
                  mode=hypothesis.strategies.sampled_from(sumpf.Signal.convolution_modes))
def test_convolve_with_single_channel(signal1, signal2, mode):
    """Tests if the convolution with a single channel signal or a one dimensional
    array is equivalent to the convolution with a signal or array with multiple
    identical channels."""
    signal2 = signal2[0]    # make sure, signal 2 has only one channel
    # test general properties of the convolution with a signal
    signal_convolution = signal1.convolve(signal2, mode=mode)
    assert signal_convolution.sampling_rate() == signal1.sampling_rate()
    assert len(signal_convolution) == len(signal1)
    assert signal_convolution.labels() == ("Convolution",) * len(signal1)
    # test general properties of the convolution with an array
    array_convolution = signal1.convolve(signal2.channels(), mode=mode)
    assert array_convolution.sampling_rate() == signal1.sampling_rate()
    assert len(array_convolution) == len(signal1)
    assert array_convolution.labels() == signal1.labels()
    # compare with the convolution with multiple channels
    multi_array = numpy.empty(shape=(len(signal1), signal2.length()))
    multi_array[:] = signal2.channels()[0]
    assert array_convolution == signal1.convolve(multi_array, mode=mode)
    multi_signal = sumpf.Signal(channels=multi_array,
                                sampling_rate=signal2.sampling_rate(),
                                offset=signal2.offset(),
                                labels=(signal2.labels()[0],) * len(signal1))
    assert signal_convolution == signal1.convolve(multi_signal, mode=mode)


@hypothesis.given(signal1=tests.strategies.signals(),
                  signal2=tests.strategies.signals(),
                  mode=hypothesis.strategies.sampled_from(sumpf.Signal.convolution_modes))
def test_convolve_with_multiple_channels(signal1, signal2, mode):   # pylint: disable=too-many-statements; this function is long, but not too complex
    """Tests the convolution of two multi-channel signals and the convolution of
    a multi-channel signal with a two dimensional array."""
    # make sure, the signals have multiple channels
    signal1 = sumpf.Merge([signal1, signal1]).output()
    signal2 = sumpf.Merge([signal2, signal2]).output()
    number_of_channels = min(len(signal1), len(signal2))
    # test general properties of the convolution with a signal
    signal_convolution = signal1.convolve(signal2, mode=mode)
    assert signal_convolution.sampling_rate() == signal1.sampling_rate()
    assert len(signal_convolution) == number_of_channels
    assert signal_convolution.labels() == ("Convolution",) * len(signal_convolution)
    # test general properties of the convolution with an array
    array_convolution = signal1.convolve(signal2.channels(), mode=mode)
    assert array_convolution.sampling_rate() == signal1.sampling_rate()
    assert len(array_convolution) == number_of_channels
    assert array_convolution.labels() == signal1.labels()[0:len(array_convolution)]
    # test properties, that are specific to the mode
    if mode == sumpf.Signal.convolution_modes.FULL:
        reference = numpy.empty(shape=(number_of_channels, signal1.length() + signal2.length() - 1))
        for r, a, b in zip(reference, signal1.channels(), signal2.channels()):
            r[:] = numpy.convolve(a, b, mode="full")
        assert (signal_convolution.channels() == reference).all()
        assert (array_convolution.channels() == reference).all()
        assert signal_convolution.offset() == signal1.offset() + signal2.offset()
        assert array_convolution.offset() == signal1.offset()
    elif mode == sumpf.Signal.convolution_modes.SAME:
        reference = numpy.empty(shape=(number_of_channels, max(signal1.length(), signal2.length())))
        for r, a, b in zip(reference, signal1.channels(), signal2.channels()):
            r[:] = numpy.convolve(a, b, mode="same")
        o = signal1.offset() + (min(signal1.length(), signal2.length()) - 1) // 2
        assert (signal_convolution.channels() == reference).all()
        assert (array_convolution.channels() == reference).all()
        assert signal_convolution.offset() == o + signal2.offset()
        assert array_convolution.offset() == o
    elif mode == sumpf.Signal.convolution_modes.VALID:
        reference = numpy.empty(shape=(number_of_channels, abs(signal1.length() - signal2.length()) + 1))
        for r, a, b in zip(reference, signal1.channels(), signal2.channels()):
            r[:] = numpy.convolve(a, b, mode="valid")
        o = signal1.offset() + min(signal1.length(), signal2.length()) - 1
        assert (signal_convolution.channels() == reference).all()
        assert (array_convolution.channels() == reference).all()
        assert signal_convolution.offset() == o + signal2.offset()
        assert array_convolution.offset() == o
    elif mode == sumpf.Signal.convolution_modes.SPECTRUM:
        length = max(signal1.length(), signal2.length())
        padded1 = signal1[0:number_of_channels].pad(length if length % 2 == 0 else length + 1)
        padded2 = signal2[0:number_of_channels].pad(length if length % 2 == 0 else length + 1)
        spectrum1 = padded1.shift(None).fourier_transform()
        spectrum2 = padded2.shift(None).fourier_transform()
        reference = (spectrum1 * spectrum2).inverse_fourier_transform()[:, 0:length]
        assert (signal_convolution.channels() == reference.channels()).all()
        assert (array_convolution.channels() == reference.channels()).all()
        assert signal_convolution.offset() == signal1.offset() + signal2.offset()
        assert array_convolution.offset() == signal1.offset()
    elif mode == sumpf.Signal.convolution_modes.SPECTRUM_PADDED:
        length = signal1.length() + signal2.length() - 1
        padded1 = signal1[0:number_of_channels].pad(length + 2 if length % 2 == 0 else length + 1)
        padded2 = signal2[0:number_of_channels].pad(length + 2 if length % 2 == 0 else length + 1)
        spectrum1 = padded1.shift(None).fourier_transform()
        spectrum2 = padded2.shift(None).fourier_transform()
        reference = (spectrum1 * spectrum2).inverse_fourier_transform()[:, 0:length]
        assert (signal_convolution.channels() == reference.channels()).all()
        assert (array_convolution.channels() == reference.channels()).all()
        assert signal_convolution.offset() == signal1.offset() + signal2.offset()
        assert array_convolution.offset() == signal1.offset()
    else:
        raise RuntimeError(f"Unknown mode: {mode}")


@hypothesis.given(length1=hypothesis.strategies.integers(min_value=2, max_value=2 ** 12),   # minimum length of 2, because otherwise, the FFT will fail
                  length2=hypothesis.strategies.integers(min_value=2, max_value=2 ** 12),
                  mode=hypothesis.strategies.sampled_from(sumpf.Signal.convolution_modes))
def test_convolve_offset(length1, length2, mode):
    """Tests if the offset is computed correctly during convolution."""
    for number_of_channels in (1, 2):
        # create test signals with impulses at the zero point in time
        signals = []
        for i, l in enumerate((length1, length2)):
            offset = (l - i) // 2
            channels = numpy.zeros(shape=(number_of_channels, l))
            channels[:, offset] = 1.0
            signal = sumpf.Signal(channels=channels, offset=-offset)
            signals.append(signal)
            assert numpy.argmax(channels[0]) == numpy.argmin(numpy.abs(signal.time_samples()))  # ensure, that the signals have their impulses at the zero point in time
        signal1, signal2 = signals                                                              # pylint: disable=unbalanced-tuple-unpacking
        # test, that the convolution result has its impulse also at the zero point in time
        result = signal1.convolve(other=signal2, mode=mode)
        zero_index = numpy.argmin(numpy.abs(result.time_samples()))
        for i in range(number_of_channels):
            assert numpy.argmax(result.channels()[i]) == zero_index


@hypothesis.given(signal1=tests.strategies.signals(min_value=-1.0, max_value=1.0),
                  signal2=tests.strategies.signals(min_value=-1.0, max_value=1.0))
def test_convolve_spectrum_padded(signal1, signal2):
    """Compares NumPy's full convolution with the frequency domain multiplication of padded signals."""
    padded = signal1.convolve(signal2, mode=sumpf.Signal.convolution_modes.SPECTRUM_PADDED)
    full = signal1.convolve(signal2, mode=sumpf.Signal.convolution_modes.FULL)
    assert padded.channels() == pytest.approx(full.channels())


@hypothesis.given(signal=tests.strategies.signals(),
                  number=hypothesis.strategies.floats(min_value=-1e100, max_value=1e100),
                  mode=hypothesis.strategies.sampled_from(sumpf.Signal.convolution_modes))
def test_correlate_with_number(signal, number, mode):
    """Tests the correlate method with a number."""
    assert signal.correlate(number, mode) == signal * number


@hypothesis.given(signal1=tests.strategies.signals(),
                  signal2=tests.strategies.signals(),
                  mode=hypothesis.strategies.sampled_from(sumpf.Signal.convolution_modes))
def test_correlate_with_single_channel(signal1, signal2, mode):
    """Tests if the correlation with a single channel signal or a one dimensional
    array is equivalent to the correlation with a signal or array with multiple
    identical channels."""
    signal2 = signal2[0]    # make sure, signal 2 has only one channel
    # test general properties of the correlation with a signal
    signal_correlation = signal1.correlate(signal2, mode=mode)
    assert signal_correlation.sampling_rate() == signal1.sampling_rate()
    assert len(signal_correlation) == len(signal1)
    assert signal_correlation.labels() == ("Correlation",) * len(signal1)
    # test general properties of the correlation with an array
    array_correlation = signal1.correlate(signal2.channels(), mode=mode)
    assert array_correlation.sampling_rate() == signal1.sampling_rate()
    assert len(array_correlation) == len(signal1)
    assert array_correlation.labels() == signal1.labels()
    # compare with the correlation with multiple channels
    multi_array = numpy.empty(shape=(len(signal1), signal2.length()))
    multi_array[:] = signal2.channels()[0]
    assert array_correlation == signal1.correlate(multi_array, mode=mode)
    multi_signal = sumpf.Signal(channels=multi_array,
                                sampling_rate=signal2.sampling_rate(),
                                offset=signal2.offset(),
                                labels=(signal2.labels()[0],) * len(signal1))
    assert signal_correlation == signal1.correlate(multi_signal, mode=mode)


@hypothesis.given(signal1=tests.strategies.signals(),
                  signal2=tests.strategies.signals(),
                  mode=hypothesis.strategies.sampled_from(sumpf.Signal.convolution_modes))
def test_correlate_with_multiple_channels(signal1, signal2, mode):  # noqa: C901; this function is long, but not too complex
    # pylint: disable=too-many-branches,too-many-statements,line-too-long
    """Tests the correlation of two multi-channel signals and the correlation of
    a multi-channel signal with a two dimensional array."""
    # make sure, the signals have multiple channels
    signal1 = sumpf.Merge([signal1, signal1]).output()
    signal2 = sumpf.Merge([signal2, signal2]).output()
    number_of_channels = min(len(signal1), len(signal2))
    # test general properties of the correlation with a signal
    signal_correlation = signal1.correlate(signal2, mode=mode)
    assert signal_correlation.sampling_rate() == signal1.sampling_rate()
    assert len(signal_correlation) == number_of_channels
    assert signal_correlation.labels() == ("Correlation",) * len(signal_correlation)
    # test general properties of the correlation with an array
    array_correlation = signal1.correlate(signal2.channels(), mode=mode)
    assert array_correlation.sampling_rate() == signal1.sampling_rate()
    assert len(array_correlation) == number_of_channels
    assert array_correlation.labels() == signal1.labels()[0:len(array_correlation)]
    # test properties, that are specific to the mode
    if mode == sumpf.Signal.convolution_modes.FULL:
        reference = numpy.empty(shape=(number_of_channels, signal1.length() + signal2.length() - 1))
        for r, a, b in zip(reference, signal1.channels(), signal2.channels()):
            r[:] = numpy.correlate(a, b, mode="full")[::-1]
        assert (signal_correlation.channels() == reference).all()
        assert (array_correlation.channels() == reference).all()
        assert signal_correlation.offset() == signal2.offset() - signal1.offset() - signal1.length() + 1
        assert array_correlation.offset() == -signal1.offset() - signal1.length() + 1
    elif mode == sumpf.Signal.convolution_modes.SAME:
        result_length = max(signal1.length(), signal2.length())
        reference = numpy.empty(shape=(number_of_channels, result_length))
        for r, a, b in zip(reference, signal1.channels(), signal2.channels()):
            r[:] = numpy.convolve(a[::-1], b, mode="same")
        o = -signal1.offset() + signal2.length() - result_length - (min(signal1.length(), signal2.length())) // 2
        assert (signal_correlation.channels() == reference).all()
        assert (array_correlation.channels() == reference).all()
        assert signal_correlation.offset() == o + signal2.offset()
        assert array_correlation.offset() == o
    elif mode == sumpf.Signal.convolution_modes.VALID:
        result_length = abs(signal1.length() - signal2.length()) + 1
        reference = numpy.empty(shape=(number_of_channels, result_length))
        for r, a, b in zip(reference, signal1.channels(), signal2.channels()):
            r[:] = numpy.correlate(a, b, mode="valid")[::-1]
        o = -signal1.offset() - (signal1.length() - signal2.length() + result_length) // 2
        assert (signal_correlation.channels() == reference).all()
        assert (array_correlation.channels() == reference).all()
        assert signal_correlation.offset() == o + signal2.offset()
        assert array_correlation.offset() == o
    elif mode == sumpf.Signal.convolution_modes.SPECTRUM:
        length = max(signal1.length(), signal2.length())
        if length % 2 == 1:
            padded_length = length + 1
            padded1 = signal1[0:number_of_channels].shift(padded_length - signal1.length(), sumpf.Signal.shift_modes.PAD)
            padded2 = signal2[0:number_of_channels].pad(padded_length)
        elif signal1.length() < length:
            padded1 = signal1[0:number_of_channels].shift(length - signal1.length(), sumpf.Signal.shift_modes.PAD).shift(1, sumpf.Signal.shift_modes.CYCLE)
            padded2 = signal2[0:number_of_channels]
        elif signal2.length() < length:
            padded1 = signal1[0:number_of_channels]
            padded2 = signal2[0:number_of_channels].pad(length).shift(-1, sumpf.Signal.shift_modes.CYCLE)
        else:
            padded1 = signal1[0:number_of_channels]
            padded2 = signal2[0:number_of_channels].shift(-1, sumpf.Signal.shift_modes.CYCLE)
        spectrum1 = padded1.shift(None).fourier_transform().conjugate()
        spectrum2 = padded2.shift(None).fourier_transform()
        reference = (spectrum1 * spectrum2).inverse_fourier_transform()[:, -length:]
        assert (signal_correlation.channels() == reference.channels()).all()
        assert (array_correlation.channels() == reference.channels()).all()
        assert signal_correlation.offset() == signal2.offset() - signal1.offset() - signal1.length() + 1
        assert array_correlation.offset() == -signal1.offset() - signal1.length() + 1
    elif mode == sumpf.Signal.convolution_modes.SPECTRUM_PADDED:
        length = signal1.length() + signal2.length() - 1
        if length % 2 == 0:
            padded_length = length + 2
            padded1 = signal1[0:number_of_channels].shift(2, sumpf.Signal.shift_modes.PAD).pad(padded_length)
        else:
            padded_length = length + 1
            padded1 = signal1[0:number_of_channels].shift(1, sumpf.Signal.shift_modes.PAD).pad(padded_length)
        padded2 = signal2[0:number_of_channels].shift(padded_length - signal2.length(), sumpf.Signal.shift_modes.PAD)
        spectrum1 = padded1.shift(None).fourier_transform().conjugate()
        spectrum2 = padded2.shift(None).fourier_transform()
        reference = (spectrum1 * spectrum2).inverse_fourier_transform()[:, 0:length]
        assert (signal_correlation.channels() == reference.channels()).all()
        assert (array_correlation.channels() == reference.channels()).all()
        assert signal_correlation.offset() == signal2.offset() - signal1.offset() - signal1.length() + 1
        assert array_correlation.offset() == -signal1.offset() - signal1.length() + 1
    else:
        raise RuntimeError(f"Unknown mode: {mode}")


@hypothesis.given(length1=hypothesis.strategies.integers(min_value=2, max_value=2 ** 12),   # minimum length of 2, because otherwise, the FFT will fail
                  length2=hypothesis.strategies.integers(min_value=2, max_value=2 ** 12),
                  mode=hypothesis.strategies.sampled_from(sumpf.Signal.convolution_modes))
def test_correlate_offset(length1, length2, mode):
    """Tests if the offset is computed correctly during correlation."""
    for number_of_channels in (1, 2):
        # create test signals with impulses at the zero point in time
        signals = []
        for i, l in enumerate((length1, length2)):
            offset = (l - i) // 2
            channels = numpy.zeros(shape=(number_of_channels, l))
            channels[:, offset] = 1.0
            signal = sumpf.Signal(channels=channels, offset=-offset)
            signals.append(signal)
            assert numpy.argmax(channels[0]) == numpy.argmin(numpy.abs(signal.time_samples()))  # ensure, that the signals have their impulses at the zero point in time
        signal1, signal2 = signals                                                              # pylint: disable=unbalanced-tuple-unpacking
        # test, that the correlation result has its impulse also at the zero point in time
        result = signal1.correlate(other=signal2, mode=mode)
        zero_index = numpy.argmin(numpy.abs(result.time_samples()))
        for i in range(number_of_channels):
            peak_index = numpy.argmax(result.channels()[i])
            assert zero_index == peak_index


@hypothesis.given(signal1=tests.strategies.signals(min_value=-1.0, max_value=1.0),
                  signal2=tests.strategies.signals(min_value=-1.0, max_value=1.0))
def test_correlate_spectrum_padded(signal1, signal2):
    """Compares NumPy's full correlation with the frequency domain multiplication of padded signals."""
    padded = signal1.correlate(signal2, mode=sumpf.Signal.convolution_modes.SPECTRUM_PADDED)
    full = signal1.correlate(signal2, mode=sumpf.Signal.convolution_modes.FULL)
    assert padded.channels() == pytest.approx(full.channels())


@hypothesis.given(signal1=tests.strategies.signals(min_value=-10.0, max_value=10.0),
                  signal2=tests.strategies.signals(min_value=-10.0, max_value=10.0),
                  mode=hypothesis.strategies.sampled_from(sumpf.Signal.convolution_modes))
def test_correlation_as_convolution_with_reverse(signal1, signal2, mode):
    """Checks if computing the correlation is equivalent to computing the convolution with the first signal reversed."""
    correlation = signal1.correlate(signal2, mode)
    convolution = reversed(signal1).convolve(signal2, mode)
    assert correlation.channels() == pytest.approx(convolution.channels())
