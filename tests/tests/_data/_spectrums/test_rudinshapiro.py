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

"""Tests for the RudinShapiroNoiseSpectrum class"""

import math
import hypothesis
import numpy
import sumpf
import tests


@hypothesis.given(start_frequency=tests.strategies.frequencies,
                  stop_frequency=tests.strategies.non_zero_frequencies,
                  resolution=tests.strategies.resolutions,
                  length=tests.strategies.short_lengths)
def test_parameters(start_frequency, stop_frequency, resolution, length):
    """Does some very basic tests with the constructor parameters of the RudinShapiroNoiseSpectrum class"""
    start_frequency, stop_frequency = sorted((start_frequency, stop_frequency))
    noise = sumpf.RudinShapiroNoiseSpectrum(start_frequency, stop_frequency, resolution, length)
    assert noise.shape() == (1, length)
    assert noise.resolution() == resolution


@hypothesis.given(start_frequency=tests.strategies.frequencies,
                  stop_frequency=tests.strategies.non_zero_frequencies,
                  resolution=tests.strategies.resolutions,
                  length=tests.strategies.short_lengths)
def test_spectrum(start_frequency, stop_frequency, resolution, length):
    """Tests the properties of the Rudin-Shapiro-Noise-spectrums"""
    start_frequency, stop_frequency = sorted((start_frequency, stop_frequency))
    noise = sumpf.RudinShapiroNoiseSpectrum(start_frequency, stop_frequency, resolution, length)
    start_index = min(int(round(start_frequency / resolution)), length)
    stop_index = min(int(round(stop_frequency / resolution)), length)
    # check the sequence length
    assert noise.sequence_length() == stop_index - start_index
    # check the magnitude
    magnitude = noise.magnitude()[0]
    assert (magnitude[0:start_index] == numpy.zeros(start_index)).all()
    if stop_index - start_index > 0:
        assert (magnitude[start_index:stop_index] == numpy.ones(stop_index - start_index)).all()
    if stop_index < length:
        assert (magnitude[stop_index:] == numpy.zeros(length - stop_index)).all()
    # check the phase (or the sign) by comparing it to an alternate implementation of the Rudin-Shapiro sequence
    if stop_index - start_index > 0:
        sequence = noise.channels()[0, start_index:stop_index]
        reference = [1, 1]
        while len(reference) < len(sequence):
            new_reference = []
            for i in range(0, len(reference), 2):
                s = reference[i:i + 2]
                if s == [1, 1]:
                    new_reference.extend((1, 1, 1, -1))
                elif s == [1, -1]:
                    new_reference.extend((1, 1, -1, 1))
                elif s == [-1, 1]:
                    new_reference.extend((-1, -1, 1, -1))
                elif s == [-1, -1]:
                    new_reference.extend((-1, -1, -1, 1))
            reference = new_reference
        assert (sequence == reference[0:len(sequence)]).all


@hypothesis.given(power=hypothesis.strategies.integers(min_value=6, max_value=16))
def test_crest_factor(power):
    """Checks the crest factor of the Rudin-Shapiro-Noise-spectrums"""
    spectrum = sumpf.RudinShapiroNoiseSpectrum(length=2 ** power)
    assert spectrum.sequence_length() == 2 ** power
    signal = spectrum.inverse_fourier_transform()
    level = signal.level()[0]
    peak = max(signal.channels().max(), -signal.channels().min())
    crest_factor = 20.0 * math.log10(peak / level)
    assert crest_factor < 6.3   # 6dB is the theoretical minimum
