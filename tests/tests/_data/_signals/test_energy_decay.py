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

"""Contains tests for the EnergyDecayCurve signal class."""

import math
import hypothesis
import numpy
import pytest
import sumpf
import tests


@hypothesis.given(tests.strategies.signals)
def test_metadata(signal):
    """tests if the energy decay curve computation preserves the original signal's metadata."""
    edc = sumpf.EnergyDecayCurve(signal)
    assert edc.sampling_rate() == signal.sampling_rate()
    assert edc.offset() == signal.offset()
    assert edc.labels() == signal.labels()


def test_channels_manual():
    """compares the result of an energy decay curve computation to a manually computed result."""
    signal = sumpf.Signal(channels=numpy.array([(1.0, 2.0, 3.0),
                                                (0.4, 0.5, 0.6)]))
    edc = sumpf.EnergyDecayCurve(signal).channels()
    ref = numpy.array([(14.0, 13.0, 9.0),
                       (0.77, 0.61, 0.36)])
    assert (edc == ref).all()


@hypothesis.given(tests.strategies.signals)
def test_channels(signal):
    """compares the energy decay curve computation to a straight forward numpy implementation."""
    edc = sumpf.EnergyDecayCurve(signal).channels()
    ref = numpy.square(signal.channels())
    for i in range(signal.length()):
        ref[:, i] = numpy.sum(ref[:, i:], axis=1)
    assert edc == pytest.approx(ref)


@hypothesis.given(before_length=hypothesis.strategies.integers(min_value=2, max_value=2 ** 8),
                  decay_length=hypothesis.strategies.integers(min_value=3, max_value=2 ** 12),
                  after_length=hypothesis.strategies.integers(min_value=2, max_value=2 ** 8),
                  start_level=hypothesis.strategies.floats(min_value=1e-4, max_value=1e15),
                  decays=hypothesis.strategies.lists(elements=hypothesis.strategies.floats(min_value=5e-4, max_value=1.0 - 1e-6), min_size=1, max_size=5),
                  sampling_rate=tests.strategies.sampling_rates,
                  offset=hypothesis.strategies.integers(),
                  labels=tests.strategies.labels)
def test_reverberation_time(before_length, decay_length, after_length, start_level, decays, sampling_rate, offset, labels):
    """Tests the reverberation time computation with a manual computation from the
    slope of the decay_model method's result.
    """
    decay_stop = before_length + decay_length
    edc = _new_energy_decay_curve(before_length, decay_length, after_length, start_level, decays, sampling_rate, offset, labels)
    model = edc.decay_model(before_length, decay_stop)
    reverberation_times = edc.reverberation_time(before_length, decay_stop)
    for channel, reverberation_time in zip(model.channels(), reverberation_times):
        slope = 10.0 * numpy.average(numpy.diff(numpy.log10(channel)))
        reference = -60 / slope / model.sampling_rate()
        assert reverberation_time == pytest.approx(reference, rel=1e-8)


@pytest.mark.filterwarnings("ignore:overflow")
@hypothesis.given(before_length=hypothesis.strategies.integers(min_value=2, max_value=2 ** 12),
                  decay_length=hypothesis.strategies.integers(min_value=2, max_value=2 ** 12),
                  after_length=hypothesis.strategies.integers(min_value=2, max_value=2 ** 12),
                  start_level=hypothesis.strategies.floats(min_value=1e-4, max_value=1e15),
                  decays=hypothesis.strategies.lists(elements=hypothesis.strategies.floats(min_value=1e-4, max_value=1.0), min_size=1, max_size=5),
                  sampling_rate=tests.strategies.sampling_rates,
                  offset=hypothesis.strategies.integers(),
                  labels=tests.strategies.labels)
def test_decay_model(before_length, decay_length, after_length, start_level, decays, sampling_rate, offset, labels):
    """Tests the decay_model method."""
    decay_stop = before_length + decay_length
    edc = _new_energy_decay_curve(before_length, decay_length, after_length, start_level, decays, sampling_rate, offset, labels)
    model = edc.decay_model(before_length, decay_stop)
    assert model.shape() == edc.shape()
    for channel, reference in zip(model.channels(), edc.channels()):
        assert channel[before_length:decay_stop] == pytest.approx(reference[before_length:decay_stop])
    assert model.sampling_rate() == sampling_rate
    assert model.offset() == offset
    assert model.labels() == edc.labels()


def _new_energy_decay_curve(before_length, decay_length, after_length, start_level, decays, sampling_rate, offset, labels):
    """Helper function for creating a very simple energy decay function from parameters,
    that can be generated by hypothesis."""
    channels = numpy.empty(shape=(len(decays), before_length + decay_length + after_length))
    decay_stop = before_length + decay_length
    for channel, decay in zip(channels, decays):
        channel[0:before_length] = start_level
        channel[before_length:decay_stop] = start_level * numpy.exp((math.log(decay) / decay_length) * numpy.arange(decay_length))
        channel[decay_stop:] = start_level * decay
        start_level *= decay
    edc = sumpf.EnergyDecayCurve.__new__(sumpf.EnergyDecayCurve)
    sumpf.Signal.__init__(edc, channels, sampling_rate, offset, labels)
    return edc
