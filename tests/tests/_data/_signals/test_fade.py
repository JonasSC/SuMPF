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

"""Tests for the :class:`~sumpf.Fade` class"""

import hypothesis
import numpy
import sumpf
import sumpf._internal as sumpf_internal
import tests


def test_constructor_defaults():
    """Tests the behavior, if a fade is instantiated without constructor parameters."""
    fade = sumpf.Fade()
    assert fade.labels() == ("Fade",)
    assert (fade.channels() == numpy.ones(shape=fade.shape())).all()


@hypothesis.given(function=hypothesis.strategies.sampled_from((numpy.ones,
                                                               numpy.bartlett,
                                                               numpy.hanning,
                                                               numpy.hamming,
                                                               numpy.blackman)),
                  start=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  stop=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_single_fade(function, start, stop, sampling_rate, length):
    """Tests the behavior, if there is only a fade in or out and not both."""
    # instantiate a fade in and a fade out
    interval = sorted((start, stop))
    a, b = sumpf_internal.index(interval, length=length)
    fade_in = sumpf.Fade(function=function, rise_interval=interval, sampling_rate=sampling_rate, length=length)
    fade_out = sumpf.Fade(function=function, fall_interval=interval, sampling_rate=sampling_rate, length=length)
    # instantiate test data
    rise = numpy.empty(length)
    rise[0:a] = 0.0
    rise[a:b] = function(2 * (b - a))[0:b - a]
    rise[b:] = 1.0
    fall = numpy.empty(length)
    fall[0:a] = 1.0
    fall[a:b] = function(2 * (b - a))[b - a:]
    fall[b:] = 0.0
    # check the metadata
    assert fade_in.sampling_rate() == fade_out.sampling_rate() == sampling_rate
    assert fade_in.length() == fade_out.length() == length
    assert fade_in.shape() == fade_out.shape() == (1, length)
    assert fade_in.labels() == ("Fade in",)
    assert fade_out.labels() == ("Fade out",)
    # check the samples of the fades
    assert not numpy.isnan(fade_in.channels()[0]).any()
    assert (fade_in.channels()[0] == rise).all()
    assert not numpy.isnan(fade_out.channels()[0]).any()
    assert (fade_out.channels()[0] == fall).all()


@hypothesis.given(function=hypothesis.strategies.sampled_from((numpy.ones,
                                                               numpy.bartlett,
                                                               numpy.hanning,
                                                               numpy.hamming,
                                                               numpy.blackman)),
                  rise_start=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  rise_stop=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  fall_start=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  fall_stop=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_both_fades(function, rise_start, rise_stop, fall_start, fall_stop, sampling_rate, length):
    """Tests the behavior, if there is a fade in and a fade out."""
    # instantiate the fade
    rise_interval = sorted((rise_start, rise_stop))
    fall_interval = sorted((fall_start, fall_stop))
    fade = sumpf.Fade(function, rise_interval, fall_interval, sampling_rate, length)
    # check the metadata
    assert fade.sampling_rate() == sampling_rate
    assert fade.length() == length
    assert fade.shape() == (1, length)
    # compare the signal's channel to a simpler (and slower) implementation
    a, b = sumpf_internal.index(rise_interval, length=length)
    rise = numpy.empty(length)
    rise[0:a] = 0.0
    rise[a:b] = function(2 * (b - a))[0:b - a]
    rise[b:] = 1.0
    c, d = sumpf_internal.index(fall_interval, length=length)
    fall = numpy.empty(length)
    fall[0:c] = 1.0
    fall[c:d] = function(2 * (d - c))[d - c:]
    fall[d:] = 0.0
    if a < c or (a == b == c != d):
        window = rise * fall
        label = "Fade in-out"
    else:
        window = rise + fall
        label = "Fade out-in"
    assert not numpy.isnan(fade.channels()[0]).any()
    assert (fade.channels()[0] == window).all()
    assert fade.labels() == (label,)
