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

"""Tests for the ConcatenateSignals class"""

import random
import hypothesis
import numpy
import pytest
import sumpf
import tests


def test_empty():
    """Tests the behavior when no data is added."""
    with pytest.raises(RuntimeError):
        sumpf.Concatenate().output()

#####################
# test with signals #
#####################


def test_manually_generated_signals():
    """Tests the concatenation behavior with manually generated signals."""
    signal1 = sumpf.Signal(channels=numpy.array([(1.1, 1.2, 1.3)]),
                           sampling_rate=1.0,
                           offset=1,
                           labels=("s1c1",))
    signal2 = sumpf.Signal(channels=numpy.array([(2.1, 2.2, 2.3, 2.4), (3.1, 3.2, 3.3, 3.4)]),
                           sampling_rate=2.0,
                           offset=-4,
                           labels=("s2c1", "s2c2"))
    signal12 = sumpf.Signal(channels=numpy.array([(2.1, 3.3, 3.5, 3.7), (3.1, 3.2, 3.3, 3.4)]),
                            sampling_rate=1.0,
                            offset=0,
                            labels=("Concatenation 1", "Concatenation 2"))
    signal21 = sumpf.Signal(channels=numpy.array([(2.1, 2.2, 2.3, 2.4, 0.0, 1.1, 1.2, 1.3),
                                                  (3.1, 3.2, 3.3, 3.4, 0.0, 0.0, 0.0, 0.0)]),
                            sampling_rate=2.0,
                            offset=-4,
                            labels=("Concatenation 1", "Concatenation 2"))
    assert tests.compare_signals_approx(_concatenate_signals([signal1, signal2]), signal12)
    assert tests.compare_signals_approx(_concatenate_signals([signal2, signal1]), signal21)
    assert tests.compare_signals_approx(sumpf.Concatenate([signal1, signal2]).output(), signal12)
    assert tests.compare_signals_approx(sumpf.Concatenate([signal2, signal1]).output(), signal21)


@hypothesis.given(signals=hypothesis.strategies.lists(elements=tests.strategies.signals(), min_size=2, max_size=5),
                  index=hypothesis.strategies.integers(min_value=1, max_value=5))
def test_concatenate_signals(signals, index):
    """Tests the concatenation behavior with automatically generated signals."""
    signals = _sanitize_offsets(signals)
    # add a single signal
    concatenate = sumpf.Concatenate(signals[0:1])
    assert concatenate.output() == signals[0]
    # concatenate multiple signals
    signal_ids = [concatenate.add(s) for s in signals[1:]]
    assert tests.compare_signals_approx(concatenate.output(),
                                        _concatenate_signals(signals))
    # replace one signal
    if index > len(signals) - 1:
        index = index % (len(signals) - 1) + 1
    signal_id = signal_ids[index - 1]
    concatenate.replace(signal_id, signals[-1])
    assert tests.compare_signals_approx(concatenate.output(),
                                        _concatenate_signals(signals[0:index] + [signals[-1]] + signals[index + 1:]))
    # remove one signal
    concatenate.remove(signal_id)
    assert tests.compare_signals_approx(concatenate.output(),
                                        _concatenate_signals(signals[0:index] + signals[index + 1:]))


@hypothesis.given(signal1=tests.strategies.signals(),
                  signal2=tests.strategies.signals(),
                  signal3=tests.strategies.signals())
def test_connectors_with_signals(signal1, signal2, signal3):
    """tests the connector functionality of the Concatenate class."""
    signal1, signal2, signal3 = _sanitize_offsets((signal1, signal2, signal3))          # pylint: disable=unbalanced-tuple-unpacking
    concatenate1 = sumpf.Concatenate([signal2])
    concatenate2 = sumpf.Concatenate([signal1]).add.connect(concatenate1.output)
    signal12 = _concatenate_signals([signal1, signal2])
    assert concatenate2.output() == signal12
    signal_id = concatenate1.add(signal3)
    assert tests.compare_signals_approx(concatenate2.output(),
                                        _concatenate_signals([signal1, signal2, signal3]))
    concatenate1.remove(signal_id)
    assert concatenate2.output() == signal12

##########################
# test with spectrograms #
##########################


def test_manually_generated_spectrograms():
    """Tests the concatenation behavior with manually generated spectrograms."""
    spectrogram1 = sumpf.Spectrogram(channels=numpy.array([([1.11, 1.12, 1.13],
                                                            [1.21j, 1.22j, 1.23j],
                                                            [1.31, 1.32, 1.33])]),
                                     resolution=1.0,
                                     sampling_rate=2.0,
                                     offset=1,
                                     labels=("s1c1",))
    spectrogram2 = sumpf.Spectrogram(channels=numpy.array([([2.11, 2.12, 2.13, 2.14],
                                                            [2.21j, 2.22j, 2.23j, 2.24j]),
                                                           ([3.11, 3.12, 3.13, 3.14],
                                                            [3.21j, 3.22j, 3.23j, 3.24j])]),
                                     resolution=3.0,
                                     sampling_rate=4.0,
                                     offset=-4,
                                     labels=("s2c1", "s2c2"))
    spectrogram12 = sumpf.Spectrogram(channels=numpy.array([([2.11, 3.23, 3.25, 3.27],
                                                             [2.21j, 3.43j, 3.45j, 3.47j],
                                                             [0.0, 1.31, 1.32, 1.33]),
                                                            ([3.11, 3.12, 3.13, 3.14],
                                                             [3.21j, 3.22j, 3.23j, 3.24j],
                                                             [0.0, 0.0, 0.0, 0.0])]),
                                      resolution=1.0,
                                      sampling_rate=2.0,
                                      offset=0,
                                      labels=("Concatenation 1", "Concatenation 2"))
    spectrogram21 = sumpf.Spectrogram(channels=numpy.array([([2.11, 2.12, 2.13, 2.14, 0.0, 1.11, 1.12, 1.13],
                                                             [2.21j, 2.22j, 2.23j, 2.24j, 0.0j, 1.21j, 1.22j, 1.23j],
                                                             [0.0, 0.0, 0.0, 0.0, 0.0, 1.31, 1.32, 1.33]),
                                                            ([3.11, 3.12, 3.13, 3.14, 0.0, 0.0, 0.0, 0.0],
                                                             [3.21j, 3.22j, 3.23j, 3.24j, 0.0j, 0.0j, 0.0j, 0.0j],
                                                             [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])]),
                                      resolution=3.0,
                                      sampling_rate=4.0,
                                      offset=-4,
                                      labels=("Concatenation 1", "Concatenation 2"))
    assert tests.compare_spectrograms_approx(_concatenate_spectrograms([spectrogram1, spectrogram2]), spectrogram12)
    assert tests.compare_spectrograms_approx(_concatenate_spectrograms([spectrogram2, spectrogram1]), spectrogram21)
    assert tests.compare_spectrograms_approx(sumpf.Concatenate([spectrogram1, spectrogram2]).output(), spectrogram12)
    assert tests.compare_spectrograms_approx(sumpf.Concatenate([spectrogram2, spectrogram1]).output(), spectrogram21)


@hypothesis.given(spectrograms=hypothesis.strategies.lists(elements=tests.strategies.spectrograms(max_number_of_frequencies=17,  # pylint: disable=line-too-long
                                                                                                  max_length=33),
                                                           min_size=2,
                                                           max_size=5),
                  index=hypothesis.strategies.integers(min_value=1, max_value=5))
def test_concatenate_spectrograms(spectrograms, index):
    """Tests the concatenation behavior with automatically generated spectrograms."""
    spectrograms = _sanitize_offsets(spectrograms)
    # add a single spectrogram
    concatenate = sumpf.Concatenate(spectrograms[0:1])
    assert concatenate.output() == spectrograms[0]
    # concatenate multiple spectrograms
    spectrogram_ids = [concatenate.add(s) for s in spectrograms[1:]]
    assert tests.compare_spectrograms_approx(concatenate.output(),
                                             _concatenate_spectrograms(spectrograms))
    # replace one spectrogram
    if index > len(spectrograms) - 1:
        index = index % (len(spectrograms) - 1) + 1
    spectrogram_id = spectrogram_ids[index - 1]
    concatenate.replace(spectrogram_id, spectrograms[-1])
    assert tests.compare_spectrograms_approx(concatenate.output(),
                                             _concatenate_spectrograms(spectrograms[0:index] +
                                                                       [spectrograms[-1]] +
                                                                       spectrograms[index + 1:]))
    # remove one spectrogram
    concatenate.remove(spectrogram_id)
    assert tests.compare_spectrograms_approx(concatenate.output(),
                                             _concatenate_spectrograms(spectrograms[0:index] +
                                                                       spectrograms[index + 1:]))


@hypothesis.given(spectrogram1=tests.strategies.spectrograms(),
                  spectrogram2=tests.strategies.spectrograms(),
                  spectrogram3=tests.strategies.spectrograms())
def test_connectors(spectrogram1, spectrogram2, spectrogram3):
    """tests the connector functionality of the Concatenate class with spectrograms."""
    spectrogram1, spectrogram2, spectrogram3 = _sanitize_offsets((spectrogram1, spectrogram2, spectrogram3))  # pylint: disable=unbalanced-tuple-unpacking
    concatenate1 = sumpf.Concatenate([spectrogram2])
    concatenate2 = sumpf.Concatenate([spectrogram1]).add.connect(concatenate1.output)
    spectrogram12 = _concatenate_spectrograms([spectrogram1, spectrogram2])
    assert concatenate2.output() == spectrogram12
    spectrogram_id = concatenate1.add(spectrogram3)
    assert concatenate2.output() == _concatenate_spectrograms([spectrogram1, spectrogram2, spectrogram3])
    concatenate1.remove(spectrogram_id)
    assert concatenate2.output() == spectrogram12

####################
# helper functions #
####################


def _sanitize_offsets(data):
    """makes sure, that the offsets of the signals and spectrograms are not so
    large, that the concatenation requires excessive amounts of memory."""
    r = random.Random()
    r.seed(data[0].offset())
    # the first data set is returned with its original offset
    result = [data[0]]
    # the other data sets offset must not exceed their length, so the concatenation is at maximum twice as long as the original data sets combined
    for s in data[1:]:
        if abs(s.offset()) < s.length():
            result.append(s)
        else:
            if isinstance(s, sumpf.Signal):
                result.append(sumpf.Signal(channels=s.channels(),
                                           sampling_rate=s.sampling_rate(),
                                           offset=random.randint(-s.length(), s.length()),
                                           labels=s.labels()))
            else:
                result.append(sumpf.Spectrogram(channels=s.channels(),
                                                resolution=s.resolution(),
                                                sampling_rate=s.sampling_rate(),
                                                offset=random.randint(-s.length(), s.length()),
                                                labels=s.labels()))
    return result


def _concatenate_signals(signals):
    """A simple but inefficient implementation, that concatenates signals by adding them."""
    # test for the corner cases of zero or one signal
    if not signals:
        raise RuntimeError("Nothing to concatenate")
    if len(signals) == 1:
        return signals[0]
    # add the signals
    sum_ = signals[0]
    index = signals[0].length() + signals[0].offset()
    for s in signals[1:]:
        # fill missing channels with zeros
        if len(s) < len(sum_):
            new_channels = numpy.zeros(shape=(len(sum_), s.length()))
            new_channels[0:len(s)] = s.channels()
            s = sumpf.Signal(channels=new_channels, offset=s.offset())
        elif len(sum_) < len(s):
            new_channels = numpy.zeros(shape=(len(s), sum_.length()))
            new_channels[0:len(sum_)] = sum_.channels()
            sum_ = sumpf.Signal(channels=new_channels, offset=sum_.offset())
        sum_ += s.shift(index)
        index += s.length() + s.offset()
    # return a signal with the correct labels
    return sumpf.Signal(channels=sum_.channels(),
                        sampling_rate=signals[0].sampling_rate(),
                        offset=sum_.offset(),
                        labels=tuple(tuple(f"Concatenation {i}" for i in range(1, len(sum_) + 1))))


def _concatenate_spectrograms(spectrograms):
    """A simple but inefficient implementation, that concatenates signals by adding them."""
    # test for the corner cases of zero or one signal
    if not spectrograms:
        raise RuntimeError("Nothing to concatenate")
    if len(spectrograms) == 1:
        return spectrograms[0]
    # add the signals
    sum_ = spectrograms[0]
    index = spectrograms[0].length() + spectrograms[0].offset()
    for s in spectrograms[1:]:
        # fill missing channels with zeros
        if len(s) < len(sum_):
            new_channels = numpy.zeros(shape=(len(sum_), s.number_of_frequencies(), s.length()),
                                       dtype=numpy.complex128)
            new_channels[0:len(s)] = s.channels()
            s = sumpf.Spectrogram(channels=new_channels, offset=s.offset())
        elif len(sum_) < len(s):
            new_channels = numpy.zeros(shape=(len(s), sum_.number_of_frequencies(), sum_.length()),
                                       dtype=numpy.complex128)
            new_channels[0:len(sum_)] = sum_.channels()
            sum_ = sumpf.Spectrogram(channels=new_channels, offset=sum_.offset())
        sum_ += s.shift(index)
        index += s.length() + s.offset()
    # return a signal with the correct labels
    return sumpf.Spectrogram(channels=sum_.channels(),
                             resolution=spectrograms[0].resolution(),
                             sampling_rate=spectrograms[0].sampling_rate(),
                             offset=sum_.offset(),
                             labels=tuple(tuple(f"Concatenation {i}" for i in range(1, len(sum_) + 1))))
