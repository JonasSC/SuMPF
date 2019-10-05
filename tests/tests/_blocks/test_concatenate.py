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

"""Tests for the ConcatenateSignals class"""

import random
import hypothesis
import numpy
import sumpf
import tests


def test_manual():
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
    assert tests.compare_signals_approx(sumpf.ConcatenateSignals([signal1, signal2]).output(), signal12)
    assert tests.compare_signals_approx(sumpf.ConcatenateSignals([signal2, signal1]).output(), signal21)


@hypothesis.given(signals=hypothesis.strategies.lists(elements=tests.strategies.signals(), min_size=2, max_size=5),
                  index=hypothesis.strategies.integers(min_value=1, max_value=5))
def test_concatenate_signals(signals, index):
    """Tests the concatenation behavior with automatically generated signals."""
    signals = _sanitize_offsets(signals)
    # add a single signal
    concatenate = sumpf.ConcatenateSignals(signals[0:1])
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


def test_empty():
    """Tests the behavior when no signal is added."""
    assert sumpf.ConcatenateSignals().output() == sumpf.Signal()


@hypothesis.given(signal1=tests.strategies.signals(),
                  signal2=tests.strategies.signals(),
                  signal3=tests.strategies.signals())
def test_connectors(signal1, signal2, signal3):
    """tests the connector functionality of the ConcatenateSignals class."""
    signal1, signal2, signal3 = _sanitize_offsets((signal1, signal2, signal3))          # pylint: disable=unbalanced-tuple-unpacking
    concatenate1 = sumpf.ConcatenateSignals([signal2])
    concatenate2 = sumpf.ConcatenateSignals([signal1]).add.connect(concatenate1.output)
    signal12 = _concatenate_signals([signal1, signal2])
    assert concatenate2.output() == signal12
    signal_id = concatenate1.add(signal3)
    assert concatenate2.output() == _concatenate_signals([signal1, signal2, signal3])
    concatenate1.remove(signal_id)
    assert concatenate2.output() == signal12


def _concatenate_signals(signals):
    """A simple but inefficient implementation, that concatenates signals by adding them."""
    # test for the corner cases of zero or one signal
    if len(signals) == 0:       # pylint: disable=len-as-condition
        return sumpf.Signal()
    elif len(signals) == 1:
        return signals[0]
    # add the signals
    sum_ = signals[0]
    index = signals[0].length() + signals[0].offset()
    for s in signals[1:]:
        # fill missing channels with zeros
        if len(s) < len(sum_):
            new_channels = numpy.zeros(shape=(len(sum_), s.length()))
            new_channels[0:len(s), :] = s.channels()
            s = sumpf.Signal(channels=new_channels, offset=s.offset())
        elif len(sum_) < len(s):
            new_channels = numpy.zeros(shape=(len(s), sum_.length()))
            new_channels[0:len(sum_), :] = sum_.channels()
            sum_ = sumpf.Signal(channels=new_channels, offset=sum_.offset())
        sum_ += s.shift(index)
        index += s.length() + s.offset()
    # return a signal with the correct labels
    return sumpf.Signal(channels=sum_.channels(),
                        sampling_rate=signals[0].sampling_rate(),
                        offset=sum_.offset(),
                        labels=tuple(tuple("Concatenation {}".format(i) for i in range(1, len(sum_) + 1))))


def _sanitize_offsets(signals):
    """makes sure, that the offsets of the signals are not so large, that the
    concatenation requires excessive amounts of memory."""
    r = random.Random()
    r.seed(signals[0].offset())
    # the first signal is returned with its original offset
    result = [signals[0]]
    # the other signal's offset must not exceed their length, so the concatenation is at maximum twice as long as the original signals combined
    for s in signals[1:]:
        if abs(s.offset()) < s.length():
            result.append(s)
        else:
            result.append(sumpf.Signal(channels=s.channels(),
                                       sampling_rate=s.sampling_rate(),
                                       offset=random.randint(-s.length(), s.length()),
                                       labels=s.labels()))
    return result
