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

"""Tests for the MergeSpectrums class"""

import connectors
import hypothesis
import numpy
import sumpf
import tests


def test_manual():
    """Tests the merging behavior with manually generated spectrums."""
    spectrum1 = sumpf.Spectrum(channels=numpy.array([(1.1j, 1.2, 1.3j)]),
                               resolution=1.0,
                               labels=("s1c1",))
    spectrum2 = sumpf.Spectrum(channels=numpy.array([(2.1, 2.2j, 2.3, 2.4j), (3.1, 3.2j, 3.3, 3.4j)]),
                               resolution=2.0,
                               labels=("s2c1", "s2c2"))
    spectrum12 = sumpf.Spectrum(channels=numpy.array([(1.1j, 1.2, 1.3j, 0.0),
                                                      (2.1, 2.2j, 2.3, 2.4j),
                                                      (3.1, 3.2j, 3.3, 3.4j)]),
                                resolution=1.0,
                                labels=("s1c1", "s2c1", "s2c2"))
    spectrum21 = sumpf.Spectrum(channels=numpy.array([(2.1, 2.2j, 2.3, 2.4j),
                                                      (3.1, 3.2j, 3.3, 3.4j),
                                                      (1.1j, 1.2, 1.3j, 0.0)]),
                                resolution=2.0,
                                labels=("s2c1", "s2c2", "s1c1"))
    spectrum21c = sumpf.Spectrum(channels=numpy.array([(2.1, 2.2j, 2.3, 2.4j),
                                                       (1.1j, 1.2, 1.3j, 0.0),
                                                       (3.1, 3.2j, 3.3, 3.4j)]),
                                 resolution=2.0,
                                 labels=("s2c1", "s1c1", "s2c2"))
    FIRST_CHANNELS_FIRST = sumpf.MergeSpectrums.modes.FIRST_CHANNELS_FIRST
    assert sumpf.MergeSpectrums([spectrum1, spectrum2]).output() == spectrum12
    assert sumpf.MergeSpectrums([spectrum2, spectrum1]).output() == spectrum21
    assert sumpf.MergeSpectrums([spectrum1, spectrum2], mode=FIRST_CHANNELS_FIRST).output() == spectrum12
    assert sumpf.MergeSpectrums([spectrum2, spectrum1], mode=FIRST_CHANNELS_FIRST).output() == spectrum21c


@hypothesis.given(spectrums=hypothesis.strategies.lists(elements=tests.strategies.spectrums, min_size=2, max_size=5),
                  index=hypothesis.strategies.integers(min_value=0, max_value=5))
def test_merge_first_spectrum_first(spectrums, index):
    """Tests the merging with the FIRST_DATASET_FIRST mode, which is the default."""
    # add a single spectrum
    merger = sumpf.MergeSpectrums(spectrums[0:1])
    assert merger.output() == spectrums[0]
    # merge multiple spectrums
    spectrum_ids = [merger.add(s) for s in spectrums[1:]]
    _compare_merge_first_spectrum_first(spectrums=spectrums,
                                        merged=merger.output())
    # replace one spectrum
    if index >= len(spectrum_ids):
        index = index % len(spectrum_ids)
    spectrum_id = spectrum_ids[index]
    merger.replace(spectrum_id, spectrums[0])
    _compare_merge_first_spectrum_first(spectrums=spectrums[0:index + 1] + [spectrums[0]] + spectrums[index + 2:],
                                        merged=merger.output())
    # remove one spectrum
    merger.remove(spectrum_id)
    _compare_merge_first_spectrum_first(spectrums=spectrums[0:index + 1] + spectrums[index + 2:],
                                        merged=merger.output())


@hypothesis.given(spectrums=hypothesis.strategies.lists(elements=tests.strategies.spectrums, min_size=2, max_size=5),
                  index=hypothesis.strategies.integers(min_value=0, max_value=5))
def test_merge_first_channel_first(spectrums, index):
    """Tests the merging with the FIRST_CHANNEL_FIRST mode."""
    # add a single spectrum
    merger = sumpf.MergeSpectrums(spectrums[0:1], mode=sumpf.MergeSpectrums.modes.FIRST_CHANNELS_FIRST)
    assert merger.output() == spectrums[0]
    # merge multiple spectrums
    spectrum_ids = [merger.add(s) for s in spectrums[1:]]
    _compare_merge_first_channel_first(spectrums=spectrums,
                                       merged=merger.output())
    # replace one spectrum
    if index >= len(spectrum_ids):
        index = index % len(spectrum_ids)
    spectrum_id = spectrum_ids[index]
    merger.replace(spectrum_id, spectrums[0])
    _compare_merge_first_channel_first(spectrums=spectrums[0:index + 1] + [spectrums[0]] + spectrums[index + 2:],
                                       merged=merger.output())
    # remove one spectrum
    merger.remove(spectrum_id)
    _compare_merge_first_channel_first(spectrums=spectrums[0:index + 1] + spectrums[index + 2:],
                                       merged=merger.output())


def test_empty():
    """Tests the behavior when no spectrum is added."""
    assert sumpf.MergeSpectrums().output() == sumpf.Spectrum()


@hypothesis.given(spectrum1=tests.strategies.spectrums,
                  spectrum2=tests.strategies.spectrums,
                  spectrum3=tests.strategies.spectrums,
                  spectrum4=tests.strategies.spectrums)
def test_connectors(spectrum1, spectrum2, spectrum3, spectrum4):
    """tests the connector functionality of the MergeSpectrums class."""
    merger = sumpf.MergeSpectrums([spectrum1])
    p1 = connectors.blocks.PassThrough().output.connect(merger.add)
    merger.add(spectrum3)
    p2 = connectors.blocks.PassThrough().input.connect(merger.output)
    p3 = connectors.blocks.PassThrough().output.connect(merger.set_mode)
    for mode in sumpf.MergeSpectrums.modes:
        p1.input(spectrum2)
        p3.input(mode)
        assert p2.output() == sumpf.MergeSpectrums([spectrum1, spectrum2, spectrum3], mode=mode).output()
        p1.input(spectrum4)
        assert p2.output() == sumpf.MergeSpectrums([spectrum1, spectrum4, spectrum3], mode=mode).output()


def _compare_merge_first_spectrum_first(spectrums, merged):
    """tests if the merged spectrum's channels are ordered like the input spectrums"""
    c = 0
    resolution = spectrums[0].resolution()
    for s in spectrums:
        spectrum = sumpf.Spectrum(channels=s.channels(),
                                  resolution=resolution,    # take the resolution from the first spectrum
                                  labels=s.labels())        # the merged spectrum has a label for each channel, which could be empty
        stop = s.length()
        assert merged[c:c + len(spectrum), 0:stop] == spectrum
        c += len(spectrum)
    assert c == len(merged)


def _compare_merge_first_channel_first(spectrums, merged):
    """test if the merged spectrum's channels are ordered in a way that the first
    channels of all input spectrum come first"""
    resolution = spectrums[0].resolution()
    spectrums = list(spectrums)
    c = 0
    d = 0
    while spectrums:
        to_remove = []
        for s in spectrums:
            if d < len(s):
                spectrum = sumpf.Spectrum(channels=s[d].channels(),
                                          resolution=resolution,    # take the resolution from the first spectrum
                                          labels=s[d].labels())     # the merged spectrum has a label for each channel, which could be empty
                stop = spectrum.length()
                assert merged[c:c + len(spectrum), 0:stop] == spectrum
                c += 1
            else:
                to_remove.append(s)
        for s in to_remove:
            spectrums.remove(s)
        d += 1
    assert c == len(merged)
