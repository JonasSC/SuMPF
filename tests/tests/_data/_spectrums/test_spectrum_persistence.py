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

"""Tests for reading and writing :class:`~sumpf.Spectrum` instances from/to a file."""

import os
import tempfile
import hypothesis
import pytest
import sumpf
from sumpf._internal import spectrum_readers, spectrum_writers
import tests


@hypothesis.given(tests.strategies.spectrums)
def test_exact_formats_with_metadata(spectrum):
    """Tests formats, from which a spectrum can be restored exactly."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test_file")
        for Reader, Writer in [(spectrum_readers.JsonReader, spectrum_writers.JsonWriter),
                               (spectrum_readers.NumpyReader, spectrum_writers.NumpyNpzWriter),
                               (spectrum_readers.PickleReader, spectrum_writers.PickleWriter)]:
            reader = Reader()
            writer = Writer(Writer.formats[0])
            assert not os.path.exists(path)
            writer(spectrum, path)
            loaded = reader(path)
            assert (loaded.channels() == spectrum.channels()).all()
            assert loaded.resolution() == spectrum.resolution()
            assert loaded.labels() == spectrum.labels()
            os.remove(path)


@hypothesis.given(tests.strategies.spectrums)
def test_exact_with_frequency_column(spectrum):
    """Tests formats, from which a spectrum can be restored almost exactly with
    the exception of the resolution."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test_file")
        for Reader, Writer, supports_labels in [(spectrum_readers.CsvReader, spectrum_writers.CsvWriter, True),
                                                (spectrum_readers.NumpyReader, spectrum_writers.NumpyNpyWriter, False)]:
            reader = Reader()
            writer = Writer(Writer.formats[0])
            assert not os.path.exists(path)
            writer(spectrum, path)
            loaded = reader(path)
            assert (loaded.channels() == spectrum.channels()).all()
            if spectrum.length() <= 1:
                assert loaded.resolution() == 0.0
            else:
                assert loaded.resolution() == pytest.approx(spectrum.resolution())
            if supports_labels:
                assert loaded.labels() == spectrum.labels()
            else:
                assert loaded.labels() == tuple(f"test_file {index}" for index in range(1, len(spectrum) + 1))
            os.remove(path)


def test_autodetect_format_on_reading():
    """Tests if auto-detecting the file format, when reading a file works."""
    spectrum = sumpf.RudinShapiroNoiseSpectrum()
    with tempfile.TemporaryDirectory() as d:
        for file_format in sumpf.Spectrum.file_formats:
            if file_format != sumpf.Spectrum.file_formats.AUTO:
                path = os.path.join(d, "test_file")
                assert not os.path.exists(path)
                spectrum.save(path, file_format)
                loaded = sumpf.Spectrum.load(path)
                assert loaded.shape() == spectrum.shape()
                os.remove(path)


def test_autodetect_format_on_saving():
    """Tests if auto-detecting the file format from the file extension, when writing a file works."""
    file_formats = [(sumpf.Spectrum.file_formats.TEXT_CSV, ".csv", spectrum_readers.CsvReader),
                    (sumpf.Spectrum.file_formats.TEXT_JSON, ".json", spectrum_readers.JsonReader),
                    (sumpf.Spectrum.file_formats.TEXT_JSON, ".js", spectrum_readers.JsonReader),
                    (sumpf.Spectrum.file_formats.NUMPY_NPZ, ".npz", spectrum_readers.NumpyReader),
                    (sumpf.Spectrum.file_formats.NUMPY_NPY, ".npy", spectrum_readers.NumpyReader),
                    (sumpf.Spectrum.file_formats.PYTHON_PICKLE, ".pickle", spectrum_readers.PickleReader)]
    spectrum = sumpf.RudinShapiroNoiseSpectrum()
    with tempfile.TemporaryDirectory() as d:
        for file_format, ending, Reader in file_formats:
            reader = Reader()
            auto_path = os.path.join(d, "test_file" + ending)
            reference_path = os.path.join(d, "test_file")
            assert not os.path.exists(auto_path)
            assert not os.path.exists(reference_path)
            spectrum.save(auto_path)
            spectrum.save(reference_path, file_format)
            auto_loaded = sumpf.Spectrum.load(auto_path)
            reader_loaded = reader(auto_path)
            reference = reader(reference_path)
            assert auto_loaded.shape() == spectrum.shape()
            assert auto_loaded == reader_loaded
            assert reader_loaded.resolution() == reference.resolution()
            assert (reader_loaded.channels() == reference.channels()).all()
            os.remove(auto_path)
            os.remove(reference_path)
