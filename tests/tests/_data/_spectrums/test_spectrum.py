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

"""Tests for the Spectrum class"""

import copy
import logging
import math
import hypothesis
import numpy
import pytest
import sumpf
import tests

###########################################
# overloaded operators (non math-related) #
###########################################


def test_getitem_channels():
    """Tests the slicing of a spectrum's channels with the ``[]`` overload"""
    spectrum = sumpf.Spectrum(channels=numpy.array([(1.0, 0.0, 0.0),
                                                    (0.0, 2.0, 0.0),
                                                    (0.0, 0.0, 3.0)]),
                              labels=("one", "two", "three"))
    # integer
    sliced = spectrum[1]
    assert (sliced.channels() == [(0.0, 2.0, 0.0)]).all()
    assert sliced.labels() == ("two",)
    # float
    assert spectrum[0.5] == spectrum[1]
    # integer slice
    sliced = spectrum[1:3]
    assert (sliced.channels() == [(0.0, 2.0, 0.0), (0.0, 0.0, 3.0)]).all()
    assert sliced.labels() == ("two", "three")
    # integer slice with step
    sliced = spectrum[0:3:2]
    assert (sliced.channels() == [(1.0, 0.0, 0.0), (0.0, 0.0, 3.0)]).all()
    assert sliced.labels() == ("one", "three")
    # incomplete slices
    assert spectrum[:] == spectrum
    assert spectrum[:2] == spectrum[0:2]
    assert spectrum[1:] == spectrum[1:3]
    assert spectrum[0::2] == spectrum[0:3:2]
    # float slices
    assert spectrum[0.33:1.0] == spectrum[1:3]
    assert spectrum[0:3:0.66] == spectrum[0:3:2]
    # negative slices
    assert spectrum[0:-1] == spectrum[0:2]
    assert spectrum[-2:] == spectrum[1:3]
    sliced = spectrum[::-1]
    assert (sliced.channels() == [(0.0, 0.0, 3.0), (0.0, 2.0, 0.0), (1.0, 0.0, 0.0)]).all()
    assert sliced.labels() == ("three", "two", "one")
    assert spectrum[-0.99:-0.01:-0.66] == spectrum[0:3:-2]


def test_getitem_samples():
    """Tests the slicing of a spectrum with the ``[]`` overload"""
    spectrum = sumpf.Spectrum(channels=numpy.array([(1.0, 0.0, 0.0),
                                                    (0.0, 2.0, 0.0),
                                                    (0.0, 0.0, 3.0)]),
                              labels=("one", "two", "three"))
    # integer
    sliced = spectrum[1, 1]
    assert (sliced.channels() == [(2.0,)]).all()
    assert sliced.labels() == ("two",)
    # float
    assert spectrum[:, 0.5] == spectrum[:, 1]
    # integer slice
    sliced = spectrum[1:3, 1:3]
    assert (sliced.channels() == [(2.0, 0.0), (0.0, 3.0)]).all()
    assert sliced.labels() == ("two", "three")
    # integer slice with step
    sliced = spectrum[:, 0:3:2]
    assert (sliced.channels() == [(1.0, 0.0), (0.0, 0.0), (0.0, 3.0)]).all()
    assert sliced.labels() == ("one", "two", "three")
    # incomplete slices
    assert spectrum[:, :] == spectrum
    assert spectrum[:2, :1] == spectrum[0:2, 0]
    assert spectrum[1:, 2:] == spectrum[1:3, 2]
    assert spectrum[0::2, 0::2] == spectrum[0:3:2, 0:3:2]
    # float slices
    assert spectrum[0.33:1.0, 0.0:0.66] == spectrum[1:3, 0:2]
    assert spectrum[0:3:0.66, 0.0:1.0:0.66] == spectrum[0:3:2, 0:3:2]
    # negative slices
    assert spectrum[0:-2, 0:-1] == spectrum[0, 0:2]
    assert spectrum[-2:, -1:] == spectrum[1:3, 2]
    sliced = spectrum[::-1, ::-1]
    assert (sliced.channels() == [(3.0, 0.0, 0.0), (0.0, 2.0, 0.0), (0.0, 0.0, 1.0)]).all()
    assert sliced.labels() == ("three", "two", "one")
    assert spectrum[-0.99:-0.01:-0.66, -0.99:-0.01:-0.66] == spectrum[0:3:-2, 0:3:-2]


@hypothesis.given(tests.strategies.spectrums)
def test_str(spectrum):
    """Checks if casting a Spectrum instance to a string raises an error."""
    logging.info(str(spectrum))


@hypothesis.given(tests.strategies.spectrums)
def test_repr(spectrum):
    """Checks if a spectrum can be restored from its string representation."""
    # required symbols for the evaluation of the repr-string
    array = numpy.array             # noqa
    complex128 = numpy.complex128   # noqa
    Spectrum = sumpf.Spectrum       # noqa
    # create a spectrum, cast it to a string and restore it from the string
    restored = eval(repr(spectrum))     # pylint: disable=eval-used
    if spectrum.length():
        # compare the spectrums manually, because NumPy's repr does not print all required decimals
        assert restored.real() == pytest.approx(spectrum.real(), rel=1e-3)
        assert restored.imaginary() == pytest.approx(spectrum.imaginary(), rel=1e-3)
        assert restored.resolution() == spectrum.resolution()
        assert restored.labels() == spectrum.labels()
    else:
        assert restored == spectrum


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value")
@hypothesis.given(tests.strategies.spectrum_parameters)
def test_eq(parameters):
    """Tests the operator overloads for ``==`` and ``!=``."""
    spectrum1 = sumpf.Spectrum(**parameters)
    spectrum2 = sumpf.Spectrum(**parameters)
    assert spectrum1 is not spectrum2
    assert spectrum1 == spectrum2
    if spectrum2.length() > 1:
        assert spectrum1 != spectrum2[:, 0:-1]  # test for a case, where the NumPy comparison of the channels returns a boolean rather than an array of booleans
    assert spectrum1 != (spectrum2 + spectrum2) * spectrum2
    assert spectrum1 != spectrum1.channels()


@hypothesis.given(tests.strategies.spectrum_parameters)
def test_hash(parameters):
    """Tests the operator overload for hashing a spectrum with the builtin :func:`hash` function."""
    parameters2 = copy.copy(parameters)
    parameters2["channels"] = numpy.empty(shape=parameters["channels"].shape, dtype=numpy.complex128)
    parameters2["channels"][:] = parameters["channels"][:]
    spectrum1 = sumpf.Spectrum(**parameters)
    spectrum2 = sumpf.Spectrum(**parameters2)
    spectrum3 = (spectrum2 + spectrum2) * spectrum2
    assert spectrum1.channels() is not spectrum2.channels()
    assert hash(spectrum1) == hash(spectrum2)
    assert hash(spectrum1) != hash(spectrum3)

###################################
# overloaded unary math operators #
###################################


@hypothesis.given(tests.strategies.spectrums)
def test_absolute(spectrum):
    """Tests if computing the magnitude of a spectrum yields the expected result."""
    assert abs(spectrum) == sumpf.Spectrum(channels=numpy.absolute(spectrum.channels()),
                                           resolution=spectrum.resolution(),
                                           labels=spectrum.labels())


@hypothesis.given(tests.strategies.spectrums)
def test_negative(spectrum):
    """Tests if inverting the phase of a spectrum yields the expected result."""
    assert -spectrum == sumpf.Spectrum(channels=numpy.subtract(0.0, spectrum.channels()),
                                       resolution=spectrum.resolution(),
                                       labels=spectrum.labels())

####################################
# overloaded binary math operators #
####################################


def test_add():
    """Tests the overload of the ``+`` operator."""
    spectrum1 = sumpf.Spectrum(channels=numpy.array([(1.0, 0.0, 0.0),
                                                     (0.0, 2.0, 0.0)]),
                               labels=("one1", "two1"))
    spectrum2 = sumpf.Spectrum(channels=numpy.array([(1.0, 0.0, 0.0),
                                                     (0.0, 2.0, 0.0),
                                                     (0.0, 0.0, 3.0)]),
                               labels=("one2", "two2", "three2"))
    # test adding a number
    sum_ = spectrum1 + 3.7
    assert sum_.resolution() == spectrum1.resolution()
    assert sum_.labels() == spectrum1.labels()
    assert (sum_.channels() == numpy.add(spectrum1.channels(), 3.7)).all()
    assert ((3.7 + spectrum1).channels() == sum_.channels()).all()
    # test adding an array
    sum_ = spectrum1 + (1.9, -3.8, 5.5)
    assert sum_.resolution() == spectrum1.resolution()
    assert sum_.labels() == spectrum1.labels()
    assert (sum_.channels() == numpy.add(spectrum1.channels(), (1.9, -3.8, 5.5))).all()
    assert (((1.9, -3.8, 5.5) + spectrum1).channels() == sum_.channels()).all()
    # test adding a Spectrum with the same number of channels
    sum_ = spectrum1 + spectrum1
    assert sum_.resolution() == spectrum1.resolution()
    assert sum_.labels() == ("Sum",) * 2
    assert (sum_.channels() == numpy.multiply(spectrum1.channels(), 2)).all()
    # test adding a Spectrum with a higher number of channels
    sum_ = spectrum1 + spectrum2
    assert sum_.resolution() == spectrum1.resolution()
    assert sum_.labels() == ("Sum",) * 3
    assert (sum_.channels() == [numpy.add(spectrum1.channels()[0], spectrum2.channels()[0]),
                                numpy.add(spectrum1.channels()[1], spectrum2.channels()[1]),
                                spectrum2.channels()[2]]).all()
    assert ((spectrum2 + spectrum1).channels() == sum_.channels()).all()
    # test adding a single channel Spectrum
    sum_ = spectrum1 + spectrum2[2]
    assert sum_.resolution() == spectrum1.resolution()
    assert sum_.labels() == ("Sum",) * 2
    assert (sum_.channels() == numpy.add(spectrum1.channels(), spectrum2.channels()[2])).all()
    assert ((spectrum2[2] + spectrum1).channels() == sum_.channels()).all()


def test_subtract():
    """Tests the overload of the ``-`` operator."""
    spectrum1 = sumpf.Spectrum(channels=numpy.array([(1.0, 0.0, 0.0),
                                                     (0.0, 2.0, 0.0)]),
                               labels=("one1", "two1"))
    spectrum2 = sumpf.Spectrum(channels=numpy.array([(1.0, 0.0, 0.0),
                                                     (0.0, 2.0, 0.0),
                                                     (0.0, 0.0, 3.0)]),
                               labels=("one2", "two2", "three2"))
    # test subtracting a number
    difference = spectrum1 - 3.7
    assert difference.resolution() == spectrum1.resolution()
    assert difference.labels() == spectrum1.labels()
    assert (difference.channels() == numpy.subtract(spectrum1.channels(), 3.7)).all()
    assert ((3.7 - spectrum1).channels() == numpy.subtract(3.7, spectrum1.channels())).all()
    # test subtracting an array
    difference = spectrum1 - (1.9, -3.8, 5.5)
    assert difference.resolution() == spectrum1.resolution()
    assert difference.labels() == spectrum1.labels()
    assert (difference.channels() == numpy.subtract(spectrum1.channels(), (1.9, -3.8, 5.5))).all()
    assert (((1.9, -3.8, 5.5) - spectrum1).channels() == numpy.subtract((1.9, -3.8, 5.5), spectrum1.channels())).all()
    # test subtracting a Spectrum with the same number of channels
    difference = spectrum1 - spectrum1
    assert difference.resolution() == spectrum1.resolution()
    assert difference.labels() == ("Difference",) * 2
    assert (difference.channels() == numpy.zeros(shape=spectrum1.shape())).all()
    # test subtracting a Spectrum with a higher number of channels
    difference = spectrum1 - spectrum2
    assert difference.resolution() == spectrum1.resolution()
    assert difference.labels() == ("Difference",) * 3
    assert (difference.channels() == [numpy.subtract(spectrum1.channels()[0], spectrum2.channels()[0]),
                                      numpy.subtract(spectrum1.channels()[1], spectrum2.channels()[1]),
                                      numpy.subtract(0.0, spectrum2.channels()[2])]).all()
    assert ((spectrum2 - spectrum1).channels() == [numpy.subtract(spectrum2.channels()[0], spectrum1.channels()[0]),
                                                   numpy.subtract(spectrum2.channels()[1], spectrum1.channels()[1]),
                                                   spectrum2.channels()[2]]).all()
    # test subtracting a single channel Spectrum
    difference = spectrum1 - spectrum2[2]
    assert difference.resolution() == spectrum1.resolution()
    assert difference.labels() == ("Difference",) * 2
    assert (difference.channels() == numpy.subtract(spectrum1.channels(), spectrum2.channels()[2])).all()
    assert ((spectrum2[2] - spectrum1).channels() == numpy.subtract(spectrum2.channels()[2],
                                                                    spectrum1.channels())).all()


def test_multiply():
    """Tests the overload of the ``*`` operator."""
    spectrum1 = sumpf.Spectrum(channels=numpy.array([(1.1, 1.0, 1.0),
                                                     (1.0, 1.2, 1.0)]),
                               labels=("one1", "two1"))
    spectrum2 = sumpf.Spectrum(channels=numpy.array([(2.0, 1.0, 1.0),
                                                     (1.0, 3.0, 1.0),
                                                     (1.0, 1.0, 4.0)]),
                               labels=("one2", "two2", "three2"))
    # test multiplying with a number
    product = spectrum1 * 3.7
    assert product.resolution() == spectrum1.resolution()
    assert product.labels() == spectrum1.labels()
    assert (product.channels() == numpy.multiply(spectrum1.channels(), 3.7)).all()
    assert ((3.7 * spectrum1).channels() == product.channels()).all()
    # test multiplying with an array
    product = spectrum1 * (1.9, -3.8, 5.5)
    assert product.resolution() == spectrum1.resolution()
    assert product.labels() == spectrum1.labels()
    assert (product.channels() == numpy.multiply(spectrum1.channels(), (1.9, -3.8, 5.5))).all()
    assert (((1.9, -3.8, 5.5) * spectrum1).channels() == product.channels()).all()
    # test multiplying with a Spectrum with the same number of channels
    product = spectrum1 * spectrum1
    assert product.resolution() == spectrum1.resolution()
    assert product.labels() == ("Product",) * 2
    assert (product.channels() == numpy.square(spectrum1.channels())).all()
    # test multiplying with a Spectrum with a higher number of channels
    product = spectrum1 * spectrum2
    assert product.resolution() == spectrum1.resolution()
    assert product.labels() == ("Product",) * 3
    assert (product.channels() == [numpy.multiply(spectrum1.channels()[0], spectrum2.channels()[0]),
                                   numpy.multiply(spectrum1.channels()[1], spectrum2.channels()[1]),
                                   spectrum2.channels()[2]]).all()
    assert ((spectrum2 * spectrum1).channels() == product.channels()).all()
    # test multiplying with a single channel Spectrum
    product = spectrum1 * spectrum2[2]
    assert product.resolution() == spectrum1.resolution()
    assert product.labels() == ("Product",) * 2
    assert (product.channels() == numpy.multiply(spectrum1.channels(), spectrum2.channels()[2])).all()
    assert ((spectrum2[2] * spectrum1).channels() == product.channels()).all()


def test_divide():
    """Tests the overload of the ``/`` operator."""
    spectrum1 = sumpf.Spectrum(channels=numpy.array([(1.5, 1.0, 1.0),
                                                     (1.0, 1.2, 1.0)]),
                               labels=("one1", "two1"))
    spectrum2 = sumpf.Spectrum(channels=numpy.array([(2.0, 1.0, 1.0),
                                                     (1.0, 0.5, 1.0),
                                                     (1.0, 1.0, 0.2)]),
                               labels=("one2", "two2", "three2"))
    # test dividing by a number
    quotient = spectrum1 / 3.7
    assert quotient.resolution() == spectrum1.resolution()
    assert quotient.labels() == spectrum1.labels()
    assert (quotient.channels() == numpy.divide(spectrum1.channels(), 3.7)).all()
    assert ((3.7 / spectrum1).channels() == numpy.divide(3.7, spectrum1.channels())).all()
    # test dividing by an array
    quotient = spectrum1 / (1.9, -3.8, 5.5)
    assert quotient.resolution() == spectrum1.resolution()
    assert quotient.labels() == spectrum1.labels()
    assert (quotient.channels() == numpy.divide(spectrum1.channels(), (1.9, -3.8, 5.5))).all()
    assert (((1.9, -3.8, 5.5) / spectrum1).channels() == numpy.divide((1.9, -3.8, 5.5), spectrum1.channels())).all()
    # test dividing by a Spectrum with the same number of channels
    quotient = spectrum1 / spectrum1
    assert quotient.resolution() == spectrum1.resolution()
    assert quotient.labels() == ("Quotient",) * 2
    assert (quotient.channels() == numpy.ones(shape=spectrum1.shape())).all()
    # test dividing by a Spectrum with a higher number of channels
    quotient = spectrum1 / spectrum2
    assert quotient.resolution() == spectrum1.resolution()
    assert quotient.labels() == ("Quotient",) * 3
    assert (quotient.channels() == [numpy.divide(spectrum1.channels()[0], spectrum2.channels()[0]),
                                    numpy.divide(spectrum1.channels()[1], spectrum2.channels()[1]),
                                    numpy.divide(1.0, spectrum2.channels()[2])]).all()
    assert ((spectrum2 / spectrum1).channels() == [numpy.divide(spectrum2.channels()[0], spectrum1.channels()[0]),
                                                   numpy.divide(spectrum2.channels()[1], spectrum1.channels()[1]),
                                                   spectrum2.channels()[2]]).all()
    # test dividing by a single channel Spectrum
    quotient = spectrum1 / spectrum2[2]
    assert quotient.resolution() == spectrum1.resolution()
    assert quotient.labels() == ("Quotient",) * 2
    assert (quotient.channels() == numpy.divide(spectrum1.channels(), spectrum2.channels()[2])).all()
    assert ((spectrum2[2] / spectrum1).channels() == numpy.divide(spectrum2.channels()[2], spectrum1.channels())).all()


def test_power():
    """Tests the overload of the ``**`` operator."""
    spectrum1 = sumpf.Spectrum(channels=numpy.array([(1.5 + 4.0j, 1.0, 0.0 + 0.1j),
                                                     (1.0, -1.2, 1.0 + 1.0j)]),
                               labels=("one1", "two1"))
    spectrum2 = sumpf.Spectrum(channels=numpy.array([(2.0 + 1.0j, 0.0, -1.0),
                                                     (1.0 - 0.6j, -0.5, 1.0),
                                                     (1.0, 1.0, 0.2 - 2.0j)]),
                               labels=("one2", "two2", "three2"))
    # test computing the power with a number
    power = spectrum1 ** 3.7
    assert power.resolution() == spectrum1.resolution()
    assert power.labels() == spectrum1.labels()
    assert (power.channels() == numpy.power(spectrum1.channels(), 3.7)).all()
    assert ((3.7 ** spectrum1).channels() == numpy.power(3.7, spectrum1.channels())).all()
    # test computing the power with an array
    power = spectrum1 ** (1.9, -3.8, 5.5)
    assert power.resolution() == spectrum1.resolution()
    assert power.labels() == spectrum1.labels()
    assert (power.channels() == numpy.power(spectrum1.channels(), (1.9, -3.8, 5.5))).all()
    assert (((1.9, -3.8, 5.5) ** spectrum1).channels() == numpy.power((1.9, -3.8, 5.5), spectrum1.channels())).all()
    # test computing the power with a Spectrum with the same number of channels
    power = spectrum1 ** spectrum1
    assert power.resolution() == spectrum1.resolution()
    assert power.labels() == ("Power",) * 2
    assert (power.channels() == numpy.power(spectrum1.channels(), spectrum1.channels())).all()
    # test computing the power with a Spectrum with a higher number of channels
    power = spectrum1 ** spectrum2
    assert power.resolution() == spectrum1.resolution()
    assert power.labels() == ("Power",) * 3
    assert (power.channels() == [numpy.power(spectrum1.channels()[0], spectrum2.channels()[0]),
                                 numpy.power(spectrum1.channels()[1], spectrum2.channels()[1]),
                                 spectrum2.channels()[2]]).all()
    assert ((spectrum2 ** spectrum1).channels() == [numpy.power(spectrum2.channels()[0], spectrum1.channels()[0]),
                                                    numpy.power(spectrum2.channels()[1], spectrum1.channels()[1]),
                                                    spectrum2.channels()[2]]).all()
    # test computing the power with a single channel Spectrum
    power = spectrum1 ** spectrum2[2]
    assert power.resolution() == spectrum1.resolution()
    assert power.labels() == ("Power",) * 2
    assert (power.channels() == numpy.power(spectrum1.channels(), spectrum2.channels()[2])).all()
    assert ((spectrum2[2] ** spectrum1).channels() == numpy.power(spectrum2.channels()[2], spectrum1.channels())).all()

#########################################
# overloaded and misused math operators #
#########################################


@pytest.mark.filterwarnings("ignore:divide by zero", "ignore:invalid value")
@hypothesis.given(tests.strategies.spectrums)
def test_invert(spectrum):
    """Tests if computing the inverse of a spectrum yields the expected result."""
    inverse = ~spectrum
    assert inverse.labels() == spectrum.labels()
    neutral = spectrum * inverse
    channels = numpy.nan_to_num(neutral.channels())                                 # remove the NaNs due to division by zero
    numpy.add(channels, 1.0, out=channels, where=numpy.isnan(neutral.channels()))   #
    assert channels == pytest.approx(numpy.ones(shape=spectrum.shape()), nan_ok=True)

##############
# parameters #
##############


@hypothesis.given(tests.strategies.spectrum_parameters)
def test_constructor_parameters(parameters):
    """Tests if the constructor parameters are interpreted correctly and have the expected default values."""
    # test an empty Spectrum
    spectrum = sumpf.Spectrum()
    assert (spectrum.channels() == [[]]).all()
    assert spectrum.resolution() == 1.0
    assert spectrum.labels() == ("",)
    # test a Spectrum with all constructor parameters set
    channels = parameters["channels"]
    resolution = parameters["resolution"]
    labels = tuple(parameters["labels"][0:len(channels)]) + ("",) * (len(channels) - len(parameters["labels"]))
    spectrum = sumpf.Spectrum(**parameters)
    assert (spectrum.channels() == channels).all()
    assert spectrum.resolution() == resolution
    assert spectrum.labels() == labels


@hypothesis.given(tests.strategies.spectrums)
def test_derived_parameters(spectrum):
    """Tests if the spectrum's parameters, that are derived from its constructor parameters are correct."""
    assert spectrum.length() == len(spectrum.channels()[0])
    assert spectrum.shape() == numpy.shape(spectrum.channels())
    assert spectrum.maximum_frequency() == (spectrum.length() - 1) * spectrum.resolution()
    assert (spectrum.magnitude() == numpy.absolute(spectrum.channels())).all()
    assert (spectrum.phase() == numpy.angle(spectrum.channels())).all()
    assert (spectrum.real() == numpy.real(spectrum.channels())).all()
    assert (spectrum.imaginary() == numpy.imag(spectrum.channels())).all()

#######################
# convenience methods #
#######################


@hypothesis.given(tests.strategies.spectrums)
def test_frequency_samples(spectrum):
    """Tests the method, that generates the frequency samples for the spectrum."""
    f = spectrum.frequency_samples()
    reference = numpy.multiply(tuple(range(spectrum.length())), spectrum.resolution())
    assert f == pytest.approx(reference)


@hypothesis.given(spectrum=tests.strategies.spectrums,
                  length=tests.strategies.short_lengths,
                  value=hypothesis.strategies.complex_numbers(allow_nan=False, allow_infinity=False))
def test_pad(spectrum, length, value):
    """Tests the method for padding a signal."""
    padded = spectrum.pad(length, value)
    if length < spectrum.length():
        assert padded == spectrum[:, 0:length]
    elif length > spectrum.length():
        assert padded[:, 0:spectrum.length()] == spectrum
        assert (padded.channels()[:, spectrum.length():] == value).all()
    else:
        assert padded == spectrum


@hypothesis.given(tests.strategies.spectrums)
def test_conjugate(spectrum):
    """Tests computing the complex conjugate of a spectrum."""
    conjugate = spectrum.conjugate()
    assert (conjugate.channels() == spectrum.channels().conjugate()).all()
    assert conjugate.resolution() == spectrum.resolution()
    assert conjugate.labels() == spectrum.labels()

#############################
# signal processing methods #
#############################


def test_inverse_fourier_transform_results():
    """Tests the inverse Fourier transform of a spectrum with trivial examples."""
    # an empty spectrum
    assert sumpf.Spectrum().inverse_fourier_transform().shape() == (1, 0)
    # a group delay of 1s
    spectrum = sumpf.Spectrum(channels=numpy.array([(1.0, numpy.exp(-1j * math.pi), numpy.exp(-2j * math.pi)),
                                                    (2.0, 2.0, 2.0)]),
                              resolution=0.5)
    signal = spectrum.inverse_fourier_transform()
    assert signal.duration() == 2.0
    assert signal.sampling_rate() == 2.0
    assert signal.channels()[0] == pytest.approx((0.0, 0.0, 1.0, 0.0))
    assert (signal[1].channels() == [(2.0, 0.0, 0.0, 0.0)]).all()


@hypothesis.given(tests.strategies.spectrums)
def test_inverse_fourier_transform_calculation(spectrum):
    """Does some generic tests if the inverse Fourier transform can be computed for a variety of spectrums"""
    signal = spectrum.inverse_fourier_transform()
    assert len(signal) == len(spectrum)
    assert signal.length() == max(1, (spectrum.length() - 1) * 2)
    assert signal.duration() == pytest.approx(1.0 / spectrum.resolution())
    assert signal.offset() == 0
    assert signal.labels() == spectrum.labels()


@hypothesis.given(tests.strategies.signals)
def test_level(signal):
    """Tests the level computation from the Spectrum class by comparing it to the Signal's level method."""
    if signal.length() % 2 == 1:    # with uneven signal lengths, the last sample is lost in the FFT, which makes the levels incomparable
        signal = signal.pad(signal.length() + 1)
    spectrum = signal.fourier_transform()
    # compute the level for each channel
    reference = signal.level()
    level = spectrum.level()
    assert len(level) == len(spectrum)
    assert level == pytest.approx(reference)
    # compute a scalar level value
    reference = signal.level(single_value=True)
    assert spectrum.level(single_value=True) == pytest.approx(reference)
