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

"""Contains classes and helper functions to load filters from a file."""

import collections
import csv
import itertools
import json
import os
import pickle
import re
import numpy
import sumpf
import sumpf._internal as sumpf_internal

__all__ = ("readers", "Reader")

readers = {}    # maps file extensions to reader instances, that can be used for future loading of a filter


def term_from_dict(dictionary):
    """A helper function for deserializing sub-classes of :class:`~sumpf._data._filters._base._terms._base.Term`
    from a dictionary with the required parameters. This function operates recursively,
    so nested terms are also instantiated during the deserialization.

    :param dictionary: a dictionary as it is returned by the
                       :meth:`~sumpf._data._filters._base._terms._base.Term.as_dict`
                       method of terms.
    :returns: a term instance
    """
    parameters = {}
    terms = {"Sum": sumpf.Filter.Sum,
             "Difference": sumpf.Filter.Difference,
             "Product": sumpf.Filter.Product,
             "Quotient": sumpf.Filter.Quotient,
             "Constant": sumpf.Filter.Constant,
             "Polynomial": sumpf.Filter.Polynomial,
             "Exp": sumpf.Filter.Exp,
             "Bands": sumpf.Filter.Bands,
             "Absolute": sumpf.Filter.Absolute,
             "Negative": sumpf.Filter.Negative}
    cls = None
    for name in dictionary:
        if name == "type":
            cls = terms[dictionary["type"]]
        else:
            parameter = dictionary[name]
            if isinstance(parameter, collections.abc.Mapping):
                if "type" in parameter:
                    parameters[name] = term_from_dict(parameter)
                elif {"real", "imaginary"} == parameter.keys():
                    real = parameter["real"]
                    imaginary = parameter["imaginary"]
                    a = numpy.empty(shape=numpy.shape(real), dtype=numpy.complex128)
                    a[:] = imaginary
                    a *= 1j
                    a += real
                    parameters[name] = a
                else:
                    parameters[name] = parameter
            elif isinstance(parameter, collections.abc.Iterable):
                values = []
                for p in parameter:
                    if isinstance(p, collections.abc.Mapping) and "type" in p:
                        values.append(term_from_dict(p))
                    else:
                        values.append(p)
                parameters[name] = values
            else:
                parameters[name] = parameter
    return cls(**parameters)


class Reader:
    """Base class for readers, that load :class:`~sumpf.Filter` instances from a file.

    Derived classes must implement the ``__call__`` method, that accepts the path to
    the file and returns the loaded filter. If anything goes wrong, the method
    shall raise an error (instead of returning None).
    """


class ReprReader(Reader):
    """Reads a :func:`repr`-string of a filter from a file and evaluates it.

    .. warning::

       Since this reader basically executes Python code from the read file, it can
       be a security hazard, that executes malicious code, when reading prepared
       files.
    """
    extensions = (".txt",)

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Filter` from the given path.

        :param path: the path of the file, from which the filter shall be loaded
        :returns: a :class:`~sumpf.Filter` instance
        """
        with open(path) as f:
            result = eval(f.read(), {}, {"Filter": sumpf.Filter,    # pylint: disable=eval-used
                                         "Bands": sumpf.Bands,
                                         "Interpolations": sumpf_internal.Interpolations,
                                         "array": numpy.array,
                                         "float64": numpy.float64,
                                         "complex128": numpy.complex128})
            assert isinstance(result, sumpf.Filter)
            return result


class JsonReader(Reader):
    """Reads a JSON representation of a filter from a file."""
    extensions = (".json", ".js")

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Filter` from the given path.

        :param path: the path of the file, from which the filter shall be loaded
        :returns: a :class:`~sumpf.Filter` instance
        """
        with open(path) as f:
            data = json.load(f)
            transfer_functions = [term_from_dict(tf) for tf in data["transfer_functions"]]
            return sumpf.Filter(transfer_functions=transfer_functions,
                                labels=data["labels"])


class PickleReader(Reader):
    """Reads a :mod:`pickle` serialization of a filter from a file.
    The loaded filter can also be an instance of a sub-class of :class:`~sumpf.Filter`.

    .. warning::

       Since this reader basically executes Python code from the read file, it can
       be a security hazard, that executes malicious code, when reading prepared
       files.
    """
    extensions = (".pickle",)

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Filter` from the given path.

        :param path: the path of the file, from which the filter shall be loaded
        :returns: a :class:`~sumpf.Filter` instance
        """
        with open(path, "rb") as f:
            result = pickle.load(f)
            assert isinstance(result, sumpf.Filter)
            return result

######################################################
# Reader classes, that can only read Bands instances #
######################################################


class TableReader(Reader):
    """Reads a :class:`~sumpf.Bands` instance from a text file with a comma-,
    tab-, whitespace- or pipe-separated table.

    The first column is interpreted as the frequency in Hz, while all subsequent
    columns are interpreted as the filter's channels. Real valued samples are
    interpreted as being given in dB, while complex valued samples are assumed to
    be linear.

    Complex numbers can be specified in the notation used by Python (1.0+2.0j) or
    by gnuplot (\{1.0,2.0\}). The ``j`` can alternatively be an upper case ``J``
    or an upper or lower case ``i``/``I``.

    Everything behind a ``;`` or a ``#`` is considered a comment and is ignored.
    Empty lines (or those, which start with a comment) are also ignored.

    Lines, that have less columns as other lines are interpreted as if values were
    only specified for the first channels.
    """
    extensions = (".txt", ".dat", ".asc", ".tab")

    def __call__(self, path):   # noqa; ignore flake8's complexity warning
        """Attempts to load a :class:`~sumpf.Filter` from the given path.

        :param path: the path of the file, from which the filter shall be loaded
        :returns: a :class:`~sumpf.Filter` instance
        """
        # pylint: disable=too-many-locals,too-many-nested-blocks,too-many-branches; disable pylint's complexity warnings
        unsigned = "(?:(?:\d+.?\d*e[+-]?\d+)|(?:\d+\.?\d*)|(?:\.\d+))"
        real = f"(?:-?{unsigned})"
        complex_parentheses = f"(?:\({real} *[+-] *{unsigned}[jJiI])\)"
        complex_ = f"(?:{real}[+-]{unsigned}[jJiI])"
        gnuplot = r"(?:\{-?%s *, *-?%s\})" % (unsigned, unsigned)
        nan = "(?:[nN]a[nN])|(?:\{[nN]a[nN] *, *[nN]a[nN]\})"
        mask = re.compile(f"(({gnuplot})|({complex_parentheses})|({complex_})|({real})|({nan}))")
        nan_mask = re.compile(f"^{nan}")    # checks if the line starts with a NaN-value
        all_bands = [None]
        frequency = None
        with open(path) as f:
            for l in f:
                line = l.split("#")[0].split(";")[0].strip()    # remove comments and surrounding white spaces
                if line:
                    if not (line[0].isdigit() or nan_mask.match(line)):
                        raise ValueError("The file does not seem to be a tabular representation of a Bands filter")
                    for i, (match, bands) in enumerate(itertools.zip_longest(mask.finditer(line), all_bands)):
                        g, p, c, r, n = match.groups()[1:]  # find out, what kind of number (real, gnuplot, ...) is found by checking which group is not None
                        if i == 0:
                            if r is not None:
                                frequency = float(r)
                            elif n is not None:
                                frequency = None
                            else:
                                raise OSError(f"could not interpret the frequency values in {line}")
                        else:
                            if bands is None:
                                bands = {}
                                all_bands.append(bands)
                            if frequency is not None:
                                if r is not None:       # a real number found
                                    bands[frequency] = float(r)
                                elif c is not None:     # a complex number found
                                    bands[frequency] = complex(c.rstrip("jJiI") + "j")
                                elif p is not None:     # a complex number in parentheses found
                                    bands[frequency] = complex(p.lstrip("(").rstrip(")").replace(" ", "").rstrip("jJiI") + "j")     # pylint: disable=line-too-long
                                elif g is not None:     # a complex number in gnuplot syntax found
                                    real, imaginary = g.lstrip("{").rstrip("}").split(",")
                                    bands[frequency] = float(real.strip()) + 1j * float(imaginary.strip())
        filename = os.path.split(path)[-1]
        return sumpf.Bands(bands=all_bands[1:],
                           labels=[f"{filename} {i}" for i in range(1, len(all_bands))])


class CsvReader(Reader):
    """Loads the spectrum from a CSV file, in which the first column contains the
    frequency samples.
    """
    extensions = (".csv",)

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Spectrum` from the given path.

        :param path: the path of the file, from which the spectrum shall be loaded
        :returns: a :class:`~sumpf.Spectrum` instance
        """
        with open(path, newline="") as f:
            reader = csv.reader(f)
            bands = []
            first_row = next(reader)
            # try to read the labels from the first row
            try:
                self.__process_row(bands, first_row)
            except ValueError:
                labels = tuple(first_row[1:])
            else:
                filename = os.path.split(path)[-1]
                labels = [f"{filename} {i}" for i in range(1, len(first_row))]
            # read the frequency samples
            for current_row in reader:
                self.__process_row(bands, current_row)
            # create the Filter instance
        return sumpf.Bands(bands=bands, labels=labels)

    def __process_row(self, bands, row):    # pylint: disable=no-self-use; this function only makes sense in the context of the CsvReader class
        """A helper method, that parses one row of the CSV file"""
        while len(bands) < len(row) - 1:
            bands.append({})
        if row[0]:
            frequency = float(row[0])
            values = [complex(c) if c else None for c in row[1:]]
            for c, d in zip(values, bands):
                if c is not None:
                    d[frequency] = c


class NumpyReader(Reader):
    """Reads a bands filter from a :mod:`numpy` file."""
    extensions = (".npz", ".npy")

    def __call__(self, path):
        """Attempts to load a :class:`~sumpf.Bands` from the given path.

        :param path: the path of the file, from which the bands filter shall be loaded
        :returns: a :class:`~sumpf.Bands` instance
        """
        try:
            with numpy.load(path) as data:
                frequencies = data["frequencies"]
                channels = data["channels"].transpose()
                interpolations = tuple(data["interpolations"])
                extrapolations = tuple(data["extrapolations"])
                labels = tuple(data["labels"])
        except AttributeError:  # npy files cannot be opened with a context manager
            array = numpy.load(path).transpose()
            frequencies = array[0].real
            channels = array[1:]
            interpolations = sumpf_internal.Interpolations.LINEAR
            extrapolations = sumpf_internal.Interpolations.STAIRS_LIN
            filename = os.path.split(path)[1]
            labels = [f"{filename} {i}" for i in range(1, len(array))]
        bands = []
        for c in channels:
            band = {f: s for f, s in zip(frequencies, c) if not numpy.isnan(s)}
            bands.append(band)
        return sumpf.Bands(bands=bands,
                           interpolations=interpolations,
                           extrapolations=extrapolations,
                           labels=labels)
