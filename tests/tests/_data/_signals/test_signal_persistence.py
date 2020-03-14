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

"""Tests for reading and writing :class:`~sumpf.Signal` instances from/to a file."""

import os
import tempfile
import hypothesis
import pytest
import sumpf
from sumpf._internal import signal_writers, signal_readers
import tests

# pylint: disable=line-too-long; this file contains many table-like dictionaries, that would be harder to read, if the rows were broken into multiple lines


@hypothesis.given(tests.strategies.signals(max_channels=9))
def test_exact_formats_with_metadata(signal):
    """Tests formats, from which a signal can be restored exactly."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test_file")
        for Reader, Writer in [(signal_readers.JsonReader, signal_writers.JsonWriter),
                               (signal_readers.NumpyReader, signal_writers.NumpyNpzWriter),
                               (signal_readers.PickleReader, signal_writers.PickleWriter)]:
            reader = Reader()
            for file_format in Writer.formats:
                writer = Writer(file_format)
                assert not os.path.exists(path)
                writer(signal, path)
                loaded = reader(path)
                assert (loaded.channels() == signal.channels()).all()
                assert loaded.sampling_rate() == signal.sampling_rate()
                assert loaded.offset() == signal.offset()
                assert loaded.labels() == signal.labels()
                os.remove(path)


@hypothesis.given(tests.strategies.signals(max_channels=9))
def test_exact_with_time_column(signal):
    """Tests formats, from which a signal can be restored almost exactly with
    the exception of the sampling rate and the offset, if the signal is shorter
    than two samples."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test_file")
        for Reader, Writer, supports_labels in [(signal_readers.CsvReader, signal_writers.CsvWriter, True),
                                                (signal_readers.NumpyReader, signal_writers.NumpyNpyWriter, False)]:
            reader = Reader()
            for file_format in Writer.formats:
                writer = Writer(file_format)
                assert not os.path.exists(path)
                writer(signal, path)
                loaded = reader(path)
                assert (loaded.channels() == signal.channels()).all()
                if signal.length() <= 1:
                    if signal.offset() == 0:
                        assert loaded.sampling_rate() == 48000.0
                        assert loaded.offset() == 0
                    else:
                        assert loaded.sampling_rate() == pytest.approx(abs(1.0 / signal.time_samples()[0]))
                        assert abs(loaded.offset()) == 1
                else:
                    factor = abs(signal.offset() / 1e15)
                    offset_margin = int(round(abs(signal.offset()) * factor))
                    assert loaded.sampling_rate() == pytest.approx(signal.sampling_rate(), rel=max(factor, 1e-10))
                    assert signal.offset() - offset_margin <= loaded.offset() <= signal.offset() + offset_margin
                if supports_labels:
                    assert loaded.labels() == signal.labels()
                else:
                    assert loaded.labels() == tuple(f"test_file {index}" for index in range(1, len(signal) + 1))
                os.remove(path)


@hypothesis.given(tests.strategies.signals(max_channels=9, min_value=-255 / 256, max_value=254 / 256))
def test_exact_formats_without_metadata(signal):
    """Tests formats, from which a signal's samples can be restored exactly."""
    pytest.importorskip("soundfile")
    formats = {sumpf.Signal.file_formats.WAV_FLOAT64: ([signal_readers.SoundfileReader], [signal_writers.SoundfileWriter]),
               sumpf.Signal.file_formats.AIFF_FLOAT64: ([signal_readers.SoundfileReader], [signal_writers.SoundfileWriter])}
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test_file")
        for file_format in formats:
            for Reader in formats[file_format][0]:
                reader = Reader()
                for Writer in formats[file_format][1]:
                    writer = Writer(file_format)
                    assert not os.path.exists(path)
                    writer(signal, path)
                    loaded = reader(path)
                    assert (loaded.channels() == signal.channels()).all()
                    if int(round(signal.sampling_rate())) == 0:
                        assert loaded.sampling_rate() in (signal.sampling_rate(), 1.0)
                    else:
                        assert loaded.sampling_rate() in (signal.sampling_rate(), round(signal.sampling_rate()))
                    assert loaded.offset() == 0
                    assert loaded.labels() == tuple(f"test_file {index}" for index in range(1, len(signal) + 1))
                    os.remove(path)


@hypothesis.given(tests.strategies.signals(max_channels=9, min_value=-255 / 256, max_value=254 / 256))
@hypothesis.settings(deadline=None)
def test_lossless_formats(signal):  # noqa: C901
    # pylint: disable=too-many-branches
    """Tests lossless file formats."""
    # create a dictionary: file format -> [reader classes, writer classes, bits per sample, maximum number of channels]
    try:
        import soundfile    # noqa; pylint: disable=unused-import,import-outside-toplevel; this shall raise an ImportError, if the soundfile library cannot be imported
    except ImportError:
        formats = {sumpf.Signal.file_formats.WAV_UINT8: ([signal_readers.WaveReader], [signal_writers.WaveWriter], 8, 65535),
                   sumpf.Signal.file_formats.WAV_INT16: ([signal_readers.WaveReader], [signal_writers.WaveWriter], 16, 65535),
                   sumpf.Signal.file_formats.WAV_INT32: ([signal_readers.WaveReader], [signal_writers.WaveWriter], 32, 65535),
                   sumpf.Signal.file_formats.AIFF_INT8: ([signal_readers.AifcReader], [signal_writers.AifcWriter], 8, 65535),
                   sumpf.Signal.file_formats.AIFF_INT16: ([signal_readers.AifcReader], [signal_writers.AifcWriter], 16, 65535),
                   sumpf.Signal.file_formats.AIFF_INT32: ([signal_readers.AifcReader], [signal_writers.AifcWriter], 32, 65535)}
    else:
        formats = {sumpf.Signal.file_formats.WAV_UINT8: ([signal_readers.SoundfileReader, signal_readers.WaveReader], [signal_writers.SoundfileWriter, signal_writers.WaveWriter], 8, 65535),
                   sumpf.Signal.file_formats.WAV_INT16: ([signal_readers.SoundfileReader, signal_readers.WaveReader], [signal_writers.SoundfileWriter, signal_writers.WaveWriter], 16, 65535),
                   sumpf.Signal.file_formats.WAV_INT24: ([signal_readers.SoundfileReader], [signal_writers.SoundfileWriter], 24, 65535),
                   sumpf.Signal.file_formats.WAV_INT32: ([signal_readers.SoundfileReader, signal_readers.WaveReader], [signal_writers.SoundfileWriter, signal_writers.WaveWriter], 32, 65535),
                   sumpf.Signal.file_formats.WAV_FLOAT32: ([signal_readers.SoundfileReader], [signal_writers.SoundfileWriter], 32.0, 65535),
                   sumpf.Signal.file_formats.WAV_ULAW: ([signal_readers.SoundfileReader], [signal_writers.SoundfileWriter], -8, 65535),
                   sumpf.Signal.file_formats.WAV_ALAW: ([signal_readers.SoundfileReader], [signal_writers.SoundfileWriter], -8, 65535),
                   sumpf.Signal.file_formats.AIFF_UINT8: ([signal_readers.SoundfileReader], [signal_writers.SoundfileWriter], 8, 65535),
                   sumpf.Signal.file_formats.AIFF_INT8: ([signal_readers.SoundfileReader, signal_readers.AifcReader], [signal_writers.SoundfileWriter, signal_writers.AifcWriter], 8, 65535),
                   sumpf.Signal.file_formats.AIFF_INT16: ([signal_readers.SoundfileReader, signal_readers.AifcReader], [signal_writers.SoundfileWriter, signal_writers.AifcWriter], 16, 65535),
                   sumpf.Signal.file_formats.AIFF_INT24: ([signal_readers.SoundfileReader], [signal_writers.SoundfileWriter], 24, 65535),
                   sumpf.Signal.file_formats.AIFF_INT32: ([signal_readers.SoundfileReader, signal_readers.AifcReader], [signal_writers.SoundfileWriter, signal_writers.AifcWriter], 32, 65535),
                   sumpf.Signal.file_formats.AIFF_FLOAT32: ([signal_readers.SoundfileReader], [signal_writers.SoundfileWriter], 32.0, 65535),
                   sumpf.Signal.file_formats.AIFF_ULAW: ([signal_readers.SoundfileReader], [signal_writers.SoundfileWriter], -8, 65535),
                   sumpf.Signal.file_formats.AIFF_ALAW: ([signal_readers.SoundfileReader], [signal_writers.SoundfileWriter], -8, 65535),
                   sumpf.Signal.file_formats.FLAC_INT8: ([signal_readers.SoundfileReader], [signal_writers.SoundfileWriter], 8, 8),
                   sumpf.Signal.file_formats.FLAC_INT16: ([signal_readers.SoundfileReader], [signal_writers.SoundfileWriter], 16, 8),
                   sumpf.Signal.file_formats.FLAC_INT24: ([signal_readers.SoundfileReader], [signal_writers.SoundfileWriter], 24, 8)}
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test_file")
        for file_format in formats:
            bits, max_channels = formats[file_format][2:]
            if signal.length() < 3:
                continue
            if len(signal) <= max_channels:
                original = signal
            else:
                original = signal[0:max_channels]
            for Reader in formats[file_format][0]:
                reader = Reader()
                for Writer in formats[file_format][1]:
                    writer = Writer(file_format)
                    assert not os.path.exists(path)
                    writer(original, path)
                    loaded = reader(path)
                    # compare the channels
                    if len(signal) == 1 and signal.length() % 2 == 1 and file_format in (sumpf.Signal.file_formats.AIFF_UINT8, sumpf.Signal.file_formats.AIFF_INT8, sumpf.Signal.file_formats.AIFF_ULAW, sumpf.Signal.file_formats.AIFF_ALAW):
                        if loaded.length() != signal.length():
                            assert loaded.length() == signal.length() + 1
                            loaded = loaded[:, 0:-1]
                    if isinstance(bits, int) and bits > 0:      # linear integer samples
                        assert loaded.channels() == pytest.approx(original.channels(), abs=2.0 / (2 ** bits))
                    elif isinstance(bits, int) and bits < 0:    # companded integer samples
                        assert loaded.channels() == pytest.approx(original.channels(), abs=2.0 / (2 ** -bits), rel=10.0 / (2 ** -bits))
                    else:   # linear float samples
                        assert loaded.channels() == pytest.approx(original.channels())
                    # compare the sampling rates
                    if int(round(original.sampling_rate())) == 0:
                        assert loaded.sampling_rate() in (original.sampling_rate(), 1.0)
                    elif file_format not in (sumpf.Signal.file_formats.FLAC_INT8, sumpf.Signal.file_formats.FLAC_INT16, sumpf.Signal.file_formats.FLAC_INT24):
                        assert loaded.sampling_rate() in (original.sampling_rate(), round(original.sampling_rate()))
                    else:
                        if int(round(original.sampling_rate())) < 65536:
                            assert loaded.sampling_rate() == round(original.sampling_rate())
                        elif int(round(original.sampling_rate())) > 655350:
                            assert loaded.sampling_rate() == 655350.0
                        else:
                            assert loaded.sampling_rate() == round(original.sampling_rate(), -1)
                    # compare the metadata
                    assert loaded.offset() == 0
                    assert loaded.labels() == tuple(f"test_file {index}" for index in range(1, len(original) + 1))
                    os.remove(path)


@hypothesis.given(tests.strategies.signals(max_channels=9, min_value=-255 / 256, max_value=254 / 256))
def test_lossy_formats(signal):
    """Tests lossy file formats."""
    pytest.importorskip("soundfile")
    formats = {sumpf.Signal.file_formats.OGG_VORBIS: ([signal_readers.SoundfileReader], [signal_writers.SoundfileWriter], 255)}
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test_file")
        for file_format in formats:
            max_channels = formats[file_format][2]
            if len(signal) <= max_channels:
                original = signal
            else:
                original = signal[0:max_channels]
            for Reader in formats[file_format][0]:
                reader = Reader()
                for Writer in formats[file_format][1]:
                    writer = Writer(file_format)
                    assert not os.path.exists(path)
                    writer(original, path)
                    loaded = reader(path)
                    # just compare the metadata
                    assert loaded.shape() == original.shape()
                    if file_format == sumpf.Signal.file_formats.OGG_VORBIS:
                        assert loaded.sampling_rate() == max(1000.0, min(round(original.sampling_rate()), 200000.0))
                    else:
                        assert loaded.sampling_rate() in (original.sampling_rate(), round(original.sampling_rate()))
                    assert loaded.offset() == 0
                    assert loaded.labels() == tuple(f"test_file {index}" for index in range(1, len(original) + 1))
                    os.remove(path)


def test_autodetect_format_on_reading():
    """Tests if auto-detecting the file format, when reading a file works."""
    signal = sumpf.ExponentialSweep() * 0.9
    with tempfile.TemporaryDirectory() as d:
        for file_format in sumpf.Signal.file_formats:
            if file_format != sumpf.Signal.file_formats.AUTO:
                path = os.path.join(d, "test_file")
                assert not os.path.exists(path)
                try:
                    signal.save(path, file_format)
                except ValueError:  # no writer for the given file found
                    pass
                else:
                    loaded = sumpf.Signal.load(path)
                    assert loaded.shape() == signal.shape()
                    os.remove(path)


def test_autodetect_format_on_saving():
    """Tests if auto-detecting the file format from the file extension, when writing a file works."""
    try:
        import soundfile    # noqa; pylint: disable=unused-import,import-outside-toplevel; this shall raise an ImportError, if the soundfile library cannot be imported
    except ImportError:
        file_formats = [(sumpf.Signal.file_formats.TEXT_CSV, ".csv", signal_readers.CsvReader),
                        (sumpf.Signal.file_formats.TEXT_JSON, ".json", signal_readers.JsonReader),
                        (sumpf.Signal.file_formats.TEXT_JSON, ".js", signal_readers.JsonReader),
                        (sumpf.Signal.file_formats.NUMPY_NPZ, ".npz", signal_readers.NumpyReader),
                        (sumpf.Signal.file_formats.NUMPY_NPY, ".npy", signal_readers.NumpyReader),
                        (sumpf.Signal.file_formats.PYTHON_PICKLE, ".pickle", signal_readers.PickleReader),
                        (sumpf.Signal.file_formats.WAV_INT32, ".wav", signal_readers.WaveReader),
                        (sumpf.Signal.file_formats.AIFF_INT32, ".aiff", signal_readers.AifcReader),
                        (sumpf.Signal.file_formats.AIFF_INT32, ".aifc", signal_readers.AifcReader),
                        (sumpf.Signal.file_formats.AIFF_INT32, ".aif", signal_readers.AifcReader)]
    else:
        file_formats = [(sumpf.Signal.file_formats.TEXT_CSV, ".csv", signal_readers.CsvReader),
                        (sumpf.Signal.file_formats.TEXT_JSON, ".json", signal_readers.JsonReader),
                        (sumpf.Signal.file_formats.TEXT_JSON, ".js", signal_readers.JsonReader),
                        (sumpf.Signal.file_formats.NUMPY_NPZ, ".npz", signal_readers.NumpyReader),
                        (sumpf.Signal.file_formats.NUMPY_NPY, ".npy", signal_readers.NumpyReader),
                        (sumpf.Signal.file_formats.PYTHON_PICKLE, ".pickle", signal_readers.PickleReader),
                        (sumpf.Signal.file_formats.WAV_FLOAT32, ".wav", signal_readers.SoundfileReader),
                        (sumpf.Signal.file_formats.AIFF_FLOAT32, ".aiff", signal_readers.SoundfileReader),
                        (sumpf.Signal.file_formats.AIFF_FLOAT32, ".aifc", signal_readers.SoundfileReader),
                        (sumpf.Signal.file_formats.AIFF_FLOAT32, ".aif", signal_readers.SoundfileReader),
                        (sumpf.Signal.file_formats.FLAC_INT24, ".flac", signal_readers.SoundfileReader),
                        (sumpf.Signal.file_formats.OGG_VORBIS, ".ogg", signal_readers.SoundfileReader),
                        (sumpf.Signal.file_formats.OGG_VORBIS, ".oga", signal_readers.SoundfileReader)]
    signal = sumpf.ExponentialSweep() * 0.9
    with tempfile.TemporaryDirectory() as d:
        for file_format, ending, Reader in file_formats:
            reader = Reader()
            auto_path = os.path.join(d, "test_file" + ending)
            reference_path = os.path.join(d, "test_file")
            assert not os.path.exists(auto_path)
            assert not os.path.exists(reference_path)
            signal.save(auto_path)
            signal.save(reference_path, file_format)
            auto_loaded = sumpf.Signal.load(auto_path)
            reader_loaded = reader(auto_path)
            reference = reader(reference_path)
            assert auto_loaded.shape() == signal.shape()
            assert auto_loaded == reader_loaded
            assert reader_loaded.sampling_rate() == reference.sampling_rate()
            assert reader_loaded.offset() == reference.offset()
            assert (reader_loaded.channels() == reference.channels()).all()
            os.remove(auto_path)
            os.remove(reference_path)
