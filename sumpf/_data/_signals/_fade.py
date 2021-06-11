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

"""Contains the Fade class"""

import collections
import numpy
import sumpf._internal as sumpf_internal
from ._signal import Signal

__all__ = ("Fade",)


class Fade(Signal):
    """A signal, that can be multiplied with other signals to fade them in and
    out gently.

    The fade in is done within the samples of the given rise interval, while the
    fade out is done during the fall interval. All other samples are either one
    or zero.

    If only one interval is given, the signal will be a simple fade in or fade
    out respectively.

    If the fade out is placed after the fade in, the signal starts with zeros,
    rises to one during the rise interval, stays there until the fall interval
    and ends with zeros. This is useful for fading excitation signals in and out,
    if they do not start or end with a zero sample.

    If the fade out is placed before the fade in, the signal starts with ones,
    falls to zero during the fall interval, stays there until the rise interval
    and ends with ones. This is useful for cutting away the noise in impulse responses.
    The fade in at the end can be done to capture the non-causal parts of the
    impulse response, that have been shifted to the back of the impulse response
    by a circular convolution.

    The function, that defines the slope of the fades can be configured, but the
    same function is used for both fades. If different functions shall be used,
    separate signals for the fade in and the fade out must be used.
    """

    def __init__(self,
                 function=numpy.blackman,
                 rise_interval=None,
                 fall_interval=None,
                 sampling_rate=48000.0,
                 length=2 ** 16):
        """
        :param function: a function, that takes an integer length and returns the
                         samples of a fade in, followed by a fade out, which have
                         in total as many samples as the given length. :mod:`numpy`'s
                         window functions can be used for this parameter.
        :param rise_interval: a tuple of sample indices between which the fade in
                              shall be done. The sample indices can be given as
                              integers or as floats between 0.0 and 1.0, that are
                              multiplied with the given length of the signal.
                              Negative numbers will be counted from the back of
                              the signal. Combining a float with an integer is
                              possible.
        :param fall_interval: a tuple of sample indices between which the fade out
                              shall be done. The sample indices can be given as
                              integers or as floats between 0.0 and 1.0, that are
                              multiplied with the given length of the signal.
                              Negative numbers will be counted from the back of
                              the signal. Combining a float with an integer is
                              possible.
        :param sampling_rate: the sampling rate of the signal as a float or integer
        :param length: the number of samples of the fade signal
        """
        # allocate shared memory for the channels
        channels = sumpf_internal.allocate_array(shape=(1, length), dtype=numpy.float64)
        channel = channels[0]
        # parse the raise and fall intervals
        if rise_interval is None:
            rise = None
        elif isinstance(rise_interval, collections.abc.Iterable):
            rise = sumpf_internal.index(rise_interval, length=length)
        else:
            rise = (0, sumpf_internal.index(rise_interval, length=length))
        if fall_interval is None:
            fall = None
        elif isinstance(fall_interval, collections.abc.Iterable):
            fall = sumpf_internal.index(fall_interval, length=length)
        else:
            fall = (sumpf_internal.index(fall_interval, length=length), length)
        # initialize the channels
        if rise is None:        # only fade out
            if fall is None:
                channel[:] = 1.0
                label = "Fade"
            else:
                a, b = fall
                fall_length = b - a
                channel[0:a] = 1.0
                channel[a:b] = function(2 * fall_length)[fall_length:]
                channel[b:] = 0.0
                label = "Fade out"
        elif fall is None:      # only fade in
            a, b = rise
            rise_length = b - a
            channel[0:a] = 0.0
            channel[a:b] = function(2 * rise_length)[0:rise_length]
            channel[b:] = 1.0
            label = "Fade in"
        elif (rise[0] < fall[0]) or ((rise[0] == rise[1] == fall[0] != fall[1])):   # fade in and then out
            a, b = rise
            c, d = fall
            start, stop = min(a, c), max(b, d)
            channel[0:start] = 0.0
            fade_in_out(function,
                        rise_stop=b - start,
                        fall_start=c - start,
                        fall_length=d - c,
                        out=channel[start:stop])
            channel[stop:] = 0.0
            label = "Fade in-out"
        else:                   # fade out and then in
            a, b = fall
            c, d = rise
            start, stop = min(a, c), max(b, d)
            channel[0:start] = 1.0
            fade_out_in(function,
                        fall_stop=b - a,
                        rise_start=c - a,
                        rise_length=d - c,
                        out=channel[min(a, c):max(b, d)])
            channel[stop:] = 1.0
            label = "Fade out-in"
        # initialize the signal
        Signal.__init__(self, channels=channels, sampling_rate=sampling_rate, offset=0, labels=(label,))

    ############################################
    # helper functions for generating the signal #
    ############################################


def fade_in_out(function, rise_stop, fall_start, fall_length, out):
    """Helper function for generating a signal, that first fades in and then fades out."""
    length = len(out)
    if rise_stop == fall_start:
        if rise_stop == fall_length:
            out[:] = function(length)
        else:
            out[0:rise_stop] = function(2 * rise_stop)[0:rise_stop]
            out[fall_start:] = function(2 * fall_length)[fall_length:]
    else:
        if rise_stop == fall_length:
            fade = function(rise_stop + fall_length)
            fade_in = fade[0:rise_stop]
            fade_out = fade[rise_stop:]
        else:
            fade_in = function(2 * rise_stop)[0:rise_stop]
            fade_out = function(2 * fall_length)[fall_length:]
        if rise_stop <= fall_start:
            out[0:rise_stop] = fade_in
            out[rise_stop:fall_start] = 1.0
            out[fall_start:] = fade_out
        else:
            fall_stop = fall_start + fall_length
            out[0:fall_start] = fade_in[0:fall_start]
            if fall_stop >= len(out):
                overlap_length = rise_stop - fall_start
                out[fall_start:rise_stop] = fade_in[fall_start:rise_stop] * fade_out[0:overlap_length]
                out[rise_stop:] = fade_out[overlap_length:]
            else:
                out[fall_start:fall_stop] = fade_in[fall_start:fall_stop] * fade_out
                out[fall_stop:] = 0.0


def fade_out_in(function, fall_stop, rise_start, rise_length, out):
    """Helper function for generating a signal, that first fades out and then fades in."""
    if fall_stop == rise_length:
        fade = function(fall_stop + rise_length)
        fade_out = fade[fall_stop:]
        fade_in = fade[0:rise_length]
    else:
        fade_out = function(2 * fall_stop)[fall_stop:]
        fade_in = function(2 * rise_length)[0:rise_length]
    if fall_stop <= rise_start:
        out[0:fall_stop] = fade_out
        out[fall_stop:rise_start] = 0.0
        out[rise_start:] = fade_in
    else:
        rise_stop = rise_start + rise_length
        out[0:rise_start] = fade_out[0:rise_start]
        if rise_stop >= len(out):
            overlap_length = fall_stop - rise_start
            out[rise_start:fall_stop] = fade_out[rise_start:fall_stop] + fade_in[0:overlap_length]
            out[fall_stop:] = fade_in[overlap_length:]
        else:
            out[rise_start:rise_stop] = fade_out[rise_start:rise_stop] + fade_in
            out[rise_stop:] = fade_out[rise_stop:] + 1.0
