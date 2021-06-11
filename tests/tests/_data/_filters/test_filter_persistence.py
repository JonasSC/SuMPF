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

"""Tests for reading and writing :class:`~sumpf.Filter` instances from/to a file."""

import os
import tempfile
import hypothesis
import numpy
import sumpf
import sumpf._internal as sumpf_internal
import tests


@hypothesis.given(tests.strategies.filters())
def test_autodetect_format_on_reading(filter_):
    """Tests if auto-detecting the file format, when reading a file works."""
    with tempfile.TemporaryDirectory() as d:
        for file_format in sumpf.Filter.file_formats:
            if file_format != sumpf.Filter.file_formats.AUTO:
                path = os.path.join(d, "test_file")
                assert not os.path.exists(path)
                filter_.save(path, file_format)
                loaded = sumpf.Filter.load(path)
                assert loaded == filter_
                os.remove(path)


@hypothesis.given(tests.strategies.filters())
def test_autodetect_format_on_saving(filter_):
    """Tests if auto-detecting the file format from the file extension, when writing a file works."""
    file_formats = [(".txt", sumpf_internal.filter_readers.ReprReader),
                    (".json", sumpf_internal.filter_readers.JsonReader),
                    (".js", sumpf_internal.filter_readers.JsonReader),
                    (".pickle", sumpf_internal.filter_readers.PickleReader)]
    with tempfile.TemporaryDirectory() as d:
        for ending, Reader in file_formats:
            reader = Reader()
            path = os.path.join(d, "test_file" + ending)
            assert not os.path.exists(path)
            filter_.save(path)
            loaded = reader(path)
            if Reader is sumpf_internal.filter_readers.ReprReader and "array" in repr(filter_):     # repr of a numpy array does not contain all digits of the array's elements
                assert repr(loaded) == repr(filter_)
            else:
                assert loaded == filter_
            os.remove(path)


@hypothesis.given(tests.strategies.bands())
def test_bands_as_table(bands):
    """Tests loading and saving bands filters in tabular text files."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test_file")
        for Reader, Writer in [(sumpf_internal.filter_readers.TableReader, sumpf_internal.filter_writers.TextTabIWriter),       # pylint: disable=line-too-long
                               (sumpf_internal.filter_readers.TableReader, sumpf_internal.filter_writers.TextTabJWriter),       # pylint: disable=line-too-long
                               (sumpf_internal.filter_readers.TableReader, sumpf_internal.filter_writers.TextPipeIWriter),      # pylint: disable=line-too-long
                               (sumpf_internal.filter_readers.TableReader, sumpf_internal.filter_writers.TextPipeJWriter),      # pylint: disable=line-too-long
                               (sumpf_internal.filter_readers.TableReader, sumpf_internal.filter_writers.TextGnuplotWriter)]:   # pylint: disable=line-too-long
            reader = Reader()
            for file_format in Writer.formats:
                if file_format in sumpf.Bands.file_formats:
                    writer = Writer(file_format)
                    assert not os.path.exists(path)
                    writer(bands, path)
                    loaded = reader(path)
                    assert len(loaded) == len(bands)
                    for t1, t2 in zip(loaded.transfer_functions(), bands.transfer_functions()):
                        assert (t1.xs == t2.xs).all()
                        assert (t1.ys == t2.ys).all()
                    os.remove(path)


@hypothesis.given(tests.strategies.bands())
def test_bands_as_csv(bands):
    """Tests loading and saving bands filters in CSV files."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test_file")
        assert not os.path.exists(path)
        reader = sumpf_internal.filter_readers.CsvReader()
        writer = sumpf_internal.filter_writers.CsvWriter(sumpf.Bands.file_formats.TEXT_CSV)
        writer(bands, path)
        loaded = reader(path)
        assert len(loaded) == len(bands)
        for t1, t2 in zip(loaded.transfer_functions(), bands.transfer_functions()):
            assert (t1.xs == t2.xs).all()
            assert (t1.ys == t2.ys).all()
        assert loaded.labels() == bands.labels()
        os.remove(path)


@hypothesis.given(tests.strategies.bands())
def test_bands_as_repr(bands):
    """Tests loading and saving bands filters' string representations in text files."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test_file")
        assert not os.path.exists(path)
        reader = sumpf_internal.filter_readers.ReprReader()
        writer = sumpf_internal.filter_writers.ReprWriter(sumpf.Bands.file_formats.TEXT_REPR)
        writer(bands, path)
        loaded = reader(path)
        assert len(loaded) == len(bands)
        for t1, t2 in zip(loaded.transfer_functions(), bands.transfer_functions()):
            assert numpy.array_equal(t1.xs, t2.xs)
            assert numpy.array_equal(t1.ys, t2.ys)
            assert t1.interpolation is t2.interpolation
            assert t1.extrapolation is t2.extrapolation
        assert loaded.labels() == bands.labels()
        os.remove(path)


@hypothesis.given(tests.strategies.bands())
def test_bands_as_serialization(bands):
    """Tests loading and saving bands filters in common serializations."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test_file")
        for Reader, Writer in [(sumpf_internal.filter_readers.JsonReader, sumpf_internal.filter_writers.JsonWriter),
                               (sumpf_internal.filter_readers.PickleReader, sumpf_internal.filter_writers.PickleWriter)]:   # pylint: disable=line-too-long
            reader = Reader()
            for file_format in Writer.formats:
                if file_format in sumpf.Bands.file_formats:
                    writer = Writer(file_format)
                    assert not os.path.exists(path)
                    writer(bands, path)
                    loaded = reader(path)
                    assert loaded == bands
                    os.remove(path)


@hypothesis.given(tests.strategies.bands())
def test_bands_as_numpy(bands):
    """Tests loading and saving bands filters in numpy files."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test_file")
        for Reader, Writer in [(sumpf_internal.filter_readers.NumpyReader, sumpf_internal.filter_writers.NumpyNpyWriter),   # pylint: disable=line-too-long
                               (sumpf_internal.filter_readers.NumpyReader, sumpf_internal.filter_writers.NumpyNpzWriter)]:  # pylint: disable=line-too-long
            reader = Reader()
            for file_format in Writer.formats:
                if file_format in sumpf.Bands.file_formats:
                    writer = Writer(file_format)
                    assert not os.path.exists(path)
                    writer(bands, path)
                    loaded = reader(path)
                    if file_format is not sumpf.Bands.file_formats.NUMPY_NPY:
                        assert loaded == bands
                    else:
                        assert len(loaded) == len(bands)
                        for t1, t2 in zip(loaded.transfer_functions(), bands.transfer_functions()):
                            assert (t1.xs == t2.xs).all()
                            assert (t1.ys == t2.ys).all()
                    os.remove(path)


@hypothesis.given(tests.strategies.bands())
def test_autodetect_format_on_reading_bands(bands):
    """Tests if auto-detecting the file format, when reading a file works."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test_file")
        for file_format in sumpf.Bands.file_formats:
            if file_format != sumpf.Bands.file_formats.AUTO:
                assert not os.path.exists(path)
                bands.save(path, file_format)
                loaded = sumpf.Bands.load(path)
                if file_format in (sumpf.Bands.file_formats.TEXT_JSON,
                                   sumpf.Bands.file_formats.TEXT_REPR,
                                   sumpf.Bands.file_formats.NUMPY_NPZ,
                                   sumpf.Bands.file_formats.PYTHON_PICKLE):
                    assert loaded == bands
                elif file_format is sumpf.Bands.file_formats.TEXT_CSV:
                    assert len(loaded) == len(bands.transfer_functions())
                    for t1, t2 in zip(loaded.transfer_functions(), bands.transfer_functions()):
                        assert (t1.xs == t2.xs).all()
                        assert (t1.ys == t2.ys).all()
                    assert loaded.labels() == bands.labels()
                elif file_format in (sumpf.Bands.file_formats.TEXT_TAB_I,
                                     sumpf.Bands.file_formats.TEXT_TAB_J,
                                     sumpf.Bands.file_formats.TEXT_PIPE_I,
                                     sumpf.Bands.file_formats.TEXT_PIPE_J,
                                     sumpf.Bands.file_formats.TEXT_GNUPLOT,
                                     sumpf.Bands.file_formats.NUMPY_NPY):
                    assert len(loaded) == len(bands.transfer_functions())
                    for t1, t2 in zip(loaded.transfer_functions(), bands.transfer_functions()):
                        assert (t1.xs == t2.xs).all()
                        assert (t1.ys == t2.ys).all()
                os.remove(path)


@hypothesis.given(tests.strategies.bands())
def test_autodetect_format_on_saving_bands(bands):
    """Tests if auto-detecting the file format from the file extension, when writing a file works."""
    file_formats = [(".txt", sumpf_internal.filter_readers.TableReader),
                    (".dat", sumpf_internal.filter_readers.TableReader),
                    (".asc", sumpf_internal.filter_readers.TableReader),
                    (".tab", sumpf_internal.filter_readers.TableReader),
                    (".csv", sumpf_internal.filter_readers.CsvReader),
                    (".json", sumpf_internal.filter_readers.JsonReader),
                    (".js", sumpf_internal.filter_readers.JsonReader),
                    (".npy", sumpf_internal.filter_readers.NumpyReader),
                    (".npz", sumpf_internal.filter_readers.NumpyReader),
                    (".pickle", sumpf_internal.filter_readers.PickleReader)]
    with tempfile.TemporaryDirectory() as d:
        for ending, Reader in file_formats:
            reader = Reader()
            path = os.path.join(d, "test_file" + ending)
            assert not os.path.exists(path)
            bands.save(path)
            loaded = reader(path)
            if ending in (".json", ".js", ".npz", ".pickle"):
                assert loaded == bands
            else:
                assert len(loaded) == len(bands.transfer_functions())
                for t1, t2 in zip(loaded.transfer_functions(), bands.transfer_functions()):
                    assert (t1.xs == t2.xs).all()
                    assert (t1.ys == t2.ys).all()
                if ending == ".csv":
                    assert loaded.labels() == bands.labels()
            os.remove(path)
