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

"""Tests for the Signal class"""

import copy
import itertools
import logging
import math
import numpy
import hypothesis
import pytest
import sumpf
import sumpf._internal as sumpf_internal
import tests

###########################################
# overloaded operators (non math-related) #
###########################################


def test_getitem_channels():
    """Tests the slicing of a signal's channels with the ``[]`` overload"""
    signal = sumpf.Signal(channels=numpy.array([(1.0, 0.0, 0.0),
                                                (0.0, 2.0, 0.0),
                                                (0.0, 0.0, 3.0)]),
                          offset=1,
                          labels=("one", "two", "three"))
    # integer
    sliced = signal[1]
    assert (sliced.channels() == [(0.0, 2.0, 0.0)]).all()
    assert sliced.offset() == signal.offset()
    assert sliced.labels() == ("two",)
    # float
    assert signal[0.5] == signal[1]
    # integer slice
    sliced = signal[1:3]
    assert (sliced.channels() == [(0.0, 2.0, 0.0), (0.0, 0.0, 3.0)]).all()
    assert sliced.offset() == signal.offset()
    assert sliced.labels() == ("two", "three")
    # integer slice with step
    sliced = signal[0:3:2]
    assert (sliced.channels() == [(1.0, 0.0, 0.0), (0.0, 0.0, 3.0)]).all()
    assert sliced.offset() == signal.offset()
    assert sliced.labels() == ("one", "three")
    # incomplete slices
    assert signal[:] == signal
    assert signal[:2] == signal[0:2]
    assert signal[1:] == signal[1:3]
    assert signal[0::2] == signal[0:3:2]
    # float slices
    assert signal[0.33:1.0] == signal[1:3]
    assert signal[0:3:0.66] == signal[0:3:2]
    # negative slices
    assert signal[0:-1] == signal[0:2]
    assert signal[-2:] == signal[1:3]
    sliced = signal[::-1]
    assert (sliced.channels() == [(0.0, 0.0, 3.0), (0.0, 2.0, 0.0), (1.0, 0.0, 0.0)]).all()
    assert sliced.offset() == signal.offset()
    assert sliced.labels() == ("three", "two", "one")
    assert signal[-0.99:-0.01:-0.66] == signal[0:3:-2]


def test_getitem_samples():
    """Tests the slicing of a signal with the ``[]`` overload"""
    signal = sumpf.Signal(channels=numpy.array([(1.0, 0.0, 0.0),
                                                (0.0, 2.0, 0.0),
                                                (0.0, 0.0, 3.0)]),
                          offset=1,
                          labels=("one", "two", "three"))
    # integer
    sliced = signal[1, 1]
    assert (sliced.channels() == [(2.0,)]).all()
    assert sliced.offset() == signal.offset() + 1
    assert sliced.labels() == ("two",)
    # float
    assert signal[:, 0.5] == signal[:, 1]
    # integer slice
    sliced = signal[1:3, 1:3]
    assert (sliced.channels() == [(2.0, 0.0), (0.0, 3.0)]).all()
    assert sliced.offset() == signal.offset() + 1
    assert sliced.labels() == ("two", "three")
    # integer slice with step
    sliced = signal[:, 0:3:2]
    assert (sliced.channels() == [(1.0, 0.0), (0.0, 0.0), (0.0, 3.0)]).all()
    assert sliced.offset() == signal.offset()
    assert sliced.labels() == ("one", "two", "three")
    # incomplete slices
    assert signal[:, :] == signal
    assert signal[:2, :1] == signal[0:2, 0]
    assert signal[1:, 2:] == signal[1:3, 2]
    assert signal[0::2, 0::2] == signal[0:3:2, 0:3:2]
    # float slices
    assert signal[0.33:1.0, 0.0:0.66] == signal[1:3, 0:2]
    assert signal[0:3:0.66, 0.0:1.0:0.66] == signal[0:3:2, 0:3:2]
    # negative slices
    assert signal[0:-2, 0:-1] == signal[0, 0:2]
    assert signal[-2:, -1:] == signal[1:3, 2]
    sliced = signal[::-1, ::-1]
    assert (sliced.channels() == [(3.0, 0.0, 0.0), (0.0, 2.0, 0.0), (0.0, 0.0, 1.0)]).all()
    assert sliced.offset() == signal.offset()
    assert sliced.labels() == ("three", "two", "one")
    assert signal[-0.99:-0.01:-0.66, -0.99:-0.01:-0.66] == signal[0:3:-2, 0:3:-2]


@hypothesis.given(tests.strategies.signals())
def test_str(signal):
    """Checks if casting a Signal instance to a string raises an error."""
    logging.info(str(signal))


@hypothesis.given(tests.strategies.signals())
def test_repr(signal):
    """Checks if a signal can be restored from its string representation."""
    # required symbols for the evaluation of the repr-string
    array = numpy.array         # noqa
    float64 = numpy.float64     # noqa
    Signal = sumpf.Signal       # noqa
    # create a signal, cast it to a string and restore it from the string
    restored = eval(repr(signal))   # pylint: disable=eval-used
    assert restored == signal


@hypothesis.given(tests.strategies.signal_parameters())
def test_eq(parameters):
    """Tests the operator overloads for ``==`` and ``!=``."""
    signal1 = sumpf.Signal(**parameters)
    signal2 = sumpf.Signal(**parameters)
    assert signal1 is not signal2
    assert signal1 == signal2
    if signal2.length() > 1:
        assert signal1 != signal2[:, 0:-1]  # test for a case, where the NumPy comparison of the channels returns a boolean rather than an array of booleans
    assert signal1 != (signal2 + signal2) * signal2
    assert signal1 != signal1.channels()


@hypothesis.given(tests.strategies.signal_parameters())
def test_hash(parameters):
    """Tests the operator overload for hashing a signal with the builtin :func:`hash` function."""
    parameters2 = copy.copy(parameters)
    parameters2["channels"] = numpy.empty(shape=parameters["channels"].shape)
    parameters2["channels"][:] = parameters["channels"][:]
    signal1 = sumpf.Signal(**parameters)
    signal2 = sumpf.Signal(**parameters2)
    signal3 = (signal2 + signal2) * signal2
    assert signal1.channels() is not signal2.channels()
    assert hash(signal1) == hash(signal2)
    assert hash(signal1) != hash(signal3)

###################################
# overloaded unary math operators #
###################################


@hypothesis.given(tests.strategies.signals())
def test_absolute(signal):
    """Tests if computing the absolute of a signal yields the expected result."""
    assert abs(signal) == sumpf.Signal(channels=numpy.absolute(signal.channels()),
                                       sampling_rate=signal.sampling_rate(),
                                       offset=signal.offset(),
                                       labels=signal.labels())


@hypothesis.given(tests.strategies.signals())
def test_reversed(signal):
    """Tests if reversing a signal works as expected"""
    reverse = reversed(signal)
    assert (reverse.channels() == [tuple(reversed(c)) for c in signal.channels()]).all()
    assert reverse.sampling_rate() == signal.sampling_rate()
    assert reverse.offset() == signal.length() - 1 - signal.offset()
    assert reverse.labels() == signal.labels()


@hypothesis.given(tests.strategies.signals())
def test_negative(signal):
    """Tests if computing the negative of a signal yields the expected result."""
    assert -signal == sumpf.Signal(channels=numpy.subtract(0.0, signal.channels()),
                                   sampling_rate=signal.sampling_rate(),
                                   offset=signal.offset(),
                                   labels=signal.labels())

####################################
# overloaded binary math operators #
####################################


def test_add():
    """Tests the overload of the ``+`` operator."""
    signal1 = sumpf.Signal(channels=numpy.array([(1.0, 0.0, 0.0),
                                                 (0.0, 2.0, 0.0)]),
                           offset=1,
                           labels=("one1", "two1"))
    signal2 = sumpf.Signal(channels=numpy.array([(1.0, 0.0, 0.0),
                                                 (0.0, 2.0, 0.0),
                                                 (0.0, 0.0, 3.0)]),
                           offset=-1,
                           labels=("one2", "two2", "three2"))
    # test adding a number
    sum_ = signal1 + 3.7
    assert sum_.offset() == signal1.offset()
    assert sum_.sampling_rate() == signal1.sampling_rate()
    assert sum_.labels() == signal1.labels()
    assert (sum_.channels() == numpy.add(signal1.channels(), 3.7)).all()
    assert ((3.7 + signal1).channels() == sum_.channels()).all()
    # test adding an array
    sum_ = signal1 + (1.9, -3.8, 5.5)
    assert sum_.offset() == signal1.offset()
    assert sum_.sampling_rate() == signal1.sampling_rate()
    assert sum_.labels() == signal1.labels()
    assert (sum_.channels() == numpy.add(signal1.channels(), (1.9, -3.8, 5.5))).all()
    assert (((1.9, -3.8, 5.5) + signal1).channels() == sum_.channels()).all()
    # test adding a fully overlapping Signal
    sum_ = signal1 + signal1
    assert sum_.offset() == signal1.offset()
    assert sum_.sampling_rate() == signal1.sampling_rate()
    assert sum_.labels() == ("Sum",) * 2
    assert (sum_.channels() == numpy.multiply(signal1.channels(), 2)).all()
    # test adding a fully overlapping single channel Signal
    sum_ = signal1 + signal1[1]
    assert sum_.offset() == signal1.offset()
    assert sum_.sampling_rate() == signal1.sampling_rate()
    assert sum_.labels() == ("Sum",) * 2
    assert (sum_.channels() == numpy.add(signal1.channels(), signal1[1].channels())).all()
    assert ((signal1[1] + signal1).channels() == sum_.channels()).all()
    # test adding a partially overlapping Signal
    sum_ = signal1 + signal2
    assert sum_.offset() == -1
    assert sum_.sampling_rate() == signal1.sampling_rate()
    assert sum_.labels() == ("Sum",) * 3
    assert (sum_.channels() == [(1.0, 0.0, 1.0, 0.0, 0.0), (0.0, 2.0, 0.0, 2.0, 0.0), (0.0, 0.0, 3.0, 0.0, 0.0)]).all()
    assert ((signal2 + signal1).channels() == sum_.channels()).all()
    # test adding a partially overlapping single channel Signal
    sum_ = signal1 + signal2[2]
    assert sum_.offset() == -1
    assert sum_.sampling_rate() == signal1.sampling_rate()
    assert sum_.labels() == ("Sum",) * 2
    assert (sum_.channels() == [(0.0, 0.0, 4.0, 0.0, 0.0), (0.0, 0.0, 3.0, 2.0, 0.0)]).all()
    assert ((signal2[2] + signal1).channels() == sum_.channels()).all()


def test_subtract():
    """Tests the overload of the ``-`` operator."""
    signal1 = sumpf.Signal(channels=numpy.array([(1.0, 0.0, 0.0),
                                                 (0.0, 2.0, 0.0)]),
                           offset=1,
                           labels=("one1", "two1"))
    signal2 = sumpf.Signal(channels=numpy.array([(1.0, 0.0, 0.0),
                                                 (0.0, 2.0, 0.0),
                                                 (0.0, 0.0, 3.0)]),
                           offset=-1,
                           labels=("one2", "two2", "three2"))
    # test subtracting a number
    difference = signal1 - 3.7
    assert difference.offset() == signal1.offset()
    assert difference.sampling_rate() == signal1.sampling_rate()
    assert difference.labels() == signal1.labels()
    assert (difference.channels() == numpy.subtract(signal1.channels(), 3.7)).all()
    assert ((3.7 - signal1).channels() == numpy.subtract(3.7, signal1.channels())).all()
    # test subtracting an array
    difference = signal1 - (1.9, -3.8, 5.5)
    assert difference.offset() == signal1.offset()
    assert difference.sampling_rate() == signal1.sampling_rate()
    assert difference.labels() == signal1.labels()
    assert (difference.channels() == numpy.subtract(signal1.channels(), (1.9, -3.8, 5.5))).all()
    assert (((1.9, -3.8, 5.5) - signal1).channels() == numpy.subtract((1.9, -3.8, 5.5), signal1.channels())).all()
    # test subtracting a fully overlapping Signal
    difference = signal1 - signal1
    assert difference.offset() == signal1.offset()
    assert difference.sampling_rate() == signal1.sampling_rate()
    assert difference.labels() == ("Difference",) * 2
    assert (difference.channels() == numpy.zeros(shape=signal1.shape())).all()
    # test subtracting a fully overlapping single channel Signal
    difference = signal1 - signal1[1]
    assert difference.offset() == signal1.offset()
    assert difference.sampling_rate() == signal1.sampling_rate()
    assert difference.labels() == ("Difference",) * 2
    assert (difference.channels() == numpy.subtract(signal1.channels(), signal1[1].channels())).all()
    assert ((signal1[1] - signal1).channels() == numpy.subtract(signal1[1].channels(), signal1.channels())).all()
    # test subtracting a partially overlapping Signal
    difference = signal1 - signal2
    assert difference.offset() == -1
    assert difference.sampling_rate() == signal1.sampling_rate()
    assert difference.labels() == ("Difference",) * 3
    assert (difference.channels() == [(-1.0, 0.0, 1.0, 0.0, 0.0),
                                      (0.0, -2.0, 0.0, 2.0, 0.0),
                                      (0.0, 0.0, -3.0, 0.0, 0.0)]).all()
    assert ((signal2 - signal1).channels() == [(1.0, 0.0, -1.0, 0.0, 0.0),
                                               (0.0, 2.0, 0.0, -2.0, 0.0),
                                               (0.0, 0.0, 3.0, 0.0, 0.0)]).all()
    # test subtracting a partially overlapping single channel Signal
    difference = signal1 - signal2[2]
    assert difference.offset() == -1
    assert difference.sampling_rate() == signal1.sampling_rate()
    assert difference.labels() == ("Difference",) * 2
    assert (difference.channels() == [(0.0, 0.0, -2.0, 0.0, 0.0), (0.0, 0.0, -3.0, 2.0, 0.0)]).all()
    assert ((signal2[2] - signal1).channels() == [(0.0, 0.0, 2.0, 0.0, 0.0), (0.0, 0.0, 3.0, -2.0, 0.0)]).all()


def test_multiply():
    """Tests the overload of the ``*`` operator."""
    signal1 = sumpf.Signal(channels=numpy.array([(1.1, 1.0, 1.0),
                                                 (1.0, 1.2, 1.0)]),
                           offset=1,
                           labels=("one1", "two1"))
    signal2 = sumpf.Signal(channels=numpy.array([(2.0, 1.0, 1.0),
                                                 (1.0, 3.0, 1.0),
                                                 (1.0, 1.0, 4.0)]),
                           offset=-1,
                           labels=("one2", "two2", "three2"))
    # test multiplying with a number
    product = signal1 * 3.7
    assert product.offset() == signal1.offset()
    assert product.sampling_rate() == signal1.sampling_rate()
    assert product.labels() == signal1.labels()
    assert (product.channels() == numpy.multiply(signal1.channels(), 3.7)).all()
    assert ((3.7 * signal1).channels() == product.channels()).all()
    # test multiplying with an array
    product = signal1 * (1.9, -3.8, 5.5)
    assert product.offset() == signal1.offset()
    assert product.sampling_rate() == signal1.sampling_rate()
    assert product.labels() == signal1.labels()
    assert (product.channels() == numpy.multiply(signal1.channels(), (1.9, -3.8, 5.5))).all()
    assert (((1.9, -3.8, 5.5) * signal1).channels() == product.channels()).all()
    # test multiplying with a fully overlapping Signal
    product = signal1 * signal1
    assert product.offset() == signal1.offset()
    assert product.sampling_rate() == signal1.sampling_rate()
    assert product.labels() == ("Product",) * 2
    assert (product.channels() == numpy.square(signal1.channels())).all()
    # test multiplying with a fully overlapping single channel Signal
    product = signal1 * signal1[1]
    assert product.offset() == signal1.offset()
    assert product.sampling_rate() == signal1.sampling_rate()
    assert product.labels() == ("Product",) * 2
    assert (product.channels() == numpy.multiply(signal1.channels(), signal1[1].channels())).all()
    assert ((signal1[1] * signal1).channels() == product.channels()).all()
    # test multiplying with a partially overlapping Signal
    product = signal1 * signal2
    assert product.offset() == -1
    assert product.sampling_rate() == signal1.sampling_rate()
    assert product.labels() == ("Product",) * 3
    assert (product.channels() == [(2.0, 1.0, 1.1, 1.0, 1.0),
                                   (1.0, 3.0, 1.0, 1.2, 1.0),
                                   (1.0, 1.0, 4.0, 0.0, 0.0)]).all()
    assert ((signal2 * signal1).channels() == product.channels()).all()
    # test multiplying with a partially overlapping single channel Signal
    product = signal1 * signal2[2]
    assert product.offset() == -1
    assert product.sampling_rate() == signal1.sampling_rate()
    assert product.labels() == ("Product",) * 2
    assert (product.channels() == [(1.0, 1.0, 4.4, 1.0, 1.0), (1.0, 1.0, 4.0, 1.2, 1.0)]).all()
    assert ((signal2[2] * signal1).channels() == product.channels()).all()


def test_divide():
    """Tests the overload of the ``/`` operator."""
    signal1 = sumpf.Signal(channels=numpy.array([(1.5, 1.0, 1.0),
                                                 (1.0, 1.2, 1.0)]),
                           offset=1,
                           labels=("one1", "two1"))
    signal2 = sumpf.Signal(channels=numpy.array([(2.0, 1.0, 1.0),
                                                 (1.0, 0.5, 1.0),
                                                 (1.0, 1.0, 0.2)]),
                           offset=-1,
                           labels=("one2", "two2", "three2"))
    # test dividing by a number
    quotient = signal1 / 3.7
    assert quotient.offset() == signal1.offset()
    assert quotient.sampling_rate() == signal1.sampling_rate()
    assert quotient.labels() == signal1.labels()
    assert (quotient.channels() == numpy.divide(signal1.channels(), 3.7)).all()
    assert ((3.7 / signal1).channels() == numpy.divide(3.7, signal1.channels())).all()
    # test dividing by an array
    quotient = signal1 / (1.9, -3.8, 5.5)
    assert quotient.offset() == signal1.offset()
    assert quotient.sampling_rate() == signal1.sampling_rate()
    assert quotient.labels() == signal1.labels()
    assert (quotient.channels() == numpy.divide(signal1.channels(), (1.9, -3.8, 5.5))).all()
    assert (((1.9, -3.8, 5.5) / signal1).channels() == numpy.divide((1.9, -3.8, 5.5), signal1.channels())).all()
    # test dividing by a fully overlapping signal
    quotient = signal1 / signal1
    assert quotient.offset() == signal1.offset()
    assert quotient.sampling_rate() == signal1.sampling_rate()
    assert quotient.labels() == ("Quotient",) * 2
    assert (quotient.channels() == numpy.ones(shape=signal1.shape())).all()
    # test dividing by a fully overlapping single channel signal
    quotient = signal1 / signal1[1]
    assert quotient.offset() == signal1.offset()
    assert quotient.sampling_rate() == signal1.sampling_rate()
    assert quotient.labels() == ("Quotient",) * 2
    assert (quotient.channels() == numpy.divide(signal1.channels(), signal1[1].channels())).all()
    assert ((signal1[1] / signal1).channels() == numpy.divide(signal1[1].channels(), signal1.channels())).all()
    # test dividing by a partially overlapping signal
    quotient = signal1 / signal2
    assert quotient.offset() == -1
    assert quotient.sampling_rate() == signal1.sampling_rate()
    assert quotient.labels() == ("Quotient",) * 3
    assert (quotient.channels() == [(0.5, 1.0, 1.5, 1.0, 1.0),
                                    (1.0, 2.0, 1.0, 1.2, 1.0),
                                    (1.0, 1.0, 5.0, 0.0, 0.0)]).all()
    assert ((signal2 / signal1).channels() == [(2.0, 1.0, 2 / 3, 1.0, 1.0),
                                               (1.0, 0.5, 1.0, 5 / 6, 1.0),
                                               (1.0, 1.0, 0.2, 0.0, 0.0)]).all()
    # test dividing by a partially overlapping single channel signal
    quotient = signal1 / signal2[2]
    assert quotient.offset() == -1
    assert quotient.sampling_rate() == signal1.sampling_rate()
    assert quotient.labels() == ("Quotient",) * 2
    assert (quotient.channels() == [(1.0, 1.0, 7.5, 1.0, 1.0), (1.0, 1.0, 5.0, 1.2, 1.0)]).all()
    assert ((signal2[2] / signal1).channels() == [(1.0, 1.0, 2 / 15, 1.0, 1.0), (1.0, 1.0, 0.2, 5 / 6, 1.0)]).all()


def test_modulo():
    """Tests the overload of the ``%`` operator."""
    signal1 = sumpf.Signal(channels=numpy.array([(1.5, 1.0, 1.0),
                                                 (1.0, 1.2, 1.0)]),
                           offset=1,
                           labels=("one1", "two1"))
    signal2 = sumpf.Signal(channels=numpy.array([(2.0, 1.0, 1.0),
                                                 (1.0, 0.5, 1.0),
                                                 (1.0, 1.0, 0.25)]),
                           offset=-1,
                           labels=("one2", "two2", "three2"))
    # test dividing by a number
    modulo = signal1 % 3.7
    assert modulo.offset() == signal1.offset()
    assert modulo.sampling_rate() == signal1.sampling_rate()
    assert modulo.labels() == signal1.labels()
    assert (modulo.channels() == numpy.mod(signal1.channels(), 3.7)).all()
    assert ((3.7 % signal1).channels() == numpy.mod(3.7, signal1.channels())).all()
    # test dividing by an array
    modulo = signal1 % (1.9, -3.8, 5.5)
    assert modulo.offset() == signal1.offset()
    assert modulo.sampling_rate() == signal1.sampling_rate()
    assert modulo.labels() == signal1.labels()
    assert (modulo.channels() == numpy.mod(signal1.channels(), (1.9, -3.8, 5.5))).all()
    assert (((1.9, -3.8, 5.5) % signal1).channels() == numpy.mod((1.9, -3.8, 5.5), signal1.channels())).all()
    # test dividing by a fully overlapping Signal
    modulo = signal1 % signal1
    assert modulo.offset() == signal1.offset()
    assert modulo.sampling_rate() == signal1.sampling_rate()
    assert modulo.labels() == ("Modulo",) * 2
    assert (modulo.channels() == numpy.zeros(shape=signal1.shape())).all()
    # test dividing by a fully overlapping single channel Signal
    modulo = signal1 % signal1[1]
    assert modulo.offset() == signal1.offset()
    assert modulo.sampling_rate() == signal1.sampling_rate()
    assert modulo.labels() == ("Modulo",) * 2
    assert (modulo.channels() == numpy.mod(signal1.channels(), signal1[1].channels())).all()
    assert ((signal1[1] % signal1).channels() == numpy.mod(signal1[1].channels(), signal1.channels())).all()
    # test dividing by a partially overlapping Signal
    modulo = signal1 % signal2
    assert modulo.offset() == -1
    assert modulo.sampling_rate() == signal1.sampling_rate()
    assert modulo.labels() == ("Modulo",) * 3
    assert (modulo.channels() == [(2.0, 1.0, 0.5, 1.0, 1.0),
                                  (1.0, 0.5, 0.0, 1.2, 1.0),
                                  (1.0, 1.0, 0.25, 0.0, 0.0)]).all()
    assert ((signal2 % signal1).channels() == [(2.0, 1.0, 1.0, 1.0, 1.0),
                                               (1.0, 0.5, 0.0, 1.2, 1.0),
                                               (1.0, 1.0, 0.25, 0.0, 0.0)]).all()
    # test dividing by a partially overlapping single channel Signal
    modulo = signal1 % signal2[2]
    assert modulo.offset() == -1
    assert modulo.sampling_rate() == signal1.sampling_rate()
    assert modulo.labels() == ("Modulo",) * 2
    assert (modulo.channels() == [(1.0, 1.0, 0.0, 1.0, 1.0), (1.0, 1.0, 0.0, 1.2, 1.0)]).all()
    assert ((signal2[2] % signal1).channels() == [(1.0, 1.0, 0.25, 1.0, 1.0), (1.0, 1.0, 0.25, 1.2, 1.0)]).all()


def test_power():
    """Tests the overload of the ``**`` operator."""
    signal1 = sumpf.Signal(channels=numpy.array([(1.5, 1.0, 1.0),
                                                 (1.0, 1.2, 1.0)]),
                           offset=1,
                           labels=("one1", "two1"))
    signal2 = sumpf.Signal(channels=numpy.array([(2.0, 1.0, 1.0),
                                                 (1.0, 0.5, 1.0),
                                                 (1.0, 1.0, 0.2)]),
                           offset=-1,
                           labels=("one2", "two2", "three2"))
    # test computing the power with a number
    power = signal1 ** 3.7
    assert power.offset() == signal1.offset()
    assert power.sampling_rate() == signal1.sampling_rate()
    assert power.labels() == signal1.labels()
    assert (power.channels() == numpy.power(signal1.channels(), 3.7)).all()
    assert ((3.7 ** signal1).channels() == numpy.power(3.7, signal1.channels())).all()
    # test computing the power with an array
    power = signal1 ** (1.9, 3.8, 5.5)
    assert power.offset() == signal1.offset()
    assert power.sampling_rate() == signal1.sampling_rate()
    assert power.labels() == signal1.labels()
    assert (power.channels() == numpy.power(signal1.channels(), (1.9, 3.8, 5.5))).all()
    assert (((1.9, 3.8, 5.5) ** signal1).channels() == numpy.power((1.9, 3.8, 5.5), signal1.channels())).all()
    # test computing the power with a fully overlapping Signal
    power = signal1 ** signal1
    assert power.offset() == signal1.offset()
    assert power.sampling_rate() == signal1.sampling_rate()
    assert power.labels() == ("Power",) * 2
    assert (power.channels() == numpy.power(signal1.channels(), signal1.channels())).all()
    # test computing the power with a fully overlapping single channel Signal
    power = signal1 ** signal1[1]
    assert power.offset() == signal1.offset()
    assert power.sampling_rate() == signal1.sampling_rate()
    assert power.labels() == ("Power",) * 2
    assert (power.channels() == numpy.power(signal1.channels(), signal1[1].channels())).all()
    assert ((signal1[1] ** signal1).channels() == numpy.power(signal1[1].channels(), signal1.channels())).all()
    # test computing the power with a partially overlapping Signal
    power = signal1 ** signal2
    assert power.offset() == -1
    assert power.sampling_rate() == signal1.sampling_rate()
    assert power.labels() == ("Power",) * 3
    assert (power.channels() == [(2.0, 1.0, 1.5, 1.0, 1.0), (1.0, 0.5, 1.0, 1.2, 1.0), (1.0, 1.0, 0.2, 0.0, 0.0)]).all()
    assert ((signal2 ** signal1).channels() == [(2.0, 1.0, 1.0, 1.0, 1.0),
                                                (1.0, 0.5, 1.0, 1.2, 1.0),
                                                (1.0, 1.0, 0.2, 0.0, 0.0)]).all()
    # test computing the power with a partially overlapping single channel Signal
    power = signal1 ** signal2[2]
    assert power.offset() == -1
    assert power.sampling_rate() == signal1.sampling_rate()
    assert power.labels() == ("Power",) * 2
    assert (power.channels() == [(1.0, 1.0, 1.5 ** 0.2, 1.0, 1.0), (1.0, 1.0, 1.0, 1.2, 1.0)]).all()
    assert ((signal2[2] ** signal1).channels() == [(1.0, 1.0, 0.2 ** 1.5, 1.0, 1.0), (1.0, 1.0, 0.2, 1.2, 1.0)]).all()

#########################################
# overloaded and misused math operators #
#########################################


def test_invert_results():
    """Tests if computing the inverse of a signal with known inverse yields the expected result."""
    # test with an even-length signal
    signal = sumpf.Signal(channels=numpy.array([(2.0, 0.0, 0.0, 0.0),
                                                (0.0, 1.0, 0.0, 0.0)]),
                          offset=-1,
                          labels=("one", "two"))
    assert ~signal == sumpf.Signal(channels=numpy.array([(0.5, 0.0, 0.0, 0.0),
                                                         (0.0, 0.0, 0.0, 1.0)]),
                                   offset=1,
                                   labels=("one", "two"))
    # test with an odd-length signal, which shall not drop a sample in the FFT
    signal = sumpf.Signal(channels=numpy.array([(2.0, 0.0, 0.0),
                                                (0.0, 1.0, 0.0)]),
                          offset=-1,
                          labels=("one", "two"))
    inverse = ~signal
    assert inverse.channels() == pytest.approx(numpy.array([(0.5, 0.0, 0.0), (0.0, 0.0, 1.0)]))
    assert inverse.offset() == -signal.offset()
    assert inverse.sampling_rate() == signal.sampling_rate()
    assert inverse.labels() == signal.labels()

##############
# parameters #
##############


@hypothesis.given(tests.strategies.signal_parameters())
def test_constructor_parameters(parameters):
    """Tests if the constructor parameters are interpreted correctly and have the expected default values."""
    # test an empty Signal
    signal = sumpf.Signal()
    assert (signal.channels() == [[]]).all()
    assert signal.sampling_rate() == 48000.0
    assert signal.offset() == 0
    assert signal.labels() == ("",)
    # test a Signal with all constructor parameters set
    channels = parameters["channels"]
    sampling_rate = parameters["sampling_rate"]
    offset = parameters["offset"]
    labels = tuple(parameters["labels"][0:len(channels)]) + ("",) * (len(channels) - len(parameters["labels"]))
    signal = sumpf.Signal(**parameters)
    assert (signal.channels() == channels).all()
    assert signal.sampling_rate() == sampling_rate
    assert signal.offset() == offset
    assert signal.labels() == labels


@hypothesis.given(tests.strategies.signals())
def test_derived_parameters(signal):
    """Tests if the signal's parameters, that are derived from its constructor parameters are correct."""
    assert signal.length() == len(signal.channels()[0])
    assert signal.shape() == numpy.shape(signal.channels())
    assert signal.duration() == signal.length() / signal.sampling_rate()

#######################
# convenience methods #
#######################


@hypothesis.given(tests.strategies.signals())
def test_time_samples(signal):
    """Tests the method, that generates the time samples for the signal."""
    t = signal.time_samples()
    if signal.length():
        assert t[0] == signal.offset() / signal.sampling_rate()
    reference = numpy.arange(signal.offset(), signal.offset() + signal.length(), dtype=numpy.float64)
    reference /= signal.sampling_rate()
    assert t == pytest.approx(reference)


@hypothesis.given(signal=tests.strategies.signals(),
                  length=tests.strategies.short_lengths,
                  value=hypothesis.strategies.floats(allow_nan=False, allow_infinity=False))
def test_pad(signal, length, value):
    """Tests the method for padding a signal."""
    padded = signal.pad(length, value)
    if length < signal.length():
        assert padded == signal[:, 0:length]
    elif length > signal.length():
        assert padded[:, 0:signal.length()] == signal
        assert (padded.channels()[:, signal.length():] == value).all()
    else:
        assert padded == signal


@hypothesis.given(signal=tests.strategies.signals(),
                  shift=hypothesis.strategies.integers(min_value=-100, max_value=100))
def test_shift(signal, shift):
    """Tests the method for shifting the signal"""
    # mode OFFSET
    shifted = signal.shift(shift)
    assert (shifted.channels() == signal.channels()).all()
    assert shifted.sampling_rate() == signal.sampling_rate()
    assert shifted.offset() == signal.offset() + shift
    assert shifted.labels() == signal.labels()
    shifted = signal.shift(None)
    assert (shifted.channels() == signal.channels()).all()
    assert shifted.sampling_rate() == signal.sampling_rate()
    assert shifted.offset() == 0
    assert shifted.labels() == signal.labels()
    # mode CROP
    shifted = signal.shift(shift=shift, mode=sumpf.Signal.shift_modes.CROP)
    if shift < 0:
        assert (shifted.channels()[:, 0:shift] == signal.channels()[:, -shift:]).all()
        assert (shifted.channels()[:, shift:] == 0.0).all()
    elif shift > 0:
        assert (shifted.channels()[:, 0:shift] == 0.0).all()
        assert (shifted.channels()[:, shift:] == signal.channels()[:, 0:-shift]).all()
    else:
        assert (shifted.channels() == signal.channels()).all()
    assert shifted.sampling_rate() == signal.sampling_rate()
    assert shifted.offset() == signal.offset()
    assert shifted.labels() == signal.labels()
    # mode PAD
    shifted = signal.shift(shift=shift, mode=sumpf.Signal.shift_modes.PAD)
    if shift < 0:
        assert (shifted.channels()[:, 0:signal.length()] == signal.channels()).all()
        assert (shifted.channels()[:, signal.length():] == 0.0).all()
    elif shift > 0:
        assert (shifted.channels()[:, 0:shift] == 0.0).all()
        assert (shifted.channels()[:, shift:] == signal.channels()).all()
    else:
        assert (shifted.channels() == signal.channels()).all()
    assert shifted.sampling_rate() == signal.sampling_rate()
    assert shifted.offset() == signal.offset()
    assert shifted.labels() == signal.labels()
    # mode CYCLE
    shifted = signal.shift(shift=shift, mode=sumpf.Signal.shift_modes.CYCLE)
    if shift == 0:
        assert (shifted.channels() == signal.channels()).all()
    else:
        assert (shifted.channels()[:, 0:shift] == signal.channels()[:, -shift:]).all()
        assert (shifted.channels()[:, shift:] == signal.channels()[:, 0:-shift]).all()
    assert shifted.sampling_rate() == signal.sampling_rate()
    assert shifted.offset() == signal.offset()
    assert shifted.labels() == signal.labels()

#############################
# signal processing methods #
#############################


def test_fourier_transform_results():
    """Tests the Fourier transformation of a signal by transforming impulses, whose spectrum is known."""
    # test with multiple channels
    signal = sumpf.Signal(channels=numpy.array([(1.0, 0.0, 0.0, 0.0),
                                                (0.0, 2.0, 0.0, 0.0)]),
                          sampling_rate=4.0)
    spectrum = signal.fourier_transform()
    assert spectrum.resolution() == 1.0
    assert (spectrum[0].channels() == [(1.0 + 0.0j, 1.0 + 0.0j, 1.0 + 0.0j)]).all()
    assert (spectrum[1].channels() == [(2.0 + 0.0j, 0.0 - 2.0j, -2.0 + 0.0j)]).all()
    # test with offset
    signal = sumpf.Signal(channels=numpy.array([(0.0, 0.0, 1.0, 0.0, 0.0, 0.0)]),
                          offset=-2,    # this offset should make the signal to an impulse at t=0
                          sampling_rate=3.0)
    spectrum = signal.fourier_transform()
    assert spectrum.resolution() == 0.5
    assert numpy.linalg.norm(numpy.subtract(spectrum[0].channels(),
                                            [(1.0 + 0.0j, 1.0 + 0.0j, 1.0 + 0.0j, 1.0 + 0.0j)])) < 1e-15


@hypothesis.given(tests.strategies.signals())
def test_fourier_transform_calculation(signal):
    """Does some generic tests if the Fourier transform can be computed for a variety of signals"""
    spectrum = signal.fourier_transform()
    assert len(spectrum) == len(signal)
    assert spectrum.length() == signal.length() // 2 + 1
    assert spectrum.resolution() == pytest.approx(1.0 / signal.duration())
    assert spectrum.labels() == signal.labels()


def test_block_wise_fourier_transform_with_known_signals():
    """tests the block-wise Fourier transform with signals, where it results in
    a down-sampled spectrum of the full Fourier transform."""
    l = 2 ** 16 - 2 ** 13
    for signal in (sumpf.MergeSignals([sumpf.ExponentialSweep(length=l),
                                       sumpf.GaussianNoise(length=l)]).output(),
                   sumpf.UniformNoise(length=2 ** 18) * sumpf.BlackmanWindow(length=2 ** 18)):
        for overlap in (0, 0.5):
            full_spectrum = signal.fourier_transform()
            short_spectrum = signal.fourier_transform(window=2 ** 13, overlap=overlap)
            ratio = int(round(short_spectrum.resolution() / full_spectrum.resolution()))
            downsampled = full_spectrum.channels()[:, ::ratio]
            assert short_spectrum.channels() == pytest.approx(downsampled)
            assert short_spectrum.resolution() == pytest.approx(full_spectrum.resolution() * ratio)
            assert short_spectrum.labels() == signal.labels()


def test_block_wise_fourier_transform_without_padding():
    """tests the block-wise Fourier transform without zero padding with a known signal"""
    start_frequency = 1500.0
    stop_frequency = 20000.0
    sweep = sumpf.LinearSweep(start_frequency=start_frequency, stop_frequency=stop_frequency, interval=(4096, -4096))
    fade = sumpf.Fade(rise_interval=(0, 4096), fall_interval=(-4096, 1.0))
    signal = sweep * fade
    full_spectrum = signal.fourier_transform()
    short_spectrum = signal.fourier_transform(window=4096, pad=False)
    ratio = int(round(short_spectrum.resolution() / full_spectrum.resolution()))
    downsampled = full_spectrum.channels()[:, ::ratio]
    a = int(math.ceil(start_frequency / short_spectrum.resolution()))
    b = int(math.floor(stop_frequency / short_spectrum.resolution())) - 96
    assert short_spectrum.channels()[:, a:b] == pytest.approx(downsampled[:, a:b], rel=1e-5)


@hypothesis.given(signal=tests.strategies.signals())
@hypothesis.settings(deadline=None)
def test_block_wise_fourier_transform_window_functions(signal):
    """tests the different methods for defining a window for the block-wise Fourier transform."""
    # pylint: disable=line-too-long
    # test the default parameters for overlap and pad
    assert signal.fourier_transform(window=2048) == signal.fourier_transform(window=sumpf.HannWindow(sampling_rate=signal.sampling_rate(),
                                                                                                     length=2048,
                                                                                                     symmetric=False),
                                                                             overlap=0.5,
                                                                             pad=True)
    # test, that the default window for an overlap of 0 is the rectangular window
    assert signal.fourier_transform(window=1345,
                                    overlap=0) == signal.fourier_transform(window=sumpf.RectangularWindow(sampling_rate=signal.sampling_rate(),
                                                                                                          length=1345,
                                                                                                          symmetric=False),
                                                                           overlap=0.0)
    # test defining the window as a sumpf window signal
    assert signal.fourier_transform(window=sumpf.BlackmanWindow(length=1024),
                                    pad=False) == signal.fourier_transform(window=sumpf.BlackmanWindow(length=1024),
                                                                           pad=False)
    # test defining the window as a list
    assert signal.fourier_transform(window=[0.0, 0.5, 1.0, 0.5],
                                    overlap=3) == signal.fourier_transform(window=sumpf.BartlettWindow(sampling_rate=signal.sampling_rate(),
                                                                                                       length=4,
                                                                                                       symmetric=False),
                                                                           overlap=0.75)
    # test defining the window as an ordinary signal (not a window signal), but with multiple channels
    windows = itertools.cycle([sumpf.RectangularWindow(length=2048),
                               sumpf.BartlettWindow(length=2048),
                               sumpf.HannWindow(length=2048),
                               sumpf.HammingWindow(length=2048),
                               sumpf.BlackmanWindow(length=2048)])
    window = sumpf.MergeSignals([next(windows) for _ in range(len(signal))]).output()
    spectrum = signal.fourier_transform(window=window, overlap=0.3)
    assert len(spectrum) == len(signal)
    for i in range(len(spectrum)):  # pylint: disable=consider-using-enumerate; these are SuMPF classes, for which the zip function will not work
        assert spectrum[i] == signal[i].fourier_transform(window=window[i], overlap=0.3)


@hypothesis.given(signal=tests.strategies.signals(min_channels=1, max_length=2 ** 12))
def test_block_wise_fourier_transform_rectangular_window(signal):
    """tests, that a rectangular window, that covers the full signal gives the same
    results with the block-wise Fourier transform as with the full Fourier transform."""
    spectrum = signal.fourier_transform()
    assert signal.fourier_transform(window=signal.length(), overlap=0, pad=True) == spectrum
    assert signal.fourier_transform(window=signal.length(), overlap=0, pad=False) == spectrum


def test_short_time_fourier_transform_results():
    """Tests the computation for the short time Fourier transform by finding the
    maximums in the spectrogram of an exponential sweep
    """
    try:
        import scipy.signal     # noqa; pylint: disable=unused-import; check if SciPy is available
    except ImportError:
        with pytest.raises(ImportError):
            sumpf.ExponentialSweep().short_time_fourier_transform()
    else:
        sweep = sumpf.ExponentialSweep()
        spectrogram = sweep.short_time_fourier_transform(window=2048)
        frequencies = sweep.instantaneous_frequency(spectrogram.time_samples())
        for c in spectrogram.magnitude():
            maximums = numpy.multiply(c.argmax(axis=0), spectrogram.resolution())
            diff = numpy.abs(frequencies - maximums)
            assert (diff[0:-1] <= spectrogram.resolution() * 1.2).all()


@hypothesis.given(signal=tests.strategies.signals(),    # noqa: C901; ignore the complexity warning
                  window_length=hypothesis.strategies.integers(min_value=1, max_value=8192),
                  overlap=hypothesis.strategies.floats(min_value=0.0, max_value=0.8),
                  pad=hypothesis.strategies.booleans())
def test_short_time_fourier_transform_calculation(signal, window_length, overlap, pad):
    """Does some generic tests if the short time Fourier transform can be computed
    for a variety of signals and with a variety of parameters
    """
    # pylint: disable=too-many-branches
    try:
        import scipy.signal     # noqa; pylint: disable=unused-import; check if SciPy is available
    except ImportError:
        with pytest.raises(ImportError):
            signal.short_time_fourier_transform()
    else:
        # sanitize the input data
        if signal.sampling_rate() > 1e5:
            signal = sumpf.Signal(channels=signal.channels(),
                                  sampling_rate=48000.0,
                                  offset=signal.offset(),
                                  labels=signal.labels())
        window_length = min(window_length, signal.length())
        overlap = min(sumpf_internal.index(overlap, window_length), window_length - 1)
        # create a window signal
        if window_length < 2 or overlap == 0:
            window = sumpf.RectangularWindow(sampling_rate=signal.sampling_rate(), length=window_length, symmetric=False)   # pylint: disable=line-too-long
        else:
            window = sumpf.HannWindow(sampling_rate=signal.sampling_rate(), length=window_length, symmetric=False)
        step = window_length - overlap
        # compute a reference spectrogram and test its properties
        reference = signal.short_time_fourier_transform(window=window, overlap=overlap, pad=pad)
        assert len(reference) == len(signal)
        assert reference.number_of_frequencies() == window_length // 2 + 1
        if pad:
            assert signal.length() / step <= reference.length() <= signal.length() / step + 2
        else:
            assert reference.length() == (signal.length() - window_length) // step + 1
        assert reference.resolution() == pytest.approx(1.0 / window.duration())
        assert reference.sampling_rate() == signal.sampling_rate() / step
        assert reference.offset() == int(round(signal.offset() / step))
        assert reference.labels() == signal.labels()
        # test other data types for the window and overlap parameters, that should produce the same results
        if window_length >= 2:
            assert signal.short_time_fourier_transform(window_length, overlap, pad) == reference
        for w in (window.channels(),
                  window.channels()[0],
                  tuple(window.channels()[0]),
                  [list(c) for c in window.channels()]):
            for o in (overlap - window_length,
                      overlap / window_length,
                      overlap / window_length - 1.0):
                assert signal.short_time_fourier_transform(w, o, pad) == reference
        if len(signal):     # pylint: disable=len-as-condition; signal is a sumpf.Signal and not a built in container
            multichannel = sumpf.MergeSignals([window] * len(signal)).output()
            for w in (multichannel,
                      multichannel.channels(),
                      [tuple(c) for c in multichannel.channels()]):
                for o in (overlap - window_length,
                          overlap / window_length,
                          overlap / window_length - 1.0):
                    assert signal.short_time_fourier_transform(w, o, pad) == reference


def test_level_manual():
    """tests the level computation of some known signals"""
    sine = sumpf.SineWave(length=48000)
    assert sine.level() == pytest.approx([0.5 ** 0.5])
    square = sumpf.SquareWave(phase=0.1)
    assert square.level() == pytest.approx([1.0])


@hypothesis.given(tests.strategies.signals())
def test_level(signal):
    """Tests the level computation from the Signal class."""
    # compute the level for each channel
    reference = numpy.sqrt(numpy.mean(numpy.square(signal.channels()), axis=1))
    level = signal.level()
    assert len(level) == len(signal)
    assert level == pytest.approx(reference)
    # compute a scalar level value
    reference = numpy.sqrt(numpy.mean(numpy.square(signal.channels())))
    assert signal.level(single_value=True) == pytest.approx(reference)

####################################################
# methods for statistical parameters of the signal #
####################################################


@hypothesis.given(tests.strategies.signals())
def test_mean(signal):
    """Tests the computation the mean from the Signal class."""
    # compute the mean for each channel
    reference = numpy.mean(signal.channels(), axis=1)
    mean = signal.mean()
    assert len(mean) == len(signal)
    assert (mean == reference).all()
    # compute a scalar value for the whole signal
    assert signal.mean(single_value=True) == numpy.mean(signal.channels())


@hypothesis.given(tests.strategies.signals())
def test_standard_deviation(signal):
    """Tests the computation the standard deviation from the Signal class."""
    # compute the standard deviation for each channel
    reference = numpy.std(signal.channels(), axis=1)
    standard_deviation = signal.standard_deviation()
    assert len(standard_deviation) == len(signal)
    assert (standard_deviation == reference).all()
    # compute a scalar value for the whole signal
    assert signal.standard_deviation(single_value=True) == numpy.std(signal.channels())


@hypothesis.given(tests.strategies.signals())
def test_variance(signal):
    """Tests the computation the variance from the Signal class."""
    # compute the variance for each channel
    reference = numpy.var(signal.channels(), axis=1)
    variance = signal.variance()
    assert len(variance) == len(signal)
    assert (variance == reference).all()
    # compute a scalar value for the whole signal
    assert signal.variance(single_value=True) == numpy.var(signal.channels())


@hypothesis.given(tests.strategies.signals())
def test_skewness(signal):
    """Tests the computation the skewness from the Signal class."""
    try:
        import scipy.stats
    except ImportError:
        with pytest.raises(ImportError):
            signal.skewness()
    else:
        # compute the skewness for each channel
        reference = scipy.stats.skew(signal.channels(), axis=1)
        skewness = signal.skewness()
        assert len(skewness) == len(signal)
        assert (skewness == reference).all()
        # compute a scalar value for the whole signal
        assert signal.skewness(single_value=True) == scipy.stats.skew(signal.channels(), axis=None)


@hypothesis.given(tests.strategies.signals(min_value=-1e15, max_value=1e15))
def test_kurtosis(signal):
    """Tests the computation the kurtosis from the Signal class."""
    try:
        import scipy.stats
    except ImportError:
        with pytest.raises(ImportError):
            signal.kurtosis()
    else:
        # compute the kurtosis for each channel
        reference = scipy.stats.kurtosis(signal.channels(), axis=1)
        kurtosis = signal.kurtosis()
        assert len(kurtosis) == len(signal)
        assert (kurtosis == reference).all()
        # compute a scalar value for the whole signal
        assert signal.kurtosis(single_value=True) == scipy.stats.kurtosis(signal.channels(), axis=None)
