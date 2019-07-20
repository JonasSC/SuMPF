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

"""Tests for the MergeSignals class"""

import random
import connectors
import hypothesis
import numpy
import sumpf
import tests


def test_manual():
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
    FIRST_CHANNELS_FIRST = sumpf.MergeSignals.modes.FIRST_CHANNELS_FIRST
    assert sumpf.MergeSignals([signal1, signal2]).output() == signal12
    assert sumpf.MergeSignals([signal2, signal1]).output() == signal21
    assert sumpf.MergeSignals([signal1, signal2], mode=FIRST_CHANNELS_FIRST).output() == signal12
    assert sumpf.MergeSignals([signal2, signal1], mode=FIRST_CHANNELS_FIRST).output() == signal21c


@hypothesis.given(signals=hypothesis.strategies.lists(elements=tests.strategies.signals, min_size=2, max_size=5),
                  index=hypothesis.strategies.integers(min_value=0, max_value=5))
def test_merge_first_signal_first(signals, index):
    """Tests the merging with the FIRST_DATASET_FIRST mode, which is the default."""
    signals = _sanitize_offsets(signals)
    # add a single signal
    merger = sumpf.MergeSignals(signals[0:1])
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


@hypothesis.given(signals=hypothesis.strategies.lists(elements=tests.strategies.signals, min_size=2, max_size=5),
                  index=hypothesis.strategies.integers(min_value=0, max_value=5))
def test_merge_first_channel_first(signals, index):
    """Tests the merging with the FIRST_CHANNEL_FIRST mode."""
    signals = _sanitize_offsets(signals)
    # add a single signal
    merger = sumpf.MergeSignals(signals[0:1], mode=sumpf.MergeSignals.modes.FIRST_CHANNELS_FIRST)
    assert merger.output() == signals[0]
    # merge multiple signals
    signal_ids = [merger.add(s) for s in signals[1:]]
    _compare_merge_first_channel_first(signals=signals,
                                       merged=merger.output())
    # replace one signal
    if index >= len(signal_ids):
        index = index % len(signal_ids)
    signal_id = signal_ids[index]
    merger.replace(signal_id, signals[0])
    _compare_merge_first_channel_first(signals=signals[0:index + 1] + [signals[0]] + signals[index + 2:],
                                       merged=merger.output())
    # remove one signal
    merger.remove(signal_id)
    _compare_merge_first_channel_first(signals=signals[0:index + 1] + signals[index + 2:],
                                       merged=merger.output())


def test_empty():
    """Tests the behavior when no signal is added."""
    assert sumpf.MergeSignals().output() == sumpf.Signal()


@hypothesis.given(signal1=tests.strategies.signals,
                  signal2=tests.strategies.signals,
                  signal3=tests.strategies.signals,
                  signal4=tests.strategies.signals)
def test_connectors(signal1, signal2, signal3, signal4):
    """tests the connector functionality of the MergeSignals class."""
    signal1, signal2, signal3, signal4 = _sanitize_offsets((signal1, signal2, signal3, signal4))    # pylint: disable=unbalanced-tuple-unpacking
    merger = sumpf.MergeSignals([signal1])
    p1 = connectors.blocks.PassThrough().output.connect(merger.add)
    merger.add(signal3)
    p2 = connectors.blocks.PassThrough().input.connect(merger.output)
    p3 = connectors.blocks.PassThrough().output.connect(merger.set_mode)
    for mode in sumpf.MergeSignals.modes:
        p1.input(signal2)
        p3.input(mode)
        assert p2.output() == sumpf.MergeSignals([signal1, signal2, signal3], mode=mode).output()
        p1.input(signal4)
        assert p2.output() == sumpf.MergeSignals([signal1, signal4, signal3], mode=mode).output()


def _sanitize_offsets(signals):
    """makes sure, that the offsets of the signals are not so large, that the
    merged signal requires excessive amounts of memory."""
    first_offset = signals[0].offset()
    r = random.Random()
    r.seed(first_offset)
    # the first signal is returned with its original offset
    result = [signals[0]]
    # the other signal's offset must not differ from the first signal's offset by more than their length
    for s in signals[1:]:
        if abs(first_offset - s.offset()) < s.length():
            result.append(s)
        else:
            result.append(sumpf.Signal(channels=s.channels(),
                                       sampling_rate=s.sampling_rate(),
                                       offset=random.randint(first_offset - s.length(), first_offset + s.length()),
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


def _compare_merge_first_channel_first(signals, merged):
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
                assert merged[c:c + len(signal), start:stop] == signal
                c += 1
            else:
                to_remove.append(s)
        for s in to_remove:
            signals.remove(s)
        d += 1
    assert c == len(merged)
