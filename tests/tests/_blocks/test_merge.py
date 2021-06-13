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

"""Tests for the MergeSignals class"""

import random
import hypothesis
import numpy
import pytest
import connectors
import sumpf
import tests


def test_empty():
    """Tests the behavior when no data is added."""
    with pytest.raises(RuntimeError):
        sumpf.Merge().output()

#####################
# test with signals #
#####################


def test_merge_signals_manually():
    """Tests the merging behavior with manually generated signals."""
    signal1 = sumpf.Signal(channels=numpy.array([(1.1, 1.2, 1.3)]),
                           sampling_rate=1.0,
                           offset=1,
                           labels=("s1c1",))
    signal2 = sumpf.Signal(channels=numpy.array([(2.1, 2.2, 2.3, 2.4), (3.1, 3.2, 3.3, 3.4)]),
                           sampling_rate=2.0,
                           offset=-4,
                           labels=("s2c1", "s2c2"))
    signal12 = sumpf.Signal(channels=numpy.array([(0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.2, 1.3),
                                                  (2.1, 2.2, 2.3, 2.4, 0.0, 0.0, 0.0, 0.0),
                                                  (3.1, 3.2, 3.3, 3.4, 0.0, 0.0, 0.0, 0.0)]),
                            sampling_rate=1.0,
                            offset=-4,
                            labels=("s1c1", "s2c1", "s2c2"))
    signal21 = sumpf.Signal(channels=numpy.array([(2.1, 2.2, 2.3, 2.4, 0.0, 0.0, 0.0, 0.0),
                                                  (3.1, 3.2, 3.3, 3.4, 0.0, 0.0, 0.0, 0.0),
                                                  (0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.2, 1.3)]),
                            sampling_rate=2.0,
                            offset=-4,
                            labels=("s2c1", "s2c2", "s1c1"))
    signal21c = sumpf.Signal(channels=numpy.array([(2.1, 2.2, 2.3, 2.4, 0.0, 0.0, 0.0, 0.0),
                                                   (0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.2, 1.3),
                                                   (3.1, 3.2, 3.3, 3.4, 0.0, 0.0, 0.0, 0.0)]),
                             sampling_rate=2.0,
                             offset=-4,
                             labels=("s2c1", "s1c1", "s2c2"))
    FIRST_CHANNELS_FIRST = sumpf.Merge.modes.FIRST_CHANNELS_FIRST
    assert sumpf.Merge([signal1, signal2]).output() == signal12
    assert sumpf.Merge([signal2, signal1]).output() == signal21
    assert sumpf.Merge([signal1, signal2], mode=FIRST_CHANNELS_FIRST).output() == signal12
    assert sumpf.Merge([signal2, signal1], mode=FIRST_CHANNELS_FIRST).output() == signal21c


@hypothesis.settings(suppress_health_check=(hypothesis.HealthCheck.too_slow,))
@hypothesis.given(signals=hypothesis.strategies.lists(elements=tests.strategies.signals(), min_size=2, max_size=5),
                  index=hypothesis.strategies.integers(min_value=0, max_value=5))
def test_merge_first_signal_first(signals, index):
    """Tests the merging with the FIRST_DATASET_FIRST mode, which is the default."""
    signals = _sanitize_offsets(signals)
    # add a single signal
    merger = sumpf.Merge(signals[0:1])
    assert merger.output() == signals[0]
    # merge multiple signals
    signal_ids = [merger.add(s) for s in signals[1:]]
    _compare_merge_first_signal_first(signals=signals,
                                      merged=merger.output())
    # replace one signal
    if index >= len(signal_ids):
        index = index % len(signal_ids)
    signal_id = signal_ids[index]
    merger.replace(signal_id, signals[0])
    _compare_merge_first_signal_first(signals=signals[0:index + 1] + [signals[0]] + signals[index + 2:],
                                      merged=merger.output())
    # remove one signal
    merger.remove(signal_id)
    _compare_merge_first_signal_first(signals=signals[0:index + 1] + signals[index + 2:],
                                      merged=merger.output())


@hypothesis.settings(suppress_health_check=(hypothesis.HealthCheck.too_slow,))
@hypothesis.given(signals=hypothesis.strategies.lists(elements=tests.strategies.signals(), min_size=2, max_size=5),
                  index=hypothesis.strategies.integers(min_value=0, max_value=5))
def test_merge_signals_first_channel_first(signals, index):
    """Tests the merging with the FIRST_CHANNEL_FIRST mode."""
    signals = _sanitize_offsets(signals)
    # add a single signal
    merger = sumpf.Merge(signals[0:1], mode=sumpf.Merge.modes.FIRST_CHANNELS_FIRST)
    assert merger.output() == signals[0]
    # merge multiple signals
    signal_ids = [merger.add(s) for s in signals[1:]]
    _compare_merge_signals_first_channel_first(signals=signals,
                                               merged=merger.output())
    # replace one signal
    if index >= len(signal_ids):
        index = index % len(signal_ids)
    signal_id = signal_ids[index]
    merger.replace(signal_id, signals[0])
    _compare_merge_signals_first_channel_first(signals=signals[0:index + 1] + [signals[0]] + signals[index + 2:],
                                               merged=merger.output())
    # remove one signal
    merger.remove(signal_id)
    _compare_merge_signals_first_channel_first(signals=signals[0:index + 1] + signals[index + 2:],
                                               merged=merger.output())


@hypothesis.given(signal1=tests.strategies.signals(),
                  signal2=tests.strategies.signals(),
                  signal3=tests.strategies.signals(),
                  signal4=tests.strategies.signals())
def test_connectors_with_signals(signal1, signal2, signal3, signal4):
    """tests the connector functionality of the Merge class."""
    signal1, signal2, signal3, signal4 = _sanitize_offsets((signal1, signal2, signal3, signal4))    # pylint: disable=unbalanced-tuple-unpacking
    merger = sumpf.Merge([signal1])
    p1 = connectors.blocks.PassThrough().output.connect(merger.add)
    merger.add(signal3)
    p2 = connectors.blocks.PassThrough().input.connect(merger.output)
    p3 = connectors.blocks.PassThrough().output.connect(merger.set_mode)
    for mode in sumpf.Merge.modes:
        p1.input(signal2)
        p3.input(mode)
        assert p2.output() == sumpf.Merge([signal1, signal2, signal3], mode=mode).output()
        p1.input(signal4)
        assert p2.output() == sumpf.Merge([signal1, signal4, signal3], mode=mode).output()

#######################
# test with spectrums #
#######################


def test_merge_spectrums_manually():
    """Tests the merging behavior with manually generated spectrums."""
    spectrum1 = sumpf.Spectrum(channels=numpy.array([(1.1j, 1.2, 1.3j)]),
                               resolution=1.0,
                               labels=("s1c1",))
    spectrum2 = sumpf.Spectrum(channels=numpy.array([(2.1, 2.2j, 2.3, 2.4j), (3.1, 3.2j, 3.3, 3.4j)]),
                               resolution=2.0,
                               labels=("s2c1", "s2c2"))
    spectrum12 = sumpf.Spectrum(channels=numpy.array([(1.1j, 1.2, 1.3j, 0.0),
                                                      (2.1, 2.2j, 2.3, 2.4j),
                                                      (3.1, 3.2j, 3.3, 3.4j)]),
                                resolution=1.0,
                                labels=("s1c1", "s2c1", "s2c2"))
    spectrum21 = sumpf.Spectrum(channels=numpy.array([(2.1, 2.2j, 2.3, 2.4j),
                                                      (3.1, 3.2j, 3.3, 3.4j),
                                                      (1.1j, 1.2, 1.3j, 0.0)]),
                                resolution=2.0,
                                labels=("s2c1", "s2c2", "s1c1"))
    spectrum21c = sumpf.Spectrum(channels=numpy.array([(2.1, 2.2j, 2.3, 2.4j),
                                                       (1.1j, 1.2, 1.3j, 0.0),
                                                       (3.1, 3.2j, 3.3, 3.4j)]),
                                 resolution=2.0,
                                 labels=("s2c1", "s1c1", "s2c2"))
    FIRST_CHANNELS_FIRST = sumpf.Merge.modes.FIRST_CHANNELS_FIRST
    assert sumpf.Merge([spectrum1, spectrum2]).output() == spectrum12
    assert sumpf.Merge([spectrum2, spectrum1]).output() == spectrum21
    assert sumpf.Merge([spectrum1, spectrum2], mode=FIRST_CHANNELS_FIRST).output() == spectrum12
    assert sumpf.Merge([spectrum2, spectrum1], mode=FIRST_CHANNELS_FIRST).output() == spectrum21c


@hypothesis.settings(suppress_health_check=(hypothesis.HealthCheck.too_slow,))
@hypothesis.given(spectrums=hypothesis.strategies.lists(elements=tests.strategies.spectrums(), min_size=2, max_size=5),
                  index=hypothesis.strategies.integers(min_value=0, max_value=5))
def test_merge_first_spectrum_first(spectrums, index):
    """Tests the merging with the FIRST_DATASET_FIRST mode, which is the default."""
    # add a single spectrum
    merger = sumpf.Merge(spectrums[0:1])
    assert merger.output() == spectrums[0]
    # merge multiple spectrums
    spectrum_ids = [merger.add(s) for s in spectrums[1:]]
    _compare_merge_first_spectrum_first(spectrums=spectrums,
                                        merged=merger.output())
    # replace one spectrum
    if index >= len(spectrum_ids):
        index = index % len(spectrum_ids)
    spectrum_id = spectrum_ids[index]
    merger.replace(spectrum_id, spectrums[0])
    _compare_merge_first_spectrum_first(spectrums=spectrums[0:index + 1] + [spectrums[0]] + spectrums[index + 2:],
                                        merged=merger.output())
    # remove one spectrum
    merger.remove(spectrum_id)
    _compare_merge_first_spectrum_first(spectrums=spectrums[0:index + 1] + spectrums[index + 2:],
                                        merged=merger.output())


@hypothesis.settings(suppress_health_check=(hypothesis.HealthCheck.too_slow,))
@hypothesis.given(spectrums=hypothesis.strategies.lists(elements=tests.strategies.spectrums(), min_size=2, max_size=5),
                  index=hypothesis.strategies.integers(min_value=0, max_value=5))
def test_merge_spectrums_first_channel_first(spectrums, index):
    """Tests the merging with the FIRST_CHANNEL_FIRST mode."""
    # add a single spectrum
    merger = sumpf.Merge(spectrums[0:1], mode=sumpf.Merge.modes.FIRST_CHANNELS_FIRST)
    assert merger.output() == spectrums[0]
    # merge multiple spectrums
    spectrum_ids = [merger.add(s) for s in spectrums[1:]]
    _compare_merge_spectrums_first_channel_first(spectrums=spectrums,
                                                 merged=merger.output())
    # replace one spectrum
    if index >= len(spectrum_ids):
        index = index % len(spectrum_ids)
    spectrum_id = spectrum_ids[index]
    merger.replace(spectrum_id, spectrums[0])
    _compare_merge_spectrums_first_channel_first(spectrums=(spectrums[0:index + 1] +
                                                            [spectrums[0]] +
                                                            spectrums[index + 2:]),
                                                 merged=merger.output())
    # remove one spectrum
    merger.remove(spectrum_id)
    _compare_merge_spectrums_first_channel_first(spectrums=spectrums[0:index + 1] + spectrums[index + 2:],
                                                 merged=merger.output())


@hypothesis.given(spectrum1=tests.strategies.spectrums(),
                  spectrum2=tests.strategies.spectrums(),
                  spectrum3=tests.strategies.spectrums(),
                  spectrum4=tests.strategies.spectrums())
def test_connectors_with_spectrums(spectrum1, spectrum2, spectrum3, spectrum4):
    """tests the connector functionality of the Merge class."""
    merger = sumpf.Merge([spectrum1])
    p1 = connectors.blocks.PassThrough().output.connect(merger.add)
    merger.add(spectrum3)
    p2 = connectors.blocks.PassThrough().input.connect(merger.output)
    p3 = connectors.blocks.PassThrough().output.connect(merger.set_mode)
    for mode in sumpf.Merge.modes:
        p1.input(spectrum2)
        p3.input(mode)
        assert p2.output() == sumpf.Merge([spectrum1, spectrum2, spectrum3], mode=mode).output()
        p1.input(spectrum4)
        assert p2.output() == sumpf.Merge([spectrum1, spectrum4, spectrum3], mode=mode).output()

##########################
# test with spectrograms #
##########################


def test_merge_spectrograms_manually():
    """Tests the merging behavior with manually generated spectrograms."""
    spectrogram1 = sumpf.Spectrogram(channels=numpy.array([([1.11j, 1.12, 1.13j],
                                                            [1.21j, 1.22, 1.23j],
                                                            [1.31j, 1.32, 1.33j])]),
                                     resolution=1.0,
                                     sampling_rate=2.0,
                                     offset=1,
                                     labels=("s1c1",))
    spectrogram2 = sumpf.Spectrogram(channels=numpy.array([([2.11, 2.12j, 2.13, 2.14j],
                                                            [2.21, 2.22j, 2.23, 2.24j]),
                                                           ([3.11, 3.12j, 3.13, 3.14j],
                                                            [3.21, 3.22j, 3.23, 3.24j])]),
                                     resolution=2.0,
                                     sampling_rate=3.0,
                                     offset=-4,
                                     labels=("s2c1", "s2c2"))
    spectrogram12 = sumpf.Spectrogram(channels=numpy.array([([0.0, 0.0, 0.0, 0.0, 0.0, 1.11j, 1.12, 1.13j],
                                                             [0.0, 0.0, 0.0, 0.0, 0.0, 1.21j, 1.22, 1.23j],
                                                             [0.0, 0.0, 0.0, 0.0, 0.0, 1.31j, 1.32, 1.33j]),
                                                            ([2.11, 2.12j, 2.13, 2.14j, 0.0, 0.0, 0.0, 0.0],
                                                             [2.21, 2.22j, 2.23, 2.24j, 0.0, 0.0, 0.0, 0.0],
                                                             [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
                                                            ([3.11, 3.12j, 3.13, 3.14j, 0.0, 0.0, 0.0, 0.0],
                                                             [3.21, 3.22j, 3.23, 3.24j, 0.0, 0.0, 0.0, 0.0],
                                                             [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])]),
                                      resolution=1.0,
                                      sampling_rate=2.0,
                                      offset=-4,
                                      labels=("s1c1", "s2c1", "s2c2"))
    spectrogram21 = sumpf.Spectrogram(channels=numpy.array([([2.11, 2.12j, 2.13, 2.14j, 0.0, 0.0, 0.0, 0.0],
                                                             [2.21, 2.22j, 2.23, 2.24j, 0.0, 0.0, 0.0, 0.0],
                                                             [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
                                                            ([3.11, 3.12j, 3.13, 3.14j, 0.0, 0.0, 0.0, 0.0],
                                                             [3.21, 3.22j, 3.23, 3.24j, 0.0, 0.0, 0.0, 0.0],
                                                             [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
                                                            ([0.0, 0.0, 0.0, 0.0, 0.0, 1.11j, 1.12, 1.13j],
                                                             [0.0, 0.0, 0.0, 0.0, 0.0, 1.21j, 1.22, 1.23j],
                                                             [0.0, 0.0, 0.0, 0.0, 0.0, 1.31j, 1.32, 1.33j])]),
                                      resolution=2.0,
                                      sampling_rate=3.0,
                                      offset=-4,
                                      labels=("s2c1", "s2c2", "s1c1"))
    spectrogram21c = sumpf.Spectrogram(channels=numpy.array([([2.11, 2.12j, 2.13, 2.14j, 0.0, 0.0, 0.0, 0.0],
                                                              [2.21, 2.22j, 2.23, 2.24j, 0.0, 0.0, 0.0, 0.0],
                                                              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
                                                             ([0.0, 0.0, 0.0, 0.0, 0.0, 1.11j, 1.12, 1.13j],
                                                              [0.0, 0.0, 0.0, 0.0, 0.0, 1.21j, 1.22, 1.23j],
                                                              [0.0, 0.0, 0.0, 0.0, 0.0, 1.31j, 1.32, 1.33j]),
                                                             ([3.11, 3.12j, 3.13, 3.14j, 0.0, 0.0, 0.0, 0.0],
                                                              [3.21, 3.22j, 3.23, 3.24j, 0.0, 0.0, 0.0, 0.0],
                                                              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])]),
                                       resolution=2.0,
                                       sampling_rate=3.0,
                                       offset=-4,
                                       labels=("s2c1", "s1c1", "s2c2"))
    FIRST_CHANNELS_FIRST = sumpf.Merge.modes.FIRST_CHANNELS_FIRST
    assert sumpf.Merge([spectrogram1, spectrogram2]).output() == spectrogram12
    assert sumpf.Merge([spectrogram2, spectrogram1]).output() == spectrogram21
    assert sumpf.Merge([spectrogram1, spectrogram2], mode=FIRST_CHANNELS_FIRST).output() == spectrogram12
    assert sumpf.Merge([spectrogram2, spectrogram1], mode=FIRST_CHANNELS_FIRST).output() == spectrogram21c


@hypothesis.settings(suppress_health_check=(hypothesis.HealthCheck.too_slow,))
@hypothesis.given(spectrograms=hypothesis.strategies.lists(elements=tests.strategies.spectrograms(),
                                                           min_size=2, max_size=5),
                  index=hypothesis.strategies.integers(min_value=0, max_value=5))
def test_merge_first_spectrogram_first(spectrograms, index):
    """Tests the merging with the FIRST_DATASET_FIRST mode, which is the default."""
    spectrograms = _sanitize_offsets(spectrograms)
    # add a single spectrogram
    merger = sumpf.Merge(spectrograms[0:1])
    assert merger.output() == spectrograms[0]
    # merge multiple spectrograms
    spectrogram_ids = [merger.add(s) for s in spectrograms[1:]]
    _compare_merge_first_spectrogram_first(spectrograms=spectrograms,
                                           merged=merger.output())
    # replace one spectrogram
    if index >= len(spectrogram_ids):
        index = index % len(spectrogram_ids)
    spectrogram_id = spectrogram_ids[index]
    merger.replace(spectrogram_id, spectrograms[0])
    _compare_merge_first_spectrogram_first(spectrograms=(spectrograms[0:index + 1] +
                                                         [spectrograms[0]] +
                                                         spectrograms[index + 2:]),
                                           merged=merger.output())
    # remove one spectrogram
    merger.remove(spectrogram_id)
    _compare_merge_first_spectrogram_first(spectrograms=spectrograms[0:index + 1] + spectrograms[index + 2:],
                                           merged=merger.output())


@hypothesis.settings(suppress_health_check=(hypothesis.HealthCheck.too_slow,))
@hypothesis.given(spectrograms=hypothesis.strategies.lists(elements=tests.strategies.spectrograms(),
                                                           min_size=2, max_size=5),
                  index=hypothesis.strategies.integers(min_value=0, max_value=5))
def test_merge_spectrograms_first_channel_first(spectrograms, index):
    """Tests the merging with the FIRST_CHANNEL_FIRST mode."""
    spectrograms = _sanitize_offsets(spectrograms)
    # add a single spectrogram
    merger = sumpf.Merge(spectrograms[0:1], mode=sumpf.Merge.modes.FIRST_CHANNELS_FIRST)
    assert merger.output() == spectrograms[0]
    # merge multiple spectrograms
    spectrogram_ids = [merger.add(s) for s in spectrograms[1:]]
    _compare_merge_spectrograms_first_channel_first(spectrograms=spectrograms,
                                                    merged=merger.output())
    # replace one spectrogram
    if index >= len(spectrogram_ids):
        index = index % len(spectrogram_ids)
    spectrogram_id = spectrogram_ids[index]
    merger.replace(spectrogram_id, spectrograms[0])
    _compare_merge_spectrograms_first_channel_first(spectrograms=(spectrograms[0:index + 1] +
                                                                  [spectrograms[0]] +
                                                                  spectrograms[index + 2:]),
                                                    merged=merger.output())
    # remove one spectrogram
    merger.remove(spectrogram_id)
    _compare_merge_spectrograms_first_channel_first(spectrograms=spectrograms[0:index + 1] + spectrograms[index + 2:],
                                                    merged=merger.output())


@hypothesis.given(spectrogram1=tests.strategies.spectrograms(),
                  spectrogram2=tests.strategies.spectrograms(),
                  spectrogram3=tests.strategies.spectrograms(),
                  spectrogram4=tests.strategies.spectrograms())
def test_connectors_with_spectrograms(spectrogram1, spectrogram2, spectrogram3, spectrogram4):
    """tests the connector functionality of the Merge class."""
    spectrogram1, spectrogram2, spectrogram3, spectrogram4 = _sanitize_offsets((spectrogram1, spectrogram2, spectrogram3, spectrogram4))  # pylint: disable=unbalanced-tuple-unpacking,line-too-long
    merger = sumpf.Merge([spectrogram1])
    p1 = connectors.blocks.PassThrough().output.connect(merger.add)
    merger.add(spectrogram3)
    p2 = connectors.blocks.PassThrough().input.connect(merger.output)
    p3 = connectors.blocks.PassThrough().output.connect(merger.set_mode)
    for mode in sumpf.Merge.modes:
        p1.input(spectrogram2)
        p3.input(mode)
        assert p2.output() == sumpf.Merge([spectrogram1, spectrogram2, spectrogram3], mode=mode).output()
        p1.input(spectrogram4)
        assert p2.output() == sumpf.Merge([spectrogram1, spectrogram4, spectrogram3], mode=mode).output()

##########################
# test with spectrograms #
##########################


def test_merge_filters_manually():
    """Tests the merging behavior with manually generated filters."""
    filter1 = sumpf.Filter(transfer_functions=(sumpf.Filter.Constant(4.9) / sumpf.Filter.Polynomial((0.2, 3.9, 1.1)),),
                           labels=("f1c1",))
    filter2 = sumpf.Filter(transfer_functions=(sumpf.Filter.Exp(12.1), abs(sumpf.Filter.Polynomial((-2.2, 1.2)))),
                           labels=("f2c1", "f2c2"))
    filter12 = sumpf.Filter(transfer_functions=(sumpf.Filter.Constant(4.9) / sumpf.Filter.Polynomial((0.2, 3.9, 1.1)),
                                                sumpf.Filter.Exp(12.1),
                                                abs(sumpf.Filter.Polynomial((-2.2, 1.2)))),
                            labels=("f1c1", "f2c1", "f2c2"))
    filter21 = sumpf.Filter(transfer_functions=(sumpf.Filter.Exp(12.1),
                                                abs(sumpf.Filter.Polynomial((-2.2, 1.2))),
                                                sumpf.Filter.Constant(4.9) / sumpf.Filter.Polynomial((0.2, 3.9, 1.1))),
                            labels=("f2c1", "f2c2", "f1c1"))
    filter21c = sumpf.Filter(transfer_functions=(sumpf.Filter.Exp(12.1),
                                                 sumpf.Filter.Constant(4.9) / sumpf.Filter.Polynomial((0.2, 3.9, 1.1)),
                                                 abs(sumpf.Filter.Polynomial((-2.2, 1.2)))),
                             labels=("f2c1", "f1c1", "f2c2"))
    FIRST_CHANNELS_FIRST = sumpf.Merge.modes.FIRST_CHANNELS_FIRST
    assert sumpf.Merge([filter1, filter2]).output() == filter12
    assert sumpf.Merge([filter2, filter1]).output() == filter21
    assert sumpf.Merge([filter1, filter2], mode=FIRST_CHANNELS_FIRST).output() == filter12
    assert sumpf.Merge([filter2, filter1], mode=FIRST_CHANNELS_FIRST).output() == filter21c


@hypothesis.settings(suppress_health_check=(hypothesis.HealthCheck.too_slow,))
@hypothesis.given(filters=hypothesis.strategies.lists(elements=tests.strategies.filters(), min_size=2, max_size=5),
                  index=hypothesis.strategies.integers(min_value=0, max_value=5))
def test_merge_first_filter_first(filters, index):
    """Tests the merging with the FIRST_DATASET_FIRST mode, which is the default."""
    # add a single filter
    merger = sumpf.Merge(filters[0:1])
    assert merger.output() == filters[0]
    # merge multiple filters
    filter_ids = [merger.add(s) for s in filters[1:]]
    _compare_merge_first_filter_first(filters=filters,
                                      merged=merger.output())
    # replace one filter
    if index >= len(filter_ids):
        index = index % len(filter_ids)
    filter_id = filter_ids[index]
    merger.replace(filter_id, filters[0])
    _compare_merge_first_filter_first(filters=filters[0:index + 1] + [filters[0]] + filters[index + 2:],
                                      merged=merger.output())
    # remove one filter
    merger.remove(filter_id)
    _compare_merge_first_filter_first(filters=filters[0:index + 1] + filters[index + 2:],
                                      merged=merger.output())


@hypothesis.settings(suppress_health_check=(hypothesis.HealthCheck.too_slow,))
@hypothesis.given(filters=hypothesis.strategies.lists(elements=tests.strategies.filters(), min_size=2, max_size=5),
                  index=hypothesis.strategies.integers(min_value=0, max_value=5))
def test_merge_filter_first_channel_first(filters, index):
    """Tests the merging with the FIRST_CHANNEL_FIRST mode."""
    # add a single filter
    merger = sumpf.Merge(filters[0:1], mode=sumpf.Merge.modes.FIRST_CHANNELS_FIRST)
    assert merger.output() == filters[0]
    # merge multiple filter
    filter_ids = [merger.add(s) for s in filters[1:]]
    _compare_merge_filters_first_channel_first(filters=filters,
                                               merged=merger.output())
    # replace one filter
    if index >= len(filter_ids):
        index = index % len(filter_ids)
    filter_id = filter_ids[index]
    merger.replace(filter_id, filters[0])
    _compare_merge_filters_first_channel_first(filters=filters[0:index + 1] + [filters[0]] + filters[index + 2:],
                                               merged=merger.output())
    # remove one filter
    merger.remove(filter_id)
    _compare_merge_filters_first_channel_first(filters=filters[0:index + 1] + filters[index + 2:],
                                               merged=merger.output())


@hypothesis.given(filter1=tests.strategies.filters(),
                  filter2=tests.strategies.filters(),
                  filter3=tests.strategies.filters(),
                  filter4=tests.strategies.filters())
def test_connectors_with_filters(filter1, filter2, filter3, filter4):
    """tests the connector functionality of the Merge class."""
    merger = sumpf.Merge([filter1])
    p1 = connectors.blocks.PassThrough().output.connect(merger.add)
    merger.add(filter3)
    p2 = connectors.blocks.PassThrough().input.connect(merger.output)
    p3 = connectors.blocks.PassThrough().output.connect(merger.set_mode)
    for mode in sumpf.Merge.modes:
        p1.input(filter2)
        p3.input(mode)
        assert p2.output() == sumpf.Merge([filter1, filter2, filter3], mode=mode).output()
        p1.input(filter4)
        assert p2.output() == sumpf.Merge([filter1, filter4, filter3], mode=mode).output()

##################################
# helper functions for the tests #
##################################


def _sanitize_offsets(data):
    """makes sure, that the offsets of the signals and spectrograms are not so
    large, that the  merged signal requires excessive amounts of memory."""
    first_offset = data[0].offset()
    r = random.Random()
    r.seed(first_offset)
    # the first signal is returned with its original offset
    result = [data[0]]
    # the other signal's offset must not differ from the first signal's offset by more than their length
    for s in data[1:]:
        if abs(first_offset - s.offset()) < s.length():
            result.append(s)
        else:
            if isinstance(s, sumpf.Signal):
                result.append(sumpf.Signal(channels=s.channels(),
                                           sampling_rate=s.sampling_rate(),
                                           offset=random.randint(first_offset - s.length(),
                                                                 first_offset + s.length()),
                                           labels=s.labels()))
            else:  # s must be a spectrogram
                result.append(sumpf.Spectrogram(channels=s.channels(),
                                                resolution=s.resolution(),
                                                sampling_rate=s.sampling_rate(),
                                                offset=random.randint(first_offset - s.length(),
                                                                      first_offset + s.length()),
                                                labels=s.labels()))
    return result


def _compare_merge_first_signal_first(signals, merged):
    """tests if the merged signal's channels are ordered like the input signals"""
    c = 0
    sampling_rate = signals[0].sampling_rate()
    for s in signals:
        signal = sumpf.Signal(channels=s.channels(),
                              sampling_rate=sampling_rate,  # take the sampling rate from the first signal
                              offset=s.offset(),
                              labels=s.labels())            # the merged signal has a label for each channel, which could be empty
        start = signal.offset() - merged.offset()
        stop = start + signal.length()
        assert merged[c:c + len(signal), start:stop] == signal
        c += len(signal)
    assert c == len(merged)


def _compare_merge_signals_first_channel_first(signals, merged):
    """test if the merged signal's channels are ordered in a way that the first
    channels of all input signals come first"""
    sampling_rate = signals[0].sampling_rate()
    signals = list(signals)
    c = 0
    d = 0
    while signals:
        to_remove = []
        for s in signals:
            if d < len(s):
                signal = sumpf.Signal(channels=s[d].channels(),
                                      sampling_rate=sampling_rate,  # take the sampling rate from the first signal
                                      offset=s[d].offset(),
                                      labels=s[d].labels())         # the merged signal has a label for each channel, which could be empty
                start = signal.offset() - merged.offset()
                stop = start + signal.length()
                assert merged[c, start:stop] == signal
                c += 1
            else:
                to_remove.append(s)
        for s in to_remove:
            signals.remove(s)
        d += 1
    assert c == len(merged)


def _compare_merge_first_spectrum_first(spectrums, merged):
    """tests if the merged spectrum's channels are ordered like the input spectrums"""
    c = 0
    resolution = spectrums[0].resolution()
    for s in spectrums:
        spectrum = sumpf.Spectrum(channels=s.channels(),
                                  resolution=resolution,    # take the resolution from the first spectrum
                                  labels=s.labels())        # the merged spectrum has a label for each channel, which could be empty
        stop = s.length()
        assert merged[c:c + len(spectrum), 0:stop] == spectrum
        c += len(spectrum)
    assert c == len(merged)


def _compare_merge_spectrums_first_channel_first(spectrums, merged):
    """test if the merged spectrum's channels are ordered in a way that the first
    channels of all input spectrum come first"""
    resolution = spectrums[0].resolution()
    spectrums = list(spectrums)
    c = 0
    d = 0
    while spectrums:
        to_remove = []
        for s in spectrums:
            if d < len(s):
                spectrum = sumpf.Spectrum(channels=s[d].channels(),
                                          resolution=resolution,    # take the resolution from the first spectrum
                                          labels=s[d].labels())     # the merged spectrum has a label for each channel, which could be empty
                stop = spectrum.length()
                assert merged[c, 0:stop] == spectrum
                c += 1
            else:
                to_remove.append(s)
        for s in to_remove:
            spectrums.remove(s)
        d += 1
    assert c == len(merged)


def _compare_merge_first_spectrogram_first(spectrograms, merged):
    """tests if the merged spectrogram's channels are ordered like the input spectrograms"""
    c = 0
    resolution = spectrograms[0].resolution()
    sampling_rate = spectrograms[0].sampling_rate()
    for s in spectrograms:
        spectrogram = sumpf.Spectrogram(channels=s.channels(),
                                        resolution=resolution,        # take the resolution from the first spectrogram
                                        sampling_rate=sampling_rate,  # take the sampling rate from the first spectrogram
                                        offset=s.offset(),
                                        labels=s.labels())            # the merged spectrogram has a label for each channel, which could be empty
        start = spectrogram.offset() - merged.offset()
        stop = start + spectrogram.length()
        max_f = s.number_of_frequencies()
        assert merged[c:c + len(spectrogram), 0:max_f, start:stop] == spectrogram
        c += len(spectrogram)
    assert c == len(merged)


def _compare_merge_spectrograms_first_channel_first(spectrograms, merged):
    """test if the merged spectrogram's channels are ordered in a way that the first
    channels of all input spectrogram come first"""
    resolution = spectrograms[0].resolution()
    sampling_rate = spectrograms[0].sampling_rate()
    spectrograms = list(spectrograms)
    c = 0
    d = 0
    while spectrograms:
        to_remove = []
        for s in spectrograms:
            if d < len(s):
                spectrogram = sumpf.Spectrogram(channels=s[d].channels(),
                                                resolution=resolution,        # take the resolution from the first spectrogram
                                                sampling_rate=sampling_rate,  # take the sampling rate from the first spectrogram
                                                offset=s[d].offset(),
                                                labels=s[d].labels())            # the merged spectrogram has a label for each channel, which could be empty
                start = spectrogram.offset() - merged.offset()
                stop = start + spectrogram.length()
                max_f = spectrogram.number_of_frequencies()
                assert merged[c, 0:max_f, start:stop] == spectrogram
                c += 1
            else:
                to_remove.append(s)
        for s in to_remove:
            spectrograms.remove(s)
        d += 1
    assert c == len(merged)


def _compare_merge_first_filter_first(filters, merged):
    """tests if the merged filter's channels are ordered like the input filters"""
    c = 0
    for f in filters:
        assert merged[c:c + len(f)] == f
        c += len(f)
    assert c == len(merged)


def _compare_merge_filters_first_channel_first(filters, merged):
    """test if the merged filter's channels are ordered in a way that the first
    channels of all input filter come first"""
    filters = list(filters)
    c = 0
    d = 0
    while filters:
        to_remove = []
        for f in filters:
            if d < len(f):
                assert merged[c] == f[d]
                c += 1
            else:
                to_remove.append(f)
        for s in to_remove:
            filters.remove(s)
        d += 1
    assert c == len(merged)
