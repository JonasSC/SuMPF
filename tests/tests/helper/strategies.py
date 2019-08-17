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

"""Contains hypothesis strategies for creating SuMPF-specific test data"""

import hypothesis.strategies as st
import hypothesis.extra.numpy as stn
import numpy
import sumpf
import sumpf._internal as sumpf_internal

__all__ = ("frequencies", "short_lengths", "labels",
           "signal_parameters", "signals", "normalized_signals",
           "spectrum_parameters", "spectrums",
           "spectrogram_parameters", "spectrograms",
           "terms", "filter_parameters", "filters", "bands")

##################
# primitive data #
##################

frequencies = st.floats(min_value=0.0, max_value=1e15)
non_zero_frequencies = st.floats(min_value=1e-15, max_value=1e15)
sampling_rates = st.floats(min_value=1e-8, max_value=1e8)
resolutions = sampling_rates
short_lengths = st.integers(min_value=0, max_value=2 ** 10)
texts = st.text(alphabet=st.characters(blacklist_categories=("Cs",), blacklist_characters=("\x00",)))
labels = st.lists(elements=texts)

##########
# Signal #
##########

_signal_parameters = {"channels": stn.arrays(dtype=numpy.float64,       # pylint: disable=no-value-for-parameter; there is a false alarm about a missing parameter for ``draw``
                                             shape=stn.array_shapes(min_dims=2, max_dims=2),
                                             elements=st.floats(min_value=-1e100, max_value=1e100)),
                      "sampling_rate": sampling_rates,
                      "offset": st.integers(min_value=-2 ** 24, max_value=2 ** 24),
                      "labels": labels}
signal_parameters = st.fixed_dictionaries(_signal_parameters)
signals = st.builds(sumpf.Signal, **_signal_parameters)
_normalized_signal_parameters = {"channels": stn.arrays(dtype=numpy.float64,       # pylint: disable=no-value-for-parameter; there is a false alarm about a missing parameter for ``draw``
                                                        shape=stn.array_shapes(min_dims=2, max_dims=2),
                                                        elements=st.floats(min_value=-255.0 / 256.0, max_value=254.0 / 256.0)),     # pylint: disable=line-too-long
                                 "sampling_rate": sampling_rates,
                                 "offset": st.integers(min_value=-2 ** 24, max_value=2 ** 24),
                                 "labels": labels}
normalized_signal_parameters = st.fixed_dictionaries(_normalized_signal_parameters)
normalized_signals = st.builds(sumpf.Signal, **_normalized_signal_parameters)

############
# Spectrum #
############

_spectrum_parameters = {"channels": stn.arrays(dtype=numpy.complex128,  # pylint: disable=no-value-for-parameter; there is a false alarm about a missing parameter for ``draw``
                                               shape=stn.array_shapes(min_dims=2, max_dims=2),
                                               elements=st.complex_numbers(max_magnitude=1e100, allow_nan=False, allow_infinity=False)),    # pylint: disable=line-too-long
                        "resolution": resolutions,
                        "labels": labels}
spectrum_parameters = st.fixed_dictionaries(_spectrum_parameters)
spectrums = st.builds(sumpf.Spectrum, **_spectrum_parameters)

###############
# Spectrogram #
###############

_spectrogram_parameters = {"channels": stn.arrays(dtype=numpy.complex128,  # pylint: disable=no-value-for-parameter; there is a false alarm about a missing parameter for ``draw``
                                                  shape=stn.array_shapes(min_dims=3, max_dims=3),
                                                  elements=st.complex_numbers(max_magnitude=1e100, allow_nan=False, allow_infinity=False)),    # pylint: disable=line-too-long
                           "resolution": resolutions,
                           "sampling_rate": sampling_rates,
                           "offset": st.integers(min_value=-2 ** 24, max_value=2 ** 24),
                           "labels": labels}
spectrogram_parameters = st.fixed_dictionaries(_spectrogram_parameters)
spectrograms = st.builds(sumpf.Spectrogram, **_spectrogram_parameters)

##########
# Filter #
##########

_polynomial = st.builds(sumpf.Filter.Polynomial,
                        coefficients=st.lists(elements=st.floats(min_value=-1e10, max_value=1e10), max_size=6),
                        transform=st.booleans())
_exp = st.builds(sumpf.Filter.Exp,
                 coefficient=st.floats(min_value=-1e5, max_value=1e5),   # it is necessary to set a lower bound to avoid a value of -inf
                 transform=st.booleans())
_bands0 = st.builds(sumpf.Filter.Bands,
                    xs=stn.arrays(dtype=numpy.float64, shape=(0,), elements=non_zero_frequencies, unique=True),
                    ys=stn.arrays(dtype=numpy.float64, shape=(0,), elements=st.floats(min_value=-1e15, max_value=1e15)),
                    interpolation=st.sampled_from(sumpf_internal.Interpolations),
                    extrapolation=st.sampled_from(sumpf_internal.Interpolations))
_bands1 = st.builds(sumpf.Filter.Bands,
                    xs=stn.arrays(dtype=numpy.float64, shape=(1,), elements=non_zero_frequencies, unique=True),
                    ys=stn.arrays(dtype=numpy.float64, shape=(1,), elements=st.floats(min_value=-1e15, max_value=1e15)),
                    interpolation=st.sampled_from(sumpf_internal.Interpolations),
                    extrapolation=st.sampled_from(sumpf_internal.Interpolations))
_bands5 = st.builds(sumpf.Filter.Bands,
                    xs=stn.arrays(dtype=numpy.float64, shape=(5,), elements=non_zero_frequencies, unique=True),
                    ys=stn.arrays(dtype=numpy.float64, shape=(5,), elements=st.floats(min_value=-1e15, max_value=1e15)),
                    interpolation=st.sampled_from(sumpf_internal.Interpolations),
                    extrapolation=st.sampled_from(sumpf_internal.Interpolations))
_quotient = st.builds(sumpf.Filter.Quotient,
                      numerator=st.one_of(_polynomial, _exp),
                      denominator=st.one_of(_polynomial, _exp),
                      transform=st.booleans())
_product = st.builds(sumpf.Filter.Product,
                     factors=st.lists(elements=st.one_of(_polynomial, _exp, _quotient)),
                     transform=st.booleans())
_sum = st.builds(sumpf.Filter.Sum,
                 summands=st.lists(elements=st.one_of(_polynomial, _exp, _quotient, _product)),
                 transform=st.booleans())
_difference = st.builds(sumpf.Filter.Difference,
                        minuend=st.one_of(_polynomial, _exp, _quotient, _product, _sum),
                        subtrahend=st.one_of(_polynomial, _exp, _quotient, _product, _sum),
                        transform=st.booleans())
_absolute = st.builds(sumpf.Filter.Absolute,
                      value=st.one_of(_polynomial, _exp, _quotient, _product, _sum, _difference),
                      transform=st.booleans())
_negative = st.builds(sumpf.Filter.Negative,
                      value=st.one_of(_polynomial, _exp, _quotient, _product, _sum, _difference, _absolute),
                      transform=st.booleans())
terms = st.one_of(_polynomial, _exp, _bands0, _bands1, _bands5,
                  _quotient, _product, _sum, _difference,
                  _absolute, _negative)
_filter_parameters = {"transfer_functions": st.lists(elements=terms,
                                                     min_size=1),
                      "labels": labels}
filter_parameters = st.fixed_dictionaries(_filter_parameters)
filters = st.builds(sumpf.Filter, **_filter_parameters)
_bands_parameters = {"bands": st.one_of(st.dictionaries(keys=frequencies, values=st.complex_numbers(min_magnitude=0.0, max_magnitude=1e15)),
                                        st.lists(elements=st.dictionaries(keys=frequencies, values=st.complex_numbers(min_magnitude=0.0, max_magnitude=1e15)), min_size=1)),
                     "interpolations": st.one_of(st.sampled_from(sumpf_internal.Interpolations),
                                                 st.lists(elements=st.sampled_from(sumpf_internal.Interpolations), min_size=1)),
                     "extrapolations": st.one_of(st.sampled_from(sumpf_internal.Interpolations),
                                                 st.lists(elements=st.sampled_from(sumpf_internal.Interpolations), min_size=1)),
                     "labels": labels}
bands = st.builds(sumpf.Bands, **_bands_parameters)
