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

"""Tests for the Spectrogram class"""

import copy
import logging
import os
import tempfile
import numpy
import hypothesis
import pytest
import sumpf
from sumpf._internal import spectrogram_readers, spectrogram_writers
import tests

###########################################
# overloaded operators (non math-related) #
###########################################


def test_getitem_channels():
    """Tests the slicing of a spectrogram's channels with the ``[]`` overload"""
    spectrogram = sumpf.Spectrogram(channels=numpy.array([[(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)],
                                                          [(2.0, 0.0, 0.0), (0.0, 2.0, 0.0), (0.0, 0.0, 2.0)],
                                                          [(3.0, 0.0, 0.0), (0.0, 3.0, 0.0), (0.0, 0.0, 3.0)]]),
                                    offset=1,
                                    labels=("one", "two", "three"))
    # integer
    sliced = spectrogram[1]
    assert (sliced.channels() == [(2.0, 0.0, 0.0), (0.0, 2.0, 0.0), (0.0, 0.0, 2.0)]).all()
    assert sliced.offset() == spectrogram.offset()
    assert sliced.labels() == ("two",)
    # float
    assert spectrogram[0.5] == spectrogram[1]
    # integer slice
    sliced = spectrogram[1:3]
    assert (sliced.channels() == [[(2.0, 0.0, 0.0), (0.0, 2.0, 0.0), (0.0, 0.0, 2.0)],
                                  [(3.0, 0.0, 0.0), (0.0, 3.0, 0.0), (0.0, 0.0, 3.0)]]).all()
    assert sliced.offset() == spectrogram.offset()
    assert sliced.labels() == ("two", "three")
    # integer slice with step
    sliced = spectrogram[0:3:2]
    assert (sliced.channels() == [[(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)],
                                  [(3.0, 0.0, 0.0), (0.0, 3.0, 0.0), (0.0, 0.0, 3.0)]]).all()
    assert sliced.offset() == spectrogram.offset()
    assert sliced.labels() == ("one", "three")
    # incomplete slices
    assert spectrogram[:] == spectrogram
    assert spectrogram[:2] == spectrogram[0:2]
    assert spectrogram[1:] == spectrogram[1:3]
    assert spectrogram[0::2] == spectrogram[0:3:2]
    # # float slices
    assert spectrogram[0.33:1.0] == spectrogram[1:3]
    assert spectrogram[0:3:0.66] == spectrogram[0:3:2]
    # # negative slices
    assert spectrogram[0:-1] == spectrogram[0:2]
    assert spectrogram[-2:] == spectrogram[1:3]
    sliced = spectrogram[::-1]
    assert (sliced.channels() == [[(3.0, 0.0, 0.0), (0.0, 3.0, 0.0), (0.0, 0.0, 3.0)],
                                  [(2.0, 0.0, 0.0), (0.0, 2.0, 0.0), (0.0, 0.0, 2.0)],
                                  [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]]).all()
    assert sliced.offset() == spectrogram.offset()
    assert sliced.labels() == ("three", "two", "one")
    assert spectrogram[-0.99:-0.01:-0.66] == spectrogram[0:3:-2]


def test_getitem_frequency_bins():
    """Tests the slicing of a spectrogram's frequency bins with the ``[]`` overload"""
    spectrogram = sumpf.Spectrogram(channels=numpy.array([[(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)],
                                                          [(2.0, 0.0, 0.0), (0.0, 2.0, 0.0), (0.0, 0.0, 2.0)],
                                                          [(3.0, 0.0, 0.0), (0.0, 3.0, 0.0), (0.0, 0.0, 3.0)]]),
                                    offset=1,
                                    labels=("one", "two", "three"))
    # integer
    sliced = spectrogram[1, 1]
    assert (sliced.channels() == [[(0.0, 2.0, 0.0)]]).all()
    assert sliced.offset() == spectrogram.offset()
    assert sliced.labels() == ("two",)
    # float
    assert spectrogram[:, 0.5] == spectrogram[:, 1]
    # integer slice
    sliced = spectrogram[1:3, 1:3]
    assert (sliced.channels() == [[(0.0, 2.0, 0.0), (0.0, 0.0, 2.0)],
                                  [(0.0, 3.0, 0.0), (0.0, 0.0, 3.0)]]).all()
    assert sliced.offset() == spectrogram.offset()
    assert sliced.labels() == ("two", "three")
    # integer slice with step
    sliced = spectrogram[:, 0:3:2]
    assert (sliced.channels() == [[(1.0, 0.0, 0.0), (0.0, 0.0, 1.0)],
                                  [(2.0, 0.0, 0.0), (0.0, 0.0, 2.0)],
                                  [(3.0, 0.0, 0.0), (0.0, 0.0, 3.0)]]).all()
    assert sliced.offset() == spectrogram.offset()
    assert sliced.labels() == ("one", "two", "three")
    # incomplete slices
    assert spectrogram[:, :] == spectrogram
    assert spectrogram[:2, :1] == spectrogram[0:2, 0]
    assert spectrogram[1:, 2:] == spectrogram[1:3, 2]
    assert spectrogram[0::2, 0::2] == spectrogram[0:3:2, 0:3:2]
    # float slices
    assert spectrogram[0.33:1.0, 0.0:0.66] == spectrogram[1:3, 0:2]
    assert spectrogram[0:3:0.66, 0.0:1.0:0.66] == spectrogram[0:3:2, 0:3:2]
    # negative slices
    assert spectrogram[0:-2, 0:-1] == spectrogram[0, 0:2]
    assert spectrogram[-2:, -1:] == spectrogram[1:3, 2]
    sliced = spectrogram[::-1, ::-1]
    assert (sliced.channels() == [[(0.0, 0.0, 3.0), (0.0, 3.0, 0.0), (3.0, 0.0, 0.0)],
                                  [(0.0, 0.0, 2.0), (0.0, 2.0, 0.0), (2.0, 0.0, 0.0)],
                                  [(0.0, 0.0, 1.0), (0.0, 1.0, 0.0), (1.0, 0.0, 0.0)]]).all()
    assert sliced.offset() == spectrogram.offset()
    assert sliced.labels() == ("three", "two", "one")
    assert spectrogram[-0.99:-0.01:-0.66, -0.99:-0.01:-0.66] == spectrogram[0:3:-2, 0:3:-2]


def test_getitem_samples():
    """Tests the slicing of a spectrogram with the ``[]`` overload"""
    spectrogram = sumpf.Spectrogram(channels=numpy.array([[(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)],
                                                          [(2.0, 0.0, 0.0), (0.0, 2.0, 0.0), (0.0, 0.0, 2.0)],
                                                          [(3.0, 0.0, 0.0), (0.0, 3.0, 0.0), (0.0, 0.0, 3.0)]]),
                                    offset=1,
                                    labels=("one", "two", "three"))
    # integer
    sliced = spectrogram[1, 1, 1]
    assert (sliced.channels() == [[(2.0,)]]).all()
    assert sliced.offset() == spectrogram.offset() + 1
    assert sliced.labels() == ("two",)
    # float
    assert spectrogram[:, 0.5, 0.8] == spectrogram[:, 1, 2]
    # integer slice
    sliced = spectrogram[1:3, 1:3, 1:3]
    assert (sliced.channels() == [[(2.0, 0.0), (0.0, 2.0)],
                                  [(3.0, 0.0), (0.0, 3.0)]]).all()
    assert sliced.offset() == spectrogram.offset() + 1
    assert sliced.labels() == ("two", "three")
    # integer slice with step
    sliced = spectrogram[:, :, 0:3:2]
    assert (sliced.channels() == [[(1.0, 0.0), (0.0, 0.0), (0.0, 1.0)],
                                  [(2.0, 0.0), (0.0, 0.0), (0.0, 2.0)],
                                  [(3.0, 0.0), (0.0, 0.0), (0.0, 3.0)]]).all()
    assert sliced.offset() == spectrogram.offset()
    assert sliced.labels() == ("one", "two", "three")
    # incomplete slices
    assert spectrogram[:, :, :] == spectrogram
    assert spectrogram[:2, :2, :1] == spectrogram[0:2, 0:2, 0]
    assert spectrogram[1:, 1:, 2:] == spectrogram[1:3, 1:3, 2]
    assert spectrogram[0::2, 0::2, 0::2] == spectrogram[0:3:2, 0:3:2, 0:3:2]
    # float slices
    assert spectrogram[0.33:1.0, 0.0:0.66, 0.33:0.66] == spectrogram[1:3, 0:2, 1]
    assert spectrogram[0:3:0.66, 0.0:1.0:0.66, 0.0:1.0:0.66] == spectrogram[0:3:2, 0:3:2, 0:3:2]
    # negative slices
    assert spectrogram[0:-2, 0:-1, 0:-2] == spectrogram[0, 0:2, 0]
    assert spectrogram[-2:, -1:, -2:] == spectrogram[1:3, 2, 1:3]
    sliced = spectrogram[::-1, ::-1, ::-1]
    assert (sliced.channels() == [[(3.0, 0.0, 0.0), (0.0, 3.0, 0.0), (0.0, 0.0, 3.0)],
                                  [(2.0, 0.0, 0.0), (0.0, 2.0, 0.0), (0.0, 0.0, 2.0)],
                                  [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]]).all()
    assert sliced.offset() == spectrogram.offset()
    assert sliced.labels() == ("three", "two", "one")
    assert spectrogram[-0.99:-0.01:-0.66, -0.99:-0.01:-0.66, -0.99:-0.01:-0.66] == spectrogram[0:3:-2, 0:3:-2, 0:3:-2]


@hypothesis.given(tests.strategies.spectrograms())
def test_str(spectrogram):
    """Checks if casting a Spectrogram instance to a string raises an error."""
    logging.info(str(spectrogram))


@hypothesis.given(tests.strategies.spectrograms())
def test_repr(spectrogram):
    """Checks if a spectrogram can be restored from its string representation."""
    # required symbols for the evaluation of the repr-string
    array = numpy.array                 # noqa
    complex128 = numpy.complex128       # noqa
    Spectrogram = sumpf.Spectrogram     # noqa
    # create a spectrogram, cast it to a string and restore it from the string
    restored = eval(repr(spectrogram))   # pylint: disable=eval-used
    assert restored == spectrogram


@hypothesis.given(tests.strategies.spectrogram_parameters())
def test_eq(parameters):
    """Tests the operator overloads for ``==`` and ``!=``."""
    spectrogram1 = sumpf.Spectrogram(**parameters)
    spectrogram2 = sumpf.Spectrogram(**parameters)
    assert spectrogram1 is not spectrogram2
    assert spectrogram1 == spectrogram2
    if spectrogram2.length() > 1:
        assert spectrogram1 != spectrogram2[:, :, 0:-1]  # test for a case, where the NumPy comparison of the channels returns a boolean rather than an array of booleans
    assert spectrogram1 != (spectrogram2 + spectrogram2) * spectrogram2
    assert spectrogram1 != spectrogram1.channels()


@hypothesis.given(tests.strategies.spectrogram_parameters())
def test_hash(parameters):
    """Tests the operator overload for hashing a spectrogram with the builtin :func:`hash` function."""
    parameters2 = copy.copy(parameters)
    parameters2["channels"] = numpy.empty(shape=parameters["channels"].shape, dtype=numpy.complex128)
    parameters2["channels"][:] = parameters["channels"][:]
    spectrogram1 = sumpf.Spectrogram(**parameters)
    spectrogram2 = sumpf.Spectrogram(**parameters2)
    spectrogram3 = (spectrogram2 + spectrogram2) * spectrogram2
    assert spectrogram1.channels() is not spectrogram2.channels()
    assert hash(spectrogram1) == hash(spectrogram2)
    assert hash(spectrogram1) != hash(spectrogram3)

###################################
# overloaded unary math operators #
###################################


@hypothesis.given(tests.strategies.spectrograms())
def test_absolute(spectrogram):
    """Tests if computing the absolute of a spectrogram yields the expected result."""
    assert abs(spectrogram) == sumpf.Spectrogram(channels=numpy.absolute(spectrogram.channels()),
                                                 resolution=spectrogram.resolution(),
                                                 sampling_rate=spectrogram.sampling_rate(),
                                                 offset=spectrogram.offset(),
                                                 labels=spectrogram.labels())


@hypothesis.given(tests.strategies.spectrograms())
def test_negative(spectrogram):
    """Tests if computing the negative of a spectrogram yields the expected result."""
    assert -spectrogram == sumpf.Spectrogram(channels=numpy.subtract(0.0, spectrogram.channels()),
                                             resolution=spectrogram.resolution(),
                                             sampling_rate=spectrogram.sampling_rate(),
                                             offset=spectrogram.offset(),
                                             labels=spectrogram.labels())

####################################
# overloaded binary math operators #
####################################


def test_add():
    """Tests the overload of the ``+`` operator."""
    # pylint: disable=line-too-long; these matrices are more readable, when the channels are in one line
    spectrogram1 = sumpf.Spectrogram(channels=numpy.array([[(1.0, 0.0, 0.0), (0.1, 0.0, 0.0)],
                                                           [(0.0, 2.0, 0.0), (0.0, 0.2, 0.0)]]),
                                     offset=1,
                                     labels=("one1", "two1"))
    spectrogram2 = sumpf.Spectrogram(channels=numpy.array([[(1.0, 0.0, 0.0), (0.1, 0.0, 0.0)],
                                                           [(0.0, 2.0, 0.0), (0.0, 0.2, 0.0)],
                                                           [(0.0, 0.0, 3.0), (0.0, 0.0, 0.3)]]),
                                     offset=-1,
                                     labels=("one2", "two2", "three2"))
    # test adding a number
    sum_ = spectrogram1 + 3.7
    assert sum_.offset() == spectrogram1.offset()
    assert sum_.resolution() == spectrogram1.resolution()
    assert sum_.sampling_rate() == spectrogram1.sampling_rate()
    assert sum_.labels() == spectrogram1.labels()
    assert (sum_.channels() == numpy.add(spectrogram1.channels(), 3.7)).all()
    assert ((3.7 + spectrogram1).channels() == sum_.channels()).all()
    # test adding an array
    sum_ = spectrogram1 + (1.9, -3.8, 5.5)
    assert sum_.offset() == spectrogram1.offset()
    assert sum_.resolution() == spectrogram1.resolution()
    assert sum_.sampling_rate() == spectrogram1.sampling_rate()
    assert sum_.labels() == spectrogram1.labels()
    assert (sum_.channels() == numpy.add(spectrogram1.channels(), (1.9, -3.8, 5.5))).all()
    assert (((1.9, -3.8, 5.5) + spectrogram1).channels() == sum_.channels()).all()
    # test adding a fully overlapping spectrogram
    sum_ = spectrogram1 + spectrogram1
    assert sum_.offset() == spectrogram1.offset()
    assert sum_.resolution() == spectrogram1.resolution()
    assert sum_.sampling_rate() == spectrogram1.sampling_rate()
    assert sum_.labels() == ("Sum",) * 2
    assert (sum_.channels() == numpy.multiply(spectrogram1.channels(), 2)).all()
    # test adding a fully overlapping single channel spectrogram
    sum_ = spectrogram1 + spectrogram1[1]
    assert sum_.offset() == spectrogram1.offset()
    assert sum_.resolution() == spectrogram1.resolution()
    assert sum_.sampling_rate() == spectrogram1.sampling_rate()
    assert sum_.labels() == ("Sum",) * 2
    assert (sum_.channels() == numpy.add(spectrogram1.channels(), spectrogram1[1].channels())).all()
    assert ((spectrogram1[1] + spectrogram1).channels() == sum_.channels()).all()
    # test adding a partially overlapping spectrogram
    sum_ = spectrogram1 + spectrogram2
    assert sum_.offset() == -1
    assert sum_.resolution() == spectrogram1.resolution()
    assert sum_.sampling_rate() == spectrogram1.sampling_rate()
    assert sum_.labels() == ("Sum",) * 3
    assert (sum_.channels() == [[(1.0, 0.0, 1.0, 0.0, 0.0), (0.1, 0.0, 0.1, 0.0, 0.0)],
                                [(0.0, 2.0, 0.0, 2.0, 0.0), (0.0, 0.2, 0.0, 0.2, 0.0)],
                                [(0.0, 0.0, 3.0, 0.0, 0.0), (0.0, 0.0, 0.3, 0.0, 0.0)]]).all()
    assert ((spectrogram2 + spectrogram1).channels() == sum_.channels()).all()
    # test adding a partially overlapping single channel spectrogram
    sum_ = spectrogram1 + spectrogram2[2]
    assert sum_.offset() == -1
    assert sum_.resolution() == spectrogram1.resolution()
    assert sum_.sampling_rate() == spectrogram1.sampling_rate()
    assert sum_.labels() == ("Sum",) * 2
    assert (sum_.channels() == [[(0.0, 0.0, 4.0, 0.0, 0.0), (0.0, 0.0, 0.4, 0.0, 0.0)],
                                [(0.0, 0.0, 3.0, 2.0, 0.0), (0.0, 0.0, 0.3, 0.2, 0.0)]]).all()
    assert ((spectrogram2[2] + spectrogram1).channels() == sum_.channels()).all()


def test_subtract():
    """Tests the overload of the ``-`` operator."""
    # pylint: disable=line-too-long; these matrices are more readable, when the channels are in one line
    spectrogram1 = sumpf.Spectrogram(channels=numpy.array([[(1.0, 0.0, 0.0), (0.1, 0.0, 0.0)],
                                                           [(0.0, 2.0, 0.0), (0.0, 0.2, 0.0)]]),
                                     offset=1,
                                     labels=("one1", "two1"))
    spectrogram2 = sumpf.Spectrogram(channels=numpy.array([[(1.0, 0.0, 0.0), (0.1, 0.0, 0.0)],
                                                           [(0.0, 2.0, 0.0), (0.0, 0.2, 0.0)],
                                                           [(0.0, 0.0, 3.0), (0.0, 0.0, 0.3)]]),
                                     offset=-1,
                                     labels=("one2", "two2", "three2"))
    # test subtracting a number
    difference = spectrogram1 - 3.7
    assert difference.offset() == spectrogram1.offset()
    assert difference.resolution() == spectrogram1.resolution()
    assert difference.sampling_rate() == spectrogram1.sampling_rate()
    assert difference.labels() == spectrogram1.labels()
    assert (difference.channels() == numpy.subtract(spectrogram1.channels(), 3.7)).all()
    assert ((3.7 - spectrogram1).channels() == numpy.negative(difference.channels())).all()
    # test subtracting an array
    difference = spectrogram1 - (1.9, -3.8, 5.5)
    assert difference.offset() == spectrogram1.offset()
    assert difference.resolution() == spectrogram1.resolution()
    assert difference.sampling_rate() == spectrogram1.sampling_rate()
    assert difference.labels() == spectrogram1.labels()
    assert (difference.channels() == numpy.subtract(spectrogram1.channels(), (1.9, -3.8, 5.5))).all()
    assert (((1.9, -3.8, 5.5) - spectrogram1).channels() == numpy.negative(difference.channels())).all()
    # test subtracting a fully overlapping spectrogram
    difference = spectrogram1 - spectrogram1
    assert difference.offset() == spectrogram1.offset()
    assert difference.resolution() == spectrogram1.resolution()
    assert difference.sampling_rate() == spectrogram1.sampling_rate()
    assert difference.labels() == ("Difference",) * 2
    assert (difference.channels() == 0.0).all()
    # test subtracting a fully overlapping single channel spectrogram
    difference = spectrogram1 - spectrogram1[1]
    assert difference.offset() == spectrogram1.offset()
    assert difference.resolution() == spectrogram1.resolution()
    assert difference.sampling_rate() == spectrogram1.sampling_rate()
    assert difference.labels() == ("Difference",) * 2
    assert (difference.channels() == numpy.subtract(spectrogram1.channels(), spectrogram1[1].channels())).all()
    assert ((spectrogram1[1] - spectrogram1).channels() == numpy.negative(difference.channels())).all()
    # test subtracting a partially overlapping spectrogram
    difference = spectrogram1 - spectrogram2
    assert difference.offset() == -1
    assert difference.resolution() == spectrogram1.resolution()
    assert difference.sampling_rate() == spectrogram1.sampling_rate()
    assert difference.labels() == ("Difference",) * 3
    assert (difference.channels() == [[(-1.0, 0.0, 1.0, 0.0, 0.0), (-0.1, 0.0, 0.1, 0.0, 0.0)],
                                      [(0.0, -2.0, 0.0, 2.0, 0.0), (0.0, -0.2, 0.0, 0.2, 0.0)],
                                      [(0.0, 0.0, -3.0, 0.0, 0.0), (0.0, 0.0, -0.3, 0.0, 0.0)]]).all()
    assert ((spectrogram2 - spectrogram1).channels() == numpy.negative(difference.channels())).all()
    # test subtracting a partially overlapping single channel spectrogram
    difference = spectrogram1 - spectrogram2[2]
    assert difference.offset() == -1
    assert difference.resolution() == spectrogram1.resolution()
    assert difference.sampling_rate() == spectrogram1.sampling_rate()
    assert difference.labels() == ("Difference",) * 2
    assert (difference.channels() == [[(0.0, 0.0, -2.0, 0.0, 0.0), (0.0, 0.0, 0.1 - 0.3, 0.0, 0.0)],
                                      [(0.0, 0.0, -3.0, 2.0, 0.0), (0.0, 0.0, -0.3, 0.2, 0.0)]]).all()
    assert ((spectrogram2[2] - spectrogram1).channels() == numpy.negative(difference.channels())).all()


def test_multiply():
    """Tests the overload of the ``*`` operator."""
    # pylint: disable=line-too-long; these matrices are more readable, when the channels are in one line
    spectrogram1 = sumpf.Spectrogram(channels=numpy.array([[(2.0, 1.0, 1.0), (0.2, 1.0, 1.0)],
                                                           [(1.0, 3.0, 1.0), (1.0, 0.3, 1.0)]]),
                                     offset=1,
                                     labels=("one1", "two1"))
    spectrogram2 = sumpf.Spectrogram(channels=numpy.array([[(2.0, 1.0, 1.0), (0.2, 1.0, 1.0)],
                                                           [(1.0, 3.0, 1.0), (1.0, 0.3, 1.0)],
                                                           [(1.0, 1.0, 4.0), (1.0, 1.0, 0.4)]]),
                                     offset=-1,
                                     labels=("one2", "two2", "three2"))
    # test multiplying with number
    product = spectrogram1 * 3.7
    assert product.offset() == spectrogram1.offset()
    assert product.resolution() == spectrogram1.resolution()
    assert product.sampling_rate() == spectrogram1.sampling_rate()
    assert product.labels() == spectrogram1.labels()
    assert (product.channels() == numpy.multiply(spectrogram1.channels(), 3.7)).all()
    assert ((3.7 * spectrogram1).channels() == product.channels()).all()
    # test multiplying with an array
    product = spectrogram1 * (1.9, -3.8, 5.5)
    assert product.offset() == spectrogram1.offset()
    assert product.resolution() == spectrogram1.resolution()
    assert product.sampling_rate() == spectrogram1.sampling_rate()
    assert product.labels() == spectrogram1.labels()
    assert (product.channels() == numpy.multiply(spectrogram1.channels(), (1.9, -3.8, 5.5))).all()
    assert (((1.9, -3.8, 5.5) * spectrogram1).channels() == product.channels()).all()
    # test multiplying with a fully overlapping spectrogram
    product = spectrogram1 * spectrogram1
    assert product.offset() == spectrogram1.offset()
    assert product.resolution() == spectrogram1.resolution()
    assert product.sampling_rate() == spectrogram1.sampling_rate()
    assert product.labels() == ("Product",) * 2
    assert (product.channels() == numpy.square(spectrogram1.channels())).all()
    # test multiplying with a fully overlapping single channel spectrogram
    product = spectrogram1 * spectrogram1[1]
    assert product.offset() == spectrogram1.offset()
    assert product.resolution() == spectrogram1.resolution()
    assert product.sampling_rate() == spectrogram1.sampling_rate()
    assert product.labels() == ("Product",) * 2
    assert (product.channels() == numpy.multiply(spectrogram1.channels(), spectrogram1[1].channels())).all()
    assert ((spectrogram1[1] * spectrogram1).channels() == product.channels()).all()
    # test multiplying with a partially overlapping spectrogram
    product = spectrogram1 * spectrogram2
    assert product.offset() == -1
    assert product.resolution() == spectrogram1.resolution()
    assert product.sampling_rate() == spectrogram1.sampling_rate()
    assert product.labels() == ("Product",) * 3
    assert (product.channels() == [[(2.0, 1.0, 2.0, 1.0, 1.0), (0.2, 1.0, 0.2, 1.0, 1.0)],
                                   [(1.0, 3.0, 1.0, 3.0, 1.0), (1.0, 0.3, 1.0, 0.3, 1.0)],
                                   [(1.0, 1.0, 4.0, 0.0, 0.0), (1.0, 1.0, 0.4, 0.0, 0.0)]]).all()
    assert ((spectrogram2 * spectrogram1).channels() == product.channels()).all()
    # test multiplying with a partially overlapping single channel spectrogram
    product = spectrogram1 * spectrogram2[2]
    assert product.offset() == -1
    assert product.resolution() == spectrogram1.resolution()
    assert product.sampling_rate() == spectrogram1.sampling_rate()
    assert product.labels() == ("Product",) * 2
    assert (product.channels() == [[(1.0, 1.0, 8.0, 1.0, 1.0), (1.0, 1.0, 0.4 * 0.2, 1.0, 1.0)],
                                   [(1.0, 1.0, 4.0, 3.0, 1.0), (1.0, 1.0, 0.4, 0.3, 1.0)]]).all()
    assert ((spectrogram2[2] * spectrogram1).channels() == product.channels()).all()


def test_divide():
    """Tests the overload of the ``/`` operator."""
    # pylint: disable=line-too-long; these matrices are more readable, when the channels are in one line
    spectrogram1 = sumpf.Spectrogram(channels=numpy.array([[(2.0, 1.0, 1.0), (0.2, 1.0, 1.0)],
                                                           [(1.0, 4.0, 1.0), (1.0, 0.4, 1.0)]]),
                                     offset=1,
                                     labels=("one1", "two1"))
    spectrogram2 = sumpf.Spectrogram(channels=numpy.array([[(2.0, 1.0, 1.0), (0.2, 1.0, 1.0)],
                                                           [(1.0, 4.0, 1.0), (1.0, 0.4, 1.0)],
                                                           [(1.0, 1.0, 8.0), (1.0, 1.0, 0.8)]]),
                                     offset=-1,
                                     labels=("one2", "two2", "three2"))
    # test dividing by number
    quotient = spectrogram1 / 3.7
    assert quotient.offset() == spectrogram1.offset()
    assert quotient.resolution() == spectrogram1.resolution()
    assert quotient.sampling_rate() == spectrogram1.sampling_rate()
    assert quotient.labels() == spectrogram1.labels()
    assert (quotient.channels() == numpy.divide(spectrogram1.channels(), 3.7)).all()
    assert ((3.7 / spectrogram1).channels() == numpy.divide(3.7, spectrogram1.channels())).all()
    # test dividing by an array
    quotient = spectrogram1 / (1.9, -3.8, 5.5)
    assert quotient.offset() == spectrogram1.offset()
    assert quotient.resolution() == spectrogram1.resolution()
    assert quotient.sampling_rate() == spectrogram1.sampling_rate()
    assert quotient.labels() == spectrogram1.labels()
    assert (quotient.channels() == numpy.divide(spectrogram1.channels(), (1.9, -3.8, 5.5))).all()
    assert (((1.9, -3.8, 5.5) / spectrogram1).channels() == numpy.divide((1.9, -3.8, 5.5), spectrogram1.channels())).all()
    # test dividing by a fully overlapping spectrogram
    quotient = spectrogram1 / spectrogram1
    assert quotient.offset() == spectrogram1.offset()
    assert quotient.resolution() == spectrogram1.resolution()
    assert quotient.sampling_rate() == spectrogram1.sampling_rate()
    assert quotient.labels() == ("Quotient",) * 2
    assert (quotient.channels() == numpy.ones(shape=spectrogram1.shape())).all()
    # test dividing by a fully overlapping single channel spectrogram
    quotient = spectrogram1 / spectrogram1[1]
    assert quotient.offset() == spectrogram1.offset()
    assert quotient.resolution() == spectrogram1.resolution()
    assert quotient.sampling_rate() == spectrogram1.sampling_rate()
    assert quotient.labels() == ("Quotient",) * 2
    assert (quotient.channels() == numpy.divide(spectrogram1.channels(), spectrogram1[1].channels())).all()
    assert ((spectrogram1[1] / spectrogram1).channels() == numpy.divide(spectrogram1[1].channels(), spectrogram1.channels())).all()
    # test dividing by a partially overlapping spectrogram
    quotient = spectrogram1 / spectrogram2
    assert quotient.offset() == -1
    assert quotient.resolution() == spectrogram1.resolution()
    assert quotient.sampling_rate() == spectrogram1.sampling_rate()
    assert quotient.labels() == ("Quotient",) * 3
    assert (quotient.channels() == [[(0.5, 1.0, 2.0, 1.0, 1.0), (5.0, 1.0, 0.2, 1.0, 1.0)],
                                    [(1.0, 0.25, 1.0, 4.0, 1.0), (1.0, 2.5, 1.0, 0.4, 1.0)],
                                    [(1.0, 1.0, 0.125, 0.0, 0.0), (1.0, 1.0, 1.25, 0.0, 0.0)]]).all()
    assert ((spectrogram2 / spectrogram1).channels() == [[(2.0, 1.0, 0.5, 1.0, 1.0), (0.2, 1.0, 5.0, 1.0, 1.0)],
                                                         [(1.0, 4.0, 1.0, 0.25, 1.0), (1.0, 0.4, 1.0, 2.5, 1.0)],
                                                         [(1.0, 1.0, 8.0, 0.0, 0.0), (1.0, 1.0, 0.8, 0.0, 0.0)]]).all()
    # test dividing by a partially overlapping single channel spectrogram
    quotient = spectrogram1 / spectrogram2[2]
    assert quotient.offset() == -1
    assert quotient.resolution() == spectrogram1.resolution()
    assert quotient.sampling_rate() == spectrogram1.sampling_rate()
    assert quotient.labels() == ("Quotient",) * 2
    assert (quotient.channels() == [[(1.0, 1.0, 0.25, 1.0, 1.0), (1.0, 1.0, 0.25, 1.0, 1.0)],
                                    [(1.0, 1.0, 0.125, 4.0, 1.0), (1.0, 1.0, 1.25, 0.4, 1.0)]]).all()
    assert ((spectrogram2[2] / spectrogram1).channels() == [[(1.0, 1.0, 4.0, 1.0, 1.0), (1.0, 1.0, 4.0, 1.0, 1.0)],
                                                            [(1.0, 1.0, 8.0, 0.25, 1.0), (1.0, 1.0, 0.8, 2.5, 1.0)]]).all()


def test_power():
    """Tests the overload of the ``**`` operator."""
    # pylint: disable=line-too-long; these matrices are more readable, when the channels are in one line
    spectrogram1 = sumpf.Spectrogram(channels=numpy.array([[(2.0, 1.0, 1.0), (5.0, 1.0, 1.0)],
                                                           [(1.0, 3.0, 1.0), (1.0, 6.0, 1.0)]]),
                                     offset=1,
                                     labels=("one1", "two1"))
    spectrogram2 = sumpf.Spectrogram(channels=numpy.array([[(2.0, 1.0, 1.0), (5.0, 1.0, 1.0)],
                                                           [(1.0, 3.0, 1.0), (1.0, 6.0, 1.0)],
                                                           [(1.0, 1.0, 4.0), (1.0, 1.0, 7.0)]]),
                                     offset=-1,
                                     labels=("one2", "two2", "three2"))
    # test multiplying with number
    power = spectrogram1 ** 3.7
    assert power.offset() == spectrogram1.offset()
    assert power.resolution() == spectrogram1.resolution()
    assert power.sampling_rate() == spectrogram1.sampling_rate()
    assert power.labels() == spectrogram1.labels()
    assert (power.channels() == numpy.power(spectrogram1.channels(), 3.7)).all()
    assert ((3.7 ** spectrogram1).channels() == numpy.power(3.7, spectrogram1.channels())).all()
    # test multiplying with an array
    power = spectrogram1 ** (1.9, -3.8, 5.5)
    assert power.offset() == spectrogram1.offset()
    assert power.resolution() == spectrogram1.resolution()
    assert power.sampling_rate() == spectrogram1.sampling_rate()
    assert power.labels() == spectrogram1.labels()
    assert (power.channels() == numpy.power(spectrogram1.channels(), (1.9, -3.8, 5.5))).all()
    assert (((1.9, -3.8, 5.5) ** spectrogram1).channels() == numpy.power((1.9, -3.8, 5.5), spectrogram1.channels())).all()
    # test multiplying with a fully overlapping spectrogram
    power = spectrogram1 ** spectrogram1
    assert power.offset() == spectrogram1.offset()
    assert power.resolution() == spectrogram1.resolution()
    assert power.sampling_rate() == spectrogram1.sampling_rate()
    assert power.labels() == ("Power",) * 2
    assert (power.channels() == numpy.power(spectrogram1.channels(), spectrogram1.channels())).all()
    # test multiplying with a fully overlapping single channel spectrogram
    power = spectrogram1 ** spectrogram1[1]
    assert power.offset() == spectrogram1.offset()
    assert power.resolution() == spectrogram1.resolution()
    assert power.sampling_rate() == spectrogram1.sampling_rate()
    assert power.labels() == ("Power",) * 2
    assert (power.channels() == numpy.power(spectrogram1.channels(), spectrogram1[1].channels())).all()
    assert ((spectrogram1[1] ** spectrogram1).channels() == numpy.power(spectrogram1[1].channels(), spectrogram1.channels())).all()
    # test multiplying with a partially overlapping spectrogram
    power = spectrogram1 ** spectrogram2
    assert power.offset() == -1
    assert power.resolution() == spectrogram1.resolution()
    assert power.sampling_rate() == spectrogram1.sampling_rate()
    assert power.labels() == ("Power",) * 3
    assert (power.channels() == [[(2.0, 1.0, 2.0, 1.0, 1.0), (5.0, 1.0, 5.0, 1.0, 1.0)],
                                 [(1.0, 3.0, 1.0, 3.0, 1.0), (1.0, 6.0, 1.0, 6.0, 1.0)],
                                 [(1.0, 1.0, 4.0, 0.0, 0.0), (1.0, 1.0, 7.0, 0.0, 0.0)]]).all()
    assert ((spectrogram2 ** spectrogram1).channels() == [[(2.0, 1.0, 1.0, 1.0, 1.0), (5.0, 1.0, 1.0, 1.0, 1.0)],
                                                          [(1.0, 3.0, 1.0, 3.0, 1.0), (1.0, 6.0, 1.0, 6.0, 1.0)],
                                                          [(1.0, 1.0, 4.0, 0.0, 0.0), (1.0, 1.0, 7.0, 0.0, 0.0)]]).all()
    # test multiplying with a partially overlapping single channel spectrogram
    power = spectrogram1 ** spectrogram2[2]
    assert power.offset() == -1
    assert power.resolution() == spectrogram1.resolution()
    assert power.sampling_rate() == spectrogram1.sampling_rate()
    assert power.labels() == ("Power",) * 2
    assert (power.channels() == [[(1.0, 1.0, 16.0, 1.0, 1.0), (1.0, 1.0, 5 ** 7, 1.0, 1.0)],
                                 [(1.0, 1.0, 1.0, 3.0, 1.0), (1.0, 1.0, 1.0, 6.0, 1.0)]]).all()
    assert ((spectrogram2[2] ** spectrogram1).channels() == [[(1.0, 1.0, 16.0, 1.0, 1.0), (1.0, 1.0, 7 ** 5, 1.0, 1.0)],
                                                             [(1.0, 1.0, 4.0, 3.0, 1.0), (1.0, 1.0, 7.0, 6.0, 1.0)]]).all()


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(spectrogram=tests.strategies.spectrograms(max_magnitude=1e15, max_channels=9, max_number_of_frequencies=33, max_length=33),  # pylint: disable=line-too-long
                  signal=tests.strategies.signals(min_value=-1e15, max_value=1e15, max_channels=9, max_length=33))
def test_algebra_with_signal(spectrogram, signal):
    """Tests computations, that combine a spectrogram with a signal."""
    # sanitize the offsets to avoid an excessively large result spectrogram
    if signal.offset() < spectrogram.offset():
        signal = signal.shift(None).shift(spectrogram.offset() - (spectrogram.offset() - signal.offset()) % 10)
    elif signal.offset() > spectrogram.offset():
        signal = signal.shift(None).shift(spectrogram.offset() + (signal.offset() - spectrogram.offset()) % 10)
    # create a spectrogram. which has the signal's samples in each frequency bin for the reference computations
    shape = (len(signal), spectrogram.number_of_frequencies(), signal.length())
    channels = numpy.empty(shape=shape, dtype=numpy.complex128)
    for s, c in zip(signal.channels(), channels):
        for b in c:
            b[:] = s
    signal_spectrogram = sumpf.Spectrogram(
        channels=channels,
        resolution=spectrogram.resolution(),
        sampling_rate=spectrogram.sampling_rate(),
        offset=signal.offset(),
        labels=spectrogram.labels(),
    )
    # addition
    reference = spectrogram + signal_spectrogram
    result = spectrogram + signal
    assert result == reference
    assert result == signal + spectrogram
    # subtraction
    reference = spectrogram - signal_spectrogram
    result = spectrogram - signal
    assert result == reference
    assert signal - spectrogram == signal_spectrogram - spectrogram
    # multiplication
    reference = spectrogram * signal_spectrogram
    result = spectrogram * signal
    assert result == reference
    assert result == signal * spectrogram
    # division
    reference = spectrogram / signal_spectrogram
    result = spectrogram / signal
    assert tests.compare_spectrograms_approx(result, reference)
    assert tests.compare_spectrograms_approx(signal / spectrogram, signal_spectrogram / spectrogram)
    # power
    reference = spectrogram ** signal_spectrogram
    result = spectrogram ** signal
    assert tests.compare_spectrograms_approx(result, reference)
    assert tests.compare_spectrograms_approx(signal ** spectrogram, signal_spectrogram ** spectrogram)


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(spectrogram=tests.strategies.spectrograms(max_magnitude=1e15, max_channels=9, max_number_of_frequencies=33, max_length=33),  # pylint: disable=line-too-long
                  spectrum=tests.strategies.spectrums(max_magnitude=1e15, max_channels=9, max_length=33))
def test_algebra_with_spectrum(spectrogram, spectrum):
    """Tests computations, that combine a spectrogram with a spectrum."""
    # if the numbers of frequency values are different for the spectrogram and the spectrum, a ValueError must be raised
    # pylint: disable=pointless-statement; all these computations, whose result is discarded, are expected to raise errors
    if spectrum.length() != spectrogram.number_of_frequencies():
        with pytest.raises(ValueError):
            spectrogram + spectrum
        with pytest.raises(ValueError):
            spectrum + spectrogram
        with pytest.raises(ValueError):
            spectrogram - spectrum
        with pytest.raises(ValueError):
            spectrum - spectrogram
        with pytest.raises(ValueError):
            spectrogram * spectrum
        with pytest.raises(ValueError):
            spectrum * spectrogram
        with pytest.raises(ValueError):
            spectrogram / spectrum
        with pytest.raises(ValueError):
            spectrum / spectrogram
        with pytest.raises(ValueError):
            spectrogram ** spectrum
        with pytest.raises(ValueError):
            spectrum ** spectrogram
        return
    # create a spectrogram. which has the signal's samples in each frequency bin for the reference computations
    channels = numpy.empty(shape=(len(spectrum), spectrum.length(), spectrogram.length()), dtype=numpy.complex128)
    for s, c in zip(spectrum.channels(), channels.transpose((0, 2, 1))):
        for b in c:
            b[:] = s
    spectrum_spectrogram = sumpf.Spectrogram(
        channels=channels,
        resolution=spectrogram.resolution(),
        sampling_rate=spectrogram.sampling_rate(),
        offset=spectrogram.offset(),
        labels=spectrogram.labels(),
    )
    # addition
    reference = spectrogram + spectrum_spectrogram
    result = spectrogram + spectrum
    assert result == reference
    assert result == spectrum + spectrogram
    # subtraction
    reference = spectrogram - spectrum_spectrogram
    result = spectrogram - spectrum
    assert result == reference
    assert spectrum - spectrogram == spectrum_spectrogram - spectrogram
    # multiplication
    reference = spectrogram * spectrum_spectrogram
    result = spectrogram * spectrum
    assert result == reference
    assert result == spectrum * spectrogram
    # division
    reference = spectrogram / spectrum_spectrogram
    result = spectrogram / spectrum
    assert tests.compare_spectrograms_approx(result, reference)
    assert tests.compare_spectrograms_approx(spectrum / spectrogram, spectrum_spectrogram / spectrogram)
    # power
    reference = spectrogram ** spectrum_spectrogram
    result = spectrogram ** spectrum
    assert tests.compare_spectrograms_approx(result, reference)
    assert tests.compare_spectrograms_approx(spectrum ** spectrogram, spectrum_spectrogram ** spectrogram)

##############
# parameters #
##############


@hypothesis.given(tests.strategies.spectrogram_parameters())
def test_constructor_parameters(parameters):
    """Tests if the constructor parameters are interpreted correctly and have the expected default values."""
    # test an empty Spectrogram
    spectrogram = sumpf.Spectrogram()
    assert (spectrogram.channels() == [[[]]]).all()
    assert spectrogram.resolution() == 1.0
    assert spectrogram.sampling_rate() == 48000.0
    assert spectrogram.offset() == 0
    assert spectrogram.labels() == ("",)
    # test a Spectrogram with all constructor parameters set
    channels = parameters["channels"]
    resolution = parameters["resolution"]
    sampling_rate = parameters["sampling_rate"]
    offset = parameters["offset"]
    labels = tuple(parameters["labels"][0:len(channels)]) + ("",) * (len(channels) - len(parameters["labels"]))
    spectrogram = sumpf.Spectrogram(**parameters)
    assert (spectrogram.channels() == channels).all()
    assert spectrogram.resolution() == resolution
    assert spectrogram.sampling_rate() == sampling_rate
    assert spectrogram.offset() == offset
    assert spectrogram.labels() == labels


@hypothesis.given(tests.strategies.spectrograms())
def test_derived_parameters(spectrogram):
    """Tests if the spectrogram's parameters, that are derived from its constructor parameters are correct."""
    assert spectrogram.number_of_frequencies() == len(spectrogram.channels()[0])
    assert spectrogram.length() == len(spectrogram.channels()[0, 0])
    assert spectrogram.shape() == numpy.shape(spectrogram.channels())
    assert spectrogram.maximum_frequency() == (spectrogram.number_of_frequencies() - 1) * spectrogram.resolution()
    assert spectrogram.duration() == spectrogram.length() / spectrogram.sampling_rate()
    assert (spectrogram.magnitude() == numpy.absolute(spectrogram.channels())).all()
    assert (spectrogram.phase() == numpy.angle(spectrogram.channels())).all()
    assert (spectrogram.real() == numpy.real(spectrogram.channels())).all()
    assert (spectrogram.imaginary() == numpy.imag(spectrogram.channels())).all()

#######################
# convenience methods #
#######################


@hypothesis.given(tests.strategies.spectrograms())
def test_time_samples(spectrogram):
    """Tests the method, that generates the time samples for the spectrogram."""
    t = spectrogram.time_samples()
    if spectrogram.length():
        assert t[0] == spectrogram.offset() / spectrogram.sampling_rate()
    reference = numpy.arange(spectrogram.offset(), spectrogram.offset() + spectrogram.length(), dtype=numpy.float64)
    reference /= spectrogram.sampling_rate()
    assert t == pytest.approx(reference)


@hypothesis.given(tests.strategies.spectrograms())
def test_frequency_samples(spectrogram):
    """Tests the method, that generates the frequency samples for the spectrogram."""
    f = spectrogram.frequency_samples()
    reference = numpy.multiply(tuple(range(spectrogram.number_of_frequencies())), spectrogram.resolution())
    assert f == pytest.approx(reference)


@hypothesis.given(spectrogram=tests.strategies.spectrograms(),
                  length=tests.strategies.short_lengths,
                  value=hypothesis.strategies.floats(allow_nan=False, allow_infinity=False))
def test_pad(spectrogram, length, value):
    """Tests the method for padding a signal."""
    padded = spectrogram.pad(length, value)
    if length < spectrogram.length():
        assert padded == spectrogram[:, :, 0:length]
    elif length > spectrogram.length():
        assert padded[:, :, 0:spectrogram.length()] == spectrogram
        assert (padded.channels()[:, :, spectrogram.length():] == value).all()
    else:
        assert padded == spectrogram


@hypothesis.given(spectrogram=tests.strategies.spectrograms(),
                  shift=hypothesis.strategies.integers(min_value=-100, max_value=100))
def test_shift(spectrogram, shift):
    """Tests the method for shifting the spectrogram"""
    # mode OFFSET
    shifted = spectrogram.shift(shift)
    assert (shifted.channels() == spectrogram.channels()).all()
    assert shifted.resolution() == spectrogram.resolution()
    assert shifted.sampling_rate() == spectrogram.sampling_rate()
    assert shifted.offset() == spectrogram.offset() + shift
    assert shifted.labels() == spectrogram.labels()
    shifted = spectrogram.shift(None)
    assert (shifted.channels() == spectrogram.channels()).all()
    assert shifted.resolution() == spectrogram.resolution()
    assert shifted.sampling_rate() == spectrogram.sampling_rate()
    assert shifted.offset() == 0
    assert shifted.labels() == spectrogram.labels()
    # mode CROP
    shifted = spectrogram.shift(shift=shift, mode=sumpf.Spectrogram.shift_modes.CROP)
    if shift < 0:
        assert (shifted.channels()[:, :, 0:shift] == spectrogram.channels()[:, :, -shift:]).all()
        assert (shifted.channels()[:, :, shift:] == 0.0).all()
    elif shift > 0:
        assert (shifted.channels()[:, :, 0:shift] == 0.0).all()
        assert (shifted.channels()[:, :, shift:] == spectrogram.channels()[:, :, 0:-shift]).all()
    else:
        assert (shifted.channels() == spectrogram.channels()).all()
    assert shifted.sampling_rate() == spectrogram.sampling_rate()
    assert shifted.offset() == spectrogram.offset()
    assert shifted.labels() == spectrogram.labels()
    # mode PAD
    shifted = spectrogram.shift(shift=shift, mode=sumpf.Spectrogram.shift_modes.PAD)
    if shift < 0:
        assert (shifted.channels()[:, :, 0:spectrogram.length()] == spectrogram.channels()).all()
        assert (shifted.channels()[:, :, spectrogram.length():] == 0.0).all()
    elif shift > 0:
        assert (shifted.channels()[:, :, 0:shift] == 0.0).all()
        assert (shifted.channels()[:, :, shift:] == spectrogram.channels()).all()
    else:
        assert (shifted.channels() == spectrogram.channels()).all()
    assert shifted.sampling_rate() == spectrogram.sampling_rate()
    assert shifted.offset() == spectrogram.offset()
    assert shifted.labels() == spectrogram.labels()
    # mode CYCLE
    shifted = spectrogram.shift(shift=shift, mode=sumpf.Spectrogram.shift_modes.CYCLE)
    if shift == 0:
        assert (shifted.channels() == spectrogram.channels()).all()
    else:
        assert (shifted.channels()[:, :, 0:shift] == spectrogram.channels()[:, :, -shift:]).all()
        assert (shifted.channels()[:, :, shift:] == spectrogram.channels()[:, :, 0:-shift]).all()
    assert shifted.sampling_rate() == spectrogram.sampling_rate()
    assert shifted.offset() == spectrogram.offset()
    assert shifted.labels() == spectrogram.labels()


@hypothesis.given(tests.strategies.spectrograms())
def test_conjugate(spectrogram):
    """Tests computing the complex conjugate of a spectrogram."""
    conjugate = spectrogram.conjugate()
    assert (conjugate.channels() == spectrogram.channels().conjugate()).all()
    assert conjugate.resolution() == spectrogram.resolution()
    assert conjugate.sampling_rate() == spectrogram.sampling_rate()
    assert conjugate.offset() == spectrogram.offset()
    assert conjugate.labels() == spectrogram.labels()

#############################
# signal processing methods #
#############################


@pytest.mark.filterwarnings("ignore:NOLA condition failed")
@hypothesis.given(tests.strategies.signals(min_value=-1e3, max_value=1e3))
def test_inverse_short_time_fourier_transform(signal):
    """tests if a signal can be restored from its spectrogram with the
    :meth:`sumpf.Spectrogram.inverse_short_time_fourier_transform` method.
    """
    try:
        import scipy.signal     # noqa; pylint: disable=unused-import,import-outside-toplevel; check if SciPy is available
    except ImportError:
        with pytest.raises(ImportError):
            signal.short_time_fourier_transform()
    else:
        if signal.length() < 256:
            signal = signal.pad(256)
        # test the offset
        spectrogram = signal.short_time_fourier_transform(window=256, overlap=0.5)
        restored = spectrogram.inverse_short_time_fourier_transform(256, 0.5)
        assert abs(restored.offset() - signal.offset()) <= 64   # < half a step
        # test the transform and the inverse transform
        signal = signal.shift(None)
        spectrogram = signal.short_time_fourier_transform(window=256, overlap=0.5)
        restored = spectrogram.inverse_short_time_fourier_transform(256, 0.5)
        assert restored.channels() == pytest.approx(signal.channels())
        assert restored.sampling_rate() == signal.sampling_rate()
        assert restored.offset() == 0
        assert restored.labels() == signal.labels()
        # test different window definitions
        window1 = sumpf.HannWindow(length=256, symmetric=False)
        window2 = sumpf.Merge([window1] * len(signal)).output()
        window3 = window1.channels()
        window4 = window1.channels()[0]
        window5 = window2.channels()
        for w in (window1, window2, window3, window4, window5):
            r = spectrogram.inverse_short_time_fourier_transform(w, 128)
            assert r == restored
        # test with pad=False
        r1 = spectrogram.inverse_short_time_fourier_transform(window=window1, overlap=0.5, pad=False)
#        assert r1.length() <= signal.length()    # for some reason, the restored signal is twice as long...
        assert r1.sampling_rate() == signal.sampling_rate()
        assert r1.offset() == 0
        assert r1.labels() == signal.labels()
        r2 = spectrogram.inverse_short_time_fourier_transform(window=window2, overlap=0.5, pad=False)
        assert r2 == r1

#######################
# persistence methods #
#######################


@hypothesis.given(tests.strategies.spectrograms())
def test_loading_and_saving(spectrogram):
    """Tests writing a spectrogram to a file and loading it again."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test_file")
        for Reader, Writer in [(spectrogram_readers.JsonReader, spectrogram_writers.JsonWriter),
                               (spectrogram_readers.NumpyReader, spectrogram_writers.NumpyNpzWriter),
                               (spectrogram_readers.PickleReader, spectrogram_writers.PickleWriter)]:
            reader = Reader()
            writer = Writer(Writer.formats[0])
            assert not os.path.exists(path)
            writer(spectrogram, path)
            loaded = reader(path)
            assert (loaded.channels() == spectrogram.channels()).all()
            assert loaded.resolution() == spectrogram.resolution()
            assert loaded.sampling_rate() == spectrogram.sampling_rate()
            assert loaded.offset() == spectrogram.offset()
            assert loaded.labels() == spectrogram.labels()
            os.remove(path)


def test_autodetect_format_on_reading():
    """Tests if auto-detecting the file format, when reading a file works."""
    try:
        import scipy.signal     # noqa; pylint: disable=unused-import,import-outside-toplevel; check if SciPy is available
    except ImportError:
        with pytest.raises(ImportError):
            sumpf.SineWave().short_time_fourier_transform()
    else:
        spectrogram = sumpf.SineWave().short_time_fourier_transform()
        with tempfile.TemporaryDirectory() as d:
            for file_format in sumpf.Spectrogram.file_formats:
                if file_format != sumpf.Spectrogram.file_formats.AUTO:
                    path = os.path.join(d, "test_file")
                    assert not os.path.exists(path)
                    spectrogram.save(path, file_format)
                    loaded = sumpf.Spectrogram.load(path)
                    assert (loaded.channels() == spectrogram.channels()).all()
                    assert loaded.resolution() == spectrogram.resolution()
                    assert loaded.sampling_rate() == spectrogram.sampling_rate()
                    assert loaded.offset() == spectrogram.offset()
                    assert loaded.labels() == spectrogram.labels()
                    os.remove(path)


def test_autodetect_format_on_saving():
    """Tests if auto-detecting the file format from the file extension, when writing a file works."""
    try:
        import scipy.signal     # noqa; pylint: disable=unused-import,import-outside-toplevel; check if SciPy is available
    except ImportError:
        with pytest.raises(ImportError):
            sumpf.SineWave().short_time_fourier_transform()
    else:
        file_formats = [(sumpf.Spectrogram.file_formats.TEXT_JSON, ".json", spectrogram_readers.JsonReader),
                        (sumpf.Spectrogram.file_formats.TEXT_JSON, ".js", spectrogram_readers.JsonReader),
                        (sumpf.Spectrogram.file_formats.NUMPY_NPZ, ".npz", spectrogram_readers.NumpyReader),
                        (sumpf.Spectrogram.file_formats.PYTHON_PICKLE, ".pickle", spectrogram_readers.PickleReader)]
        spectrogram = sumpf.SineWave().short_time_fourier_transform()
        with tempfile.TemporaryDirectory() as d:
            for file_format, ending, Reader in file_formats:
                reader = Reader()
                auto_path = os.path.join(d, "test_file" + ending)
                reference_path = os.path.join(d, "test_file")
                assert not os.path.exists(auto_path)
                assert not os.path.exists(reference_path)
                spectrogram.save(auto_path)
                spectrogram.save(reference_path, file_format)
                auto_loaded = sumpf.Spectrogram.load(auto_path)
                reader_loaded = reader(auto_path)
                reference = reader(reference_path)
                assert (auto_loaded.channels() == spectrogram.channels()).all()
                assert auto_loaded.resolution() == spectrogram.resolution()
                assert auto_loaded.sampling_rate() == spectrogram.sampling_rate()
                assert auto_loaded.offset() == spectrogram.offset()
                assert auto_loaded.labels() == spectrogram.labels()
                assert auto_loaded == reader_loaded
                assert reader_loaded.resolution() == reference.resolution()
                assert (reader_loaded.channels() == reference.channels()).all()
                os.remove(auto_path)
                os.remove(reference_path)
