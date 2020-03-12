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

"""Tests for the Filter class"""

import logging
import hypothesis
import hypothesis.strategies as st
import numpy
import pytest
import sumpf
import sumpf._internal as sumpf_internal
import tests

###########################################
# overloaded operators (non math-related) #
###########################################


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(filter_=tests.strategies.filters(),
                  resolution=tests.strategies.resolutions,
                  length=tests.strategies.short_lengths)
def test_call(filter_, resolution, length):
    """Checks the sampling of the filter's transfer function with the overloaded __call__-operator."""
    spectrum = filter_.spectrum(resolution=resolution, length=length)
    result = filter_(spectrum.frequency_samples())
    assert spectrum.shape() == (len(filter_), length)
    if length and len(filter_):    # pylint: disable=len-as-condition; the Filter class has no operator overload for casting it to a boolean
        assert numpy.shape(result) == spectrum.shape()
        not_nan = numpy.invert(numpy.logical_or(numpy.isnan(result), numpy.isinf(result)))
        eq = numpy.ones(shape=spectrum.shape(), dtype=numpy.bool_)
        numpy.equal(result, spectrum.channels(), out=eq, where=not_nan)
        assert eq.all()


@hypothesis.given(tests.strategies.filters())
def test_str(filter_):
    """Checks if casting a Filter instance to a string raises an error."""
    text = str(filter_)
    logging.info(text)


@hypothesis.given(tests.strategies.filters())
def test_repr(filter_):
    """Checks if a filter can be restored from its string representation."""
    # required symbols for the evaluation of the repr-string
    Filter = sumpf.Filter                           # noqa;
    array = numpy.array                             # noqa; sometimes polynomial coefficients are stored in NumPy arrays
    float64 = numpy.float64                         # noqa;
    complex128 = numpy.complex128                   # noqa;
    Interpolations = sumpf_internal.Interpolations  # noqa;
    # create a signal, cast it to a string and restore it from the string
    representation = repr(filter_)
    restored = eval(representation)     # pylint: disable=eval-used
    assert restored == filter_


@hypothesis.given(tests.strategies.filter_parameters())
def test_eq(parameters):
    """Tests the operator overloads for ``==`` and ``!=``."""
    filter1 = sumpf.Filter(**parameters)
    filter2 = sumpf.Filter(**parameters)
    assert filter1 == filter2
    assert filter1 != (filter2 + filter2) * filter2

###################################
# overloaded unary math operators #
###################################


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(filter_=tests.strategies.filters(),
                  frequency=tests.strategies.frequencies)
def test_absolute(filter_, frequency):
    """Tests if computing the absolute of a filter yields the expected result."""
    absolute = abs(filter_)
    reference = sumpf.Filter(transfer_functions=tuple(sumpf.Filter.Absolute(tf)
                                                      for tf in filter_.transfer_functions()),
                             labels=filter_.labels())
    result = absolute(frequency)
    if numpy.isnan(result).any():
        assert (numpy.isnan(result) == numpy.isnan(reference(frequency))).all()
    else:
        assert result == reference(frequency)


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(filter_=tests.strategies.filters(),
                  frequency=tests.strategies.frequencies)
def test_negative(filter_, frequency):
    """Tests if computing the negative of a filter yields the expected result."""
    negative = -filter_
    reference = sumpf.Filter(transfer_functions=tuple(sumpf.Filter.Negative(tf)
                                                      for tf in filter_.transfer_functions()),
                             labels=filter_.labels())
    result = negative(frequency)
    ref = reference(frequency)
    if numpy.isnan(ref).any():
        assert (numpy.isnan(result) == numpy.isnan(ref)).all()
    else:
        assert result == pytest.approx(ref)

####################################
# overloaded binary math operators #
####################################


def _check_channel_count(filter1, filter2):
    """Helper function for cropping two filters, none of which has only one channel,
    to have an equal number of channels, so that they can be used for testing the
    mathematical operations.
    """
    assert len(filter1) > 1
    assert len(filter2) > 1
    assert len(filter1) != len(filter2)
    if len(filter1) < len(filter2):
        filter2 = sumpf.Filter(transfer_functions=filter2.transfer_functions()[0:len(filter1)],
                               labels=filter2.labels()[0:len(filter1)])
    else:
        filter1 = sumpf.Filter(transfer_functions=filter1.transfer_functions()[0:len(filter2)],
                               labels=filter1.labels()[0:len(filter2)])
    return filter1, filter2


def _compare_results(result, reference):
    """Compares the result of a filter computation with a reference, that has been
    computed with NumPy.
    """
    assert numpy.shape(result) == numpy.shape(reference)
    for res, ref in zip(result, reference):
        if numpy.isinf(ref):
            assert numpy.isinf(res) or numpy.isnan(res)
        elif numpy.isnan(ref):
            # due to optimizations in the terms, the result might have a value,
            # where the manually computed reference is NaN.
            pass
        elif max(abs(res), abs(ref)) < 1e10:
            assert res.real == pytest.approx(ref.real)
            assert res.imag == pytest.approx(ref.imag)
        else:
            assert numpy.divide(res, ref) == pytest.approx(1.0)


def _compare_number_results(result, reference, number=None):
    """Compares the result of a filter computation with a reference, that has been
    computed with NumPy.
    This function is used for computations, which involve a filter and a number.
    """
    assert numpy.shape(result) == numpy.shape(reference)
    for ref, res in zip(reference, result):
        if numpy.isinf(ref):
            if number == 0:
                assert numpy.isinf(res) or numpy.isnan(res) or res == 0
            else:
                assert numpy.isinf(res) or numpy.isnan(res)
        elif numpy.isnan(ref):
            if number == 0:
                assert numpy.isnan(res) or res == 0
            else:
                assert numpy.isnan(res)
        else:
            assert res == pytest.approx(ref)


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(filter1=tests.strategies.filters(),
                  filter2=tests.strategies.filters(),
                  frequency=tests.strategies.non_zero_frequencies)
def test_add(filter1, filter2, frequency):
    """Tests the overload of the ``+`` operator."""
    try:
        sum_ = filter1 + filter2
    except ValueError:  # the filters have a different channel count, while none has only one channel
        filter1, filter2 = _check_channel_count(filter1, filter2)
        sum_ = filter1 + filter2
    result = sum_(frequency)
    reference = numpy.add(filter1(frequency), filter2(frequency))
    _compare_results(result, reference)
    channel_count = max(len(filter1), len(filter2))
    if channel_count:
        assert sum_.labels() == ("Sum",) * channel_count


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value")
@hypothesis.given(filter_=tests.strategies.filters(),
                  number=hypothesis.strategies.one_of(hypothesis.strategies.integers(),
                                                      hypothesis.strategies.floats(allow_infinity=False,
                                                                                   allow_nan=False),
                                                      hypothesis.strategies.complex_numbers(allow_infinity=False,
                                                                                            allow_nan=False)),
                  frequency=tests.strategies.non_zero_frequencies)
def test_add_with_number(filter_, number, frequency):
    """Tests the overload of the ``+`` operator."""
    reference = numpy.add(filter_(frequency), number)
    sum1 = filter_ + number
    _compare_number_results(sum1(frequency), reference)
    assert sum1.labels() == filter_.labels()
    sum2 = number + filter_
    _compare_number_results(sum2(frequency), reference)
    assert sum2.labels() == filter_.labels()


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(filter1=tests.strategies.filters(),
                  filter2=tests.strategies.filters(),
                  frequency=tests.strategies.non_zero_frequencies)
def test_subtract(filter1, filter2, frequency):
    """Tests the overload of the ``-`` operator."""
    try:
        difference = filter1 - filter2
    except ValueError:  # the filters have a different channel count, while none has only one channel
        filter1, filter2 = _check_channel_count(filter1, filter2)
        difference = filter1 - filter2
    result1 = difference(frequency)
    result2 = numpy.subtract(filter1(frequency), filter2(frequency))
    _compare_results(result1, result2)
    channel_count = max(len(filter1), len(filter2))
    if channel_count:
        assert difference.labels() == ("Difference",) * channel_count


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(filter_=tests.strategies.filters(),
                  number=hypothesis.strategies.one_of(hypothesis.strategies.integers(),
                                                      hypothesis.strategies.floats(allow_infinity=False,
                                                                                   allow_nan=False),
                                                      hypothesis.strategies.complex_numbers(allow_infinity=False,
                                                                                            allow_nan=False)),
                  frequency=tests.strategies.non_zero_frequencies)
def test_subtract_number(filter_, number, frequency):
    """Tests the overload of the ``-`` operator."""
    reference1 = numpy.subtract(filter_(frequency), number)
    difference1 = filter_ - number
    _compare_number_results(difference1(frequency), reference1)
    assert difference1.labels() == filter_.labels()
    reference2 = numpy.subtract(number, filter_(frequency))
    difference2 = number - filter_
    _compare_number_results(difference2(frequency), reference2)
    assert difference2.labels() == filter_.labels()


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(filter1=tests.strategies.filters(),
                  filter2=tests.strategies.filters(),
                  frequency=tests.strategies.non_zero_frequencies)
def test_multiply(filter1, filter2, frequency):
    """Tests the overload of the ``*`` operator."""
    try:
        product = filter1 * filter2
    except ValueError:  # the filters have a different channel count, while none has only one channel
        filter1, filter2 = _check_channel_count(filter1, filter2)
        product = filter1 * filter2
    result1 = product(frequency)
    result2 = numpy.multiply(filter1(frequency), filter2(frequency))
    _compare_results(result1, result2)
    channel_count = max(len(filter1), len(filter2))
    if channel_count:
        assert product.labels() == ("Product",) * channel_count


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(filter_=tests.strategies.filters(),
                  number=hypothesis.strategies.one_of(hypothesis.strategies.integers(min_value=-1e15,
                                                                                     max_value=1e15),
                                                      hypothesis.strategies.floats(min_value=-1e15,
                                                                                   max_value=1e15),
                                                      hypothesis.strategies.complex_numbers(max_magnitude=1e15,
                                                                                            allow_infinity=False,
                                                                                            allow_nan=False)),
                  frequency=tests.strategies.non_zero_frequencies)
def test_multiply_with_number(filter_, number, frequency):
    """Tests the overload of the ``*`` operator."""
    if number == 1:
        reference = filter_(frequency)
    else:
        reference = tuple(f * number for f in filter_(frequency))
    product1 = filter_ * number
    _compare_number_results(product1(frequency), reference, number=number)
    assert product1.labels() == filter_.labels()
    product2 = number * filter_
    _compare_number_results(product2(frequency), reference, number=number)
    assert product2.labels() == filter_.labels()


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(filter_=tests.strategies.filters(),
                  signal=tests.strategies.signals())
def test_multiply_with_signal_or_spectrum(filter_, signal):
    """Tests the multiplication of a filter with a signal or a spectrum."""
    hypothesis.assume(signal.length() >= 2)
    hypothesis.assume(signal.length() % 2 == 0)
    # apply the filter and crop the data sets' channels if necessary
    try:
        filtered_signal1 = filter_ * signal
    except ValueError:  # the data sets have a different channel count, while none has only one channel
        if filter_.channel_count() < signal.channel_count():
            signal = sumpf.Signal(channels=signal.channels()[0:len(filter_)],
                                  sampling_rate=signal.sampling_rate(),
                                  offset=signal.offset(),
                                  labels=signal.labels()[0:len(filter_)])
        else:
            filter_ = sumpf.Filter(transfer_functions=filter_.transfer_functions()[0:len(signal)],
                                   labels=filter_.labels()[0:len(signal)])
        filtered_signal1 = filter_ * signal
    # compute the multiplication manually
    spectrum = signal.fourier_transform()
    filter_spectrum = filter_.spectrum(resolution=spectrum.resolution(), length=spectrum.length())
    filtered_spectrum1 = filter_ * spectrum
    filtered_spectrum2 = filter_spectrum * spectrum
    filtered_signal2 = filtered_spectrum2.inverse_fourier_transform()
    # test the __rmul__ method
    filtered_signal3 = signal * filter_
    filtered_spectrum3 = spectrum * filter_
    # do the assertions
    if numpy.isnan(filter_spectrum.channels()).any() or numpy.isinf(filter_spectrum.channels()).any() or \
       numpy.isnan(filtered_signal1.channels()).any() or numpy.isinf(filtered_signal2.channels()).any():
        assert (numpy.nan_to_num(filtered_signal1.channels()) == numpy.nan_to_num(filtered_signal2.channels())).all()
        assert (numpy.nan_to_num(filtered_spectrum1.channels()) == numpy.nan_to_num(filtered_spectrum2.channels())).all()   # pylint: disable=line-too-long
        assert (numpy.nan_to_num(filtered_signal3.channels()) == numpy.nan_to_num(filtered_signal2.channels())).all()
        assert (numpy.nan_to_num(filtered_spectrum3.channels()) == numpy.nan_to_num(filtered_spectrum2.channels())).all()   # pylint: disable=line-too-long
    else:
        assert filtered_signal1 == filtered_signal2
        assert filtered_spectrum1 == filtered_spectrum2
        assert filtered_signal3 == filtered_signal2
        assert filtered_spectrum3 == filtered_spectrum2


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(filter_=tests.strategies.filters(),
                  spectrogram=tests.strategies.spectrograms())
def test_multiply_with_spectrogram(filter_, spectrogram):
    """Tests the multiplication of a filter with a spectrogram."""
    spectrum = filter_.spectrum(resolution=spectrogram.resolution(), length=spectrogram.number_of_frequencies())
    reference = spectrogram * spectrum
    for result in (filter_ * spectrogram, spectrogram * filter_):
        assert numpy.array_equal(numpy.nan_to_num(result.channels(), -93.4), numpy.nan_to_num(reference.channels(), -93.4))
        assert result.resolution() == reference.resolution()
        assert result.sampling_rate() == reference.sampling_rate()
        assert result.offset() == reference.offset()
        assert result.labels() == reference.labels()


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(filter1=tests.strategies.filters(),
                  filter2=tests.strategies.filters(),
                  frequency=tests.strategies.non_zero_frequencies)
def test_divide(filter1, filter2, frequency):
    """Tests the overload of the ``/`` operator."""
    nonzero = [tf + sumpf.Filter.Constant(0.01) if tf.is_zero() else tf for tf in filter2.transfer_functions()]     # avoid divisions by zero
    filter2 = sumpf.Filter(transfer_functions=nonzero,
                           labels=filter2.labels())
    try:
        quotient = filter1 / filter2
    except ValueError:  # the filters have a different channel count, while none has only one channel
        filter1, filter2 = _check_channel_count(filter1, filter2)
        quotient = filter1 / filter2
    result1 = quotient(frequency)
    result2 = numpy.divide(filter1(frequency), filter2(frequency))
    _compare_results(result1, result2)
    channel_count = max(len(filter1), len(filter2))
    if channel_count:
        assert quotient.labels() == ("Quotient",) * channel_count


@pytest.mark.filterwarnings("ignore:overflow", "ignore:invalid value", "ignore:divide by zero")
@hypothesis.given(filter_=tests.strategies.filters(),
                  number=hypothesis.strategies.one_of(hypothesis.strategies.integers(min_value=-(2 ** 63 - 1),
                                                                                     max_value=2 ** 63 - 1),
                                                      hypothesis.strategies.floats(allow_infinity=False,
                                                                                   allow_nan=False),
                                                      hypothesis.strategies.complex_numbers(allow_infinity=False,
                                                                                            allow_nan=False)),
                  frequency=tests.strategies.non_zero_frequencies)
def test_divide_by_number(filter_, number, frequency):
    """Tests the overload of the ``/`` operator."""
    values = filter_(frequency)
    if number == 1:
        reference1 = filter_(frequency)
    else:
        reference1 = tuple(v / number for v in values)
    try:
        quotient1 = filter_ / number
    except ZeroDivisionError:
        assert number == 0 and not numpy.equal(values, 0.0).all()
    else:
        _compare_number_results(quotient1(frequency), reference1, number=number)
        assert quotient1.labels() == filter_.labels()
    reference2 = tuple(numpy.divide(number, f) for f in values)
    try:
        quotient2 = number / filter_
    except ZeroDivisionError:
        assert numpy.equal(values, 0.0).any() and number != 0
    else:
        _compare_number_results(quotient2(frequency), reference2, number=number)
        assert quotient2.labels() == filter_.labels()

#########################################
# overloaded and misused math operators #
#########################################


@hypothesis.given(p_coefficients=st.lists(elements=st.floats(min_value=-1e10, max_value=1e10), min_size=1, max_size=10),    # pylint: disable=line-too-long
                  e_coefficient=st.floats(min_value=-1e5, max_value=1e5),
                  p_transform=st.booleans(),
                  e_transform=st.booleans(),
                  a_transform=st.booleans(),
                  frequency=st.floats(min_value=0.0, max_value=1e8))
def test_invert(p_coefficients, e_coefficient, p_transform, e_transform, a_transform, frequency):
    """Tests if computing the inverse of a filter yields the expected result."""
    # the default filter creation strategy explores too many corner cases, for
    # which the inversion does not work. Therefore, the filter is built here
    # manually with a simpler strategy.
    # sanitize the parameters to avoid zeros in the filter, which would cause NaNs in the inversion
    if not numpy.not_equal(p_coefficients, 0.0).any():
        p_coefficients.append(4.6123)
    if frequency == 0.0:
        if any((p_transform, e_transform, a_transform)):
            frequency += 2.65461
        elif p_coefficients[-1] == 0.0:
            p_coefficients[-1] = -2.792
    # build the transfer functions
    polynomial = sumpf.Filter.Polynomial(coefficients=p_coefficients, transform=p_transform)
    exp = sumpf.Filter.Exp(coefficient=e_coefficient, transform=e_transform)
    absolute = sumpf.Filter.Absolute(value=polynomial, transform=a_transform)
    negative = sumpf.Filter.Negative(value=absolute, transform=a_transform)
    sum_ = sumpf.Filter.Sum(summands=(polynomial, exp), transform=a_transform)
    difference = sumpf.Filter.Difference(minuend=polynomial, subtrahend=exp, transform=a_transform)
    product = sumpf.Filter.Product(factors=(polynomial, exp), transform=a_transform)
    quotient = sumpf.Filter.Quotient(numerator=polynomial, denominator=exp, transform=a_transform)
    # instantiate the filter
    filter_ = sumpf.Filter(transfer_functions=(polynomial, exp, absolute, negative, sum_, difference, product, quotient),       # pylint: disable=line-too-long
                           labels=("polynomial", "exp", "absolute", "negative", "sum_", "difference", "product", "quotient"))   # pylint: disable=line-too-long
    # check if the product of the filter with its inverse yields a filter with a constant spectrum of ones
    inverse = ~filter_
    assert inverse.labels() == filter_.labels()
    neutral = filter_ * inverse
    result = neutral(frequency)
    assert numpy.real(result) == pytest.approx(numpy.ones(len(filter_)))
    assert numpy.imag(result) == pytest.approx(numpy.zeros(len(filter_)))

##############
# parameters #
##############


@hypothesis.given(parameters=tests.strategies.filter_parameters(),
                  frequency=tests.strategies.frequencies)
def test_constructor_parameters(parameters, frequency):
    """Tests if the constructor parameters are interpreted correctly and have the expected default values."""
    # test an empty Filter
    filter_ = sumpf.Filter()
    assert filter_(frequency) == (1 + 0j,)  # check the behavior rather than the implementation of the transfer functions
    assert filter_.labels() == ("",)
    # test a Filter with all constructor parameters set
    transfer_functions = parameters["transfer_functions"]
    labels = (tuple(parameters["labels"][0:len(transfer_functions)]) +
              ("",) * (len(transfer_functions) - len(parameters["labels"])))
    filter_ = sumpf.Filter(**parameters)
    assert len(filter_) == len(transfer_functions)  # this has to be checked here to make sure, that the following zip() covers everything
    for tff, tfp in zip(filter_.transfer_functions(), transfer_functions):
        assert tff == tfp                           # checking the behavior here is hard, therefore only the implementation of the transfer functions is checked
    assert filter_.labels() == labels

#######################
# convenience methods #
#######################

# the "spectrum"-method is already tested in test_call
