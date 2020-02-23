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

"""Contains hypothesis strategies for creating SuMPF-specific test data"""

import hypothesis.strategies as st
import hypothesis.extra.numpy as stn
import numpy
import sumpf
import sumpf._internal as sumpf_internal
from . import index

__all__ = ("frequencies", "non_zero_frequencies",
           "sampling_rates", "resolutions",
           "short_lengths", "indices", "labels",
           "signals", "signal_parameters",
           "spectrums", "spectrum_parameters",
           "spectrograms", "spectrogram_parameters",
           "filters", "filter_parameters", "terms", "bands")

##################
# primitive data #
##################

frequencies = st.floats(min_value=0.0, max_value=1e15)
non_zero_frequencies = st.floats(min_value=1e-15, max_value=1e15)
sampling_rates = st.floats(min_value=1e-8, max_value=1e8)
resolutions = sampling_rates
short_lengths = st.integers(min_value=0, max_value=2 ** 10)
indices = st.builds(index.Index,
                    index=st.floats(min_value=0.0, max_value=1.0),
                    mode=st.sampled_from(index.IndexMode))


def labels(min_channels=None, max_channels=None):
    """A strategy that creates tuples of labels for SuMPF data sets."""
    texts = st.text(alphabet=st.characters(blacklist_categories=("Cs",), blacklist_characters=("\x00",)))
    return st.lists(texts, min_size=min_channels, max_size=max_channels)


_offsets = st.integers(min_value=-2 ** 24, max_value=2 ** 24)

##########
# Signal #
##########


def _signal_parameters(min_channels, max_channels,
                       min_length, max_length,
                       min_value, max_value,
                       even_length=False):
    """A helper function, that creates a dictionary with strategies for generating a Signal instance."""
    length = st.integers(min_value=min_length, max_value=max_length)
    if even_length:
        length = st.builds(lambda x: 2 * x, length)
    elements = st.floats(min_value=min_value, max_value=max_value)
    shape = st.tuples(st.integers(min_value=min_channels, max_value=max_channels), length)
    return {"channels": stn.arrays(dtype=numpy.float64, shape=shape, elements=elements),
            "sampling_rate": sampling_rates,
            "offset": _offsets,
            "labels": labels(min_channels, max_channels)}


def signals(min_channels=1, max_channels=5,
            min_length=1, max_length=65,
            min_value=-1e100, max_value=1e100,
            even_length=False):
    """A strategy that creates Signal instances."""
    return st.builds(sumpf.Signal, **_signal_parameters(min_channels, max_channels,
                                                        min_length, max_length,
                                                        min_value, max_value,
                                                        even_length))


def signal_parameters(min_channels=1, max_channels=5,
                      min_length=1, max_length=65,
                      min_value=-1e100, max_value=1e100,
                      even_length=False):
    """A strategy that creates parameter sets for instantiating the Signal class."""
    return st.fixed_dictionaries(_signal_parameters(min_channels, max_channels,
                                                    min_length, max_length,
                                                    min_value, max_value,
                                                    even_length))

############
# Spectrum #
############


def _spectrum_parameters(min_channels, max_channels,
                         min_length, max_length,
                         min_magnitude, max_magnitude):
    """A helper function, that creates a dictionary with strategies for generating a Spectrum instance."""
    elements = st.complex_numbers(min_magnitude=min_magnitude,
                                  max_magnitude=max_magnitude,
                                  allow_nan=False,
                                  allow_infinity=False)
    shape = st.tuples(st.integers(min_value=min_channels, max_value=max_channels),
                      st.integers(min_value=min_length, max_value=max_length))
    return {"channels": stn.arrays(dtype=numpy.complex128, shape=shape, elements=elements),
            "resolution": resolutions,
            "labels": labels(min_channels, max_channels)}


def spectrums(min_channels=1, max_channels=5,
              min_length=1, max_length=65,
              min_magnitude=0.0, max_magnitude=1e100):
    """A strategy that creates Spectrum instances."""
    return st.builds(sumpf.Spectrum, **_spectrum_parameters(min_channels, max_channels,
                                                            min_length, max_length,
                                                            min_magnitude, max_magnitude))


def spectrum_parameters(min_channels=1, max_channels=5,
                        min_length=1, max_length=65,
                        min_magnitude=0.0, max_magnitude=1e100):
    """A strategy that creates parameter sets for instantiating the Spectrum class."""
    return st.fixed_dictionaries(_spectrum_parameters(min_channels, max_channels,
                                                      min_length, max_length,
                                                      min_magnitude, max_magnitude))

###############
# Spectrogram #
###############


def _spectrogram_parameters(min_channels, max_channels,
                            min_number_of_frequencies, max_number_of_frequencies,
                            min_length, max_length,
                            min_magnitude, max_magnitude):
    """A helper function, that creates a dictionary with strategies for generating a Spectrogram instance."""
    elements = st.complex_numbers(min_magnitude=min_magnitude,
                                  max_magnitude=max_magnitude,
                                  allow_nan=False,
                                  allow_infinity=False)
    shape = st.tuples(st.integers(min_value=min_channels, max_value=max_channels),
                      st.integers(min_value=min_number_of_frequencies, max_value=max_number_of_frequencies),
                      st.integers(min_value=min_length, max_value=max_length))
    return {"channels": stn.arrays(dtype=numpy.complex128, shape=shape, elements=elements),
            "resolution": resolutions,
            "sampling_rate": sampling_rates,
            "offset": _offsets,
            "labels": labels(min_channels, max_channels)}


def spectrograms(min_channels=1, max_channels=5,
                 min_number_of_frequencies=1, max_number_of_frequencies=64,
                 min_length=1, max_length=65,
                 min_magnitude=0.0, max_magnitude=1e100):
    """A strategy that creates Spectrogram instances."""
    return st.builds(sumpf.Spectrogram, **_spectrogram_parameters(min_channels, max_channels,
                                                                  min_number_of_frequencies, max_number_of_frequencies,
                                                                  min_length, max_length,
                                                                  min_magnitude, max_magnitude))


def spectrogram_parameters(min_channels=1, max_channels=5,
                           min_number_of_frequencies=1, max_number_of_frequencies=64,
                           min_length=1, max_length=65,
                           min_magnitude=0.0, max_magnitude=1e100):
    """A strategy that creates parameter sets for instantiating the Spectrogram class."""
    return st.fixed_dictionaries(_spectrogram_parameters(min_channels, max_channels,
                                                         min_number_of_frequencies, max_number_of_frequencies,
                                                         min_length, max_length,
                                                         min_magnitude, max_magnitude))

##########
# Filter #
##########


_polynomial = st.builds(sumpf.Filter.Polynomial,
                        coefficients=st.lists(elements=st.floats(min_value=-1e10, max_value=1e10), max_size=6),
                        transform=st.booleans())
_exp = st.builds(sumpf.Filter.Exp,
                 coefficient=st.floats(min_value=-1e5, max_value=1e5),  # it is necessary to set a lower bound to avoid a value of -inf
                 transform=st.booleans())
_bands0 = st.builds(sumpf.Filter.Bands,
                    xs=stn.arrays(dtype=numpy.float64, shape=(0,), elements=non_zero_frequencies, unique=True),
                    ys=stn.arrays(dtype=numpy.float64, shape=(0,), elements=st.floats(min_value=-1e15, max_value=1e15)),    # pylint: disable=line-too-long
                    interpolation=st.sampled_from(sumpf_internal.Interpolations),
                    extrapolation=st.sampled_from(sumpf_internal.Interpolations))
_bands1 = st.builds(sumpf.Filter.Bands,
                    xs=stn.arrays(dtype=numpy.float64, shape=(1,), elements=non_zero_frequencies, unique=True),
                    ys=stn.arrays(dtype=numpy.float64, shape=(1,), elements=st.floats(min_value=-1e15, max_value=1e15)),    # pylint: disable=line-too-long
                    interpolation=st.sampled_from(sumpf_internal.Interpolations),
                    extrapolation=st.sampled_from(sumpf_internal.Interpolations))
_bands5 = st.builds(sumpf.Filter.Bands,
                    xs=stn.arrays(dtype=numpy.float64, shape=(5,), elements=non_zero_frequencies, unique=True),
                    ys=stn.arrays(dtype=numpy.float64, shape=(5,), elements=st.floats(min_value=-1e15, max_value=1e15)),    # pylint: disable=line-too-long
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


def _filter_parameters(min_channels, max_channels):
    """A helper function, that creates a dictionary with strategies for generating a Filter instance."""
    return {"transfer_functions": st.lists(elements=terms, min_size=min_channels, max_size=max_channels),
            "labels": labels(min_channels, max_channels)}


def filters(min_channels=1, max_channels=5):
    """A strategy that creates Filter instances."""
    return st.builds(sumpf.Filter, **_filter_parameters(min_channels, max_channels))


def filter_parameters(min_channels=1, max_channels=5):
    """A strategy that creates parameter sets for instantiating the Filter class."""
    return st.fixed_dictionaries(_filter_parameters(min_channels, max_channels))


def bands(min_channels=1, max_channels=5,
          min_magnitude=0.0, max_magnitude=1e100):
    """A strategy that creates Bands instances."""
    return st.builds(sumpf.Bands,
                     bands=st.one_of(st.dictionaries(keys=frequencies,
                                                     values=st.complex_numbers(min_magnitude=min_magnitude,
                                                                               max_magnitude=max_magnitude)),
                                     st.lists(elements=st.dictionaries(keys=frequencies,
                                                                       values=st.complex_numbers(min_magnitude=min_magnitude,       # pylint: disable=line-too-long
                                                                                                 max_magnitude=max_magnitude)),     # pylint: disable=line-too-long
                                              min_size=min_channels,
                                              max_size=max_channels)),
                     interpolations=st.one_of(st.sampled_from(sumpf.Bands.interpolations),
                                              st.lists(elements=st.sampled_from(sumpf.Bands.interpolations),
                                                       min_size=min_channels,
                                                       max_size=max_channels)),
                     extrapolations=st.one_of(st.sampled_from(sumpf.Bands.interpolations),
                                              st.lists(elements=st.sampled_from(sumpf.Bands.interpolations),
                                                       min_size=min_channels,
                                                       max_size=max_channels)),
                     labels=labels(min_channels, max_channels))
