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

"""Contains classes and helper functions to load spectrograms from a file."""

import json
import pickle
import numpy
import sumpf
from .._functions import allocate_array

__all__ = ("readers", "Reader")

readers = {}    # maps file extensions to reader instances, that can be used for future loading of a spectrogram


def from_dict(channels, dictionary):
    """Deserializes a spectrogram from a dictionary."""
    return sumpf.Spectrogram(channels=channels,
                             resolution=dictionary.get("resolution", 1.0),
                             sampling_rate=dictionary.get("sampling_rate", 48000.0),
                             offset=dictionary.get("offset", 0),
                             labels=dictionary.get("labels", ()))


class Reader:
    """Base class for readers, that load :class:`~sumpf.Spectrum` instances from
    a file.

    Derived classes must implement the ``__call__`` method, that accepts the path to
    the file and returns the loaded spectrum. If anything goes wrong, the method
    shall raise an error (instead of returning None).
    """


class JsonReader(Reader):
    """Reads a JSON representation of a spectrogram from a file."""
    extensions = (".json", ".js")

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Spectrogram` from the given path.

        :param path: the path of the file, from which the spectrogram shall be loaded
        :returns: a :class:`~sumpf.Spectrogram` instance
        """
        with open(path) as f:
            data = json.load(f)
            if "channels" in data:
                number_of_channels = len(data["channels"])
                if number_of_channels:
                    number_of_bins = len(data["channels"][0]["real"])
                    if number_of_bins:
                        number_of_samples = len(data["channels"][0]["real"][0])
                        if number_of_samples:
                            channels = allocate_array(shape=(number_of_channels,
                                                             number_of_bins,
                                                             number_of_samples),
                                                      dtype=numpy.complex128)
                            for i, c in enumerate(data["channels"]):
                                numpy.multiply(1j, c["imaginary"], out=channels[i])
                                numpy.add(channels[i], c["real"], out=channels[i])
                        else:
                            channels = numpy.empty(shape=(1, 0), dtype=numpy.complex128)
                    else:
                        channels = numpy.empty(shape=(1, 0), dtype=numpy.complex128)
                else:
                    channels = numpy.empty(shape=(1, 0), dtype=numpy.complex128)
            else:
                channels = numpy.empty(shape=(1, 0), dtype=numpy.complex128)
            return from_dict(channels, data)


class NumpyReader(Reader):
    """Reads a spectrum from a :mod:`numpy` file."""
    extensions = (".npz",)

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Spectrum` from the given path.

        :param path: the path of the file, from which the spectrum shall be loaded
        :returns: a :class:`~sumpf.Spectrum` instance
        """
        with numpy.load(path) as data:
            channels = allocate_array(shape=data["channels"].shape, dtype=numpy.complex128)
            channels[:] = data["channels"]
            return from_dict(channels, data)


class PickleReader(Reader):
    """Reads a :mod:`pickle` serialization of a spectrum from a file.
    The loaded spectrum can also be an instance of a sub-class of :class:`~sumpf.Spectrum`.

    .. warning::

       Since this reader basically executes Python code from the read file, it can
       be a security hazard, that executes malicious code, when reading prepared
       files.
    """
    extensions = (".pickle",)

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Spectrum` from the given path.

        :param path: the path of the file, from which the spectrum shall be loaded
        :returns: a :class:`~sumpf.Spectrum` instance
        """
        with open(path, "rb") as f:
            result = pickle.load(f)
            assert isinstance(result, sumpf.Spectrogram)
            return result
