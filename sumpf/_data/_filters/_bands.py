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

"""contains the class for :class:`~sumpf.Bands`-filter"""

import collections.abc
import numpy
import sumpf._internal as sumpf_internal
from ._base import Filter

__all__ = ("Bands",)


class Bands(Filter):
    """A filter, that is defined by supporting points and functions for interpolation
    and extrapolation. Use cases for this filter include storing the result of an
    n-th octave analysis or reading an equalization and applying it to a :class:`~sumpf.Signal`.
    """

    interpolations = sumpf_internal.Interpolations              #: an enumeration with flags for defining the interpolation and extrapolation functions
    file_formats = sumpf_internal.filter_writers.BandsFormats   #: an enumeration with file formats, whose flags can be passed to :meth:`~sumpf.Bands.save`

    def __init__(self,
                 bands=({},),
                 interpolations=sumpf_internal.Interpolations.LOGARITHMIC,
                 extrapolations=sumpf_internal.Interpolations.STAIRS_LIN,
                 labels=("Bands",)):
        """
        :param bands: a sequence of dictionaries, that map float frequency values
                      to complex values of the filter function. This can also be
                      a single dictionary, if the bands filter shall only have one
                      channel.
        :param interpolation: a sequence of flags from the :class:`sumpf.Bands.interpolations`
                              enumeration, that defines the function, with which
                              the interpolation between the samples given in the
                              ``bands`` dictionary shall be computed. This can also
                              be a single flag, if the same interpolation shall
                              be used for all channels.
        :param extrapolation: a sequence of flags from the :class:`sumpf.Bands.interpolations`
                              enumeration, that defines the function, with which
                              the extrapolation outside the samples given in the
                              ``bands`` dictionary shall be computed. This can also
                              be a single flag, if the same extrapolation shall
                              be used for all channels.
        :param labels: a sequence of string labels for the channels.
        """
        # make sure, that all data is in sequences with the correct length
        if isinstance(bands, collections.abc.Mapping):
            bands = (bands,)
        if not isinstance(interpolations, collections.abc.Sequence):
            interpolations = (interpolations,) * len(bands)
        elif len(interpolations) < len(bands):
            interpolations = tuple(interpolations) + (interpolations[-1],) * (len(bands) - len(interpolations))
        if not isinstance(extrapolations, collections.abc.Sequence):
            extrapolations = (extrapolations,) * len(bands)
        elif len(extrapolations) < len(bands):
            extrapolations = tuple(extrapolations) + (extrapolations[-1],) * (len(bands) - len(extrapolations))
        if not isinstance(labels, collections.abc.Sequence):
            labels = (labels,) * len(bands)
        elif len(labels) < len(bands):
            labels = tuple(labels) + (labels[0] if labels else "Bands",) * (len(bands) - len(labels))
        # create the transfer functions
        tfs = []
        for b, i, e in zip(bands, interpolations, extrapolations):
            fs = numpy.array(sorted(b.keys()))
            tf = Bands.Bands(xs=fs,
                             ys=numpy.array([b[x] for x in fs]),
                             interpolation=i,
                             extrapolation=e)
            tfs.append(tf)
        # initialize the filter
        Filter.__init__(self,
                        transfer_functions=tfs,
                        labels=labels)
        # store the original data
        self.__bands = bands
        self.__interpolations = [int(i) for i in interpolations[0:len(tfs)]]
        self.__extrapolations = [int(e) for e in extrapolations[0:len(tfs)]]

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the bands filter, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        return (f"{self.__class__.__name__}(bands={self.__bands!r}, "
                f"interpolations={self.__interpolations}, "
                f"extrapolations={self.__extrapolations}, "
                f"labels={self.labels()})")

    def save(self, path, file_format=file_formats.AUTO):
        """Saves the bands filter to a file. The file will be created if it does not exist.

        :param path: the path to the file
        :param file_format: an optional flag from the :attr:`sumpf.Bands.file_formats`
                            enumeration, that specifies the file format, in which
                            the bands filter shall be stored. If this parameter
                            is omitted or set to :attr:`~sumpf.Bands.file_formats`.\ ``AUTO``,
                            the format will be guessed from the ending of the filename.
        :returns: self
        """
        writer = sumpf_internal.get_writer(file_format=file_format,
                                           writers=sumpf_internal.filter_writers.bands_writers,
                                           writer_base_class=sumpf_internal.filter_writers.Writer)
        writer(self, path)
        return self

    def to_db(self, reference=1.0, factor=20.0):
        """Computes a bands filter with the values of this filter converted to
        decibels. It will use the same interpolation and extrapolation functions
        as the original filter.

        This method takes the values from the bands filter as they are, which might
        not make sense in case of complex of negative filter values. Consider
        computing the magnitude of the filter by using the :func:`abs` function
        before calling this method.

        :param reference: the value, by which the filter's values are divided before
                          computing the logarithm. Usually, this is one, but for
                          example when converting a filter in Pascal to dB[SPL],
                          the reference must be set to 20e-6.
        :param factor: the factor, with which the logarithm is multiplied. Use
                       20 for root-power quantities (if the bands' values are amplitudes)
                       and 10 for power quantities (if the bands' values are energies
                       or powers).
        """
        return Bands(bands=[{f: factor * numpy.log10(y / reference) for f, y in b.items()} for b in self.__bands],
                     interpolations=self.__interpolations,
                     extrapolations=self.__extrapolations,
                     labels=self.labels())

    def from_db(self, reference=1.0, factor=20.0):
        """Computes a bands filter with the values of this filter converted from
        decibels to a linear representation. It will use the same interpolation
        and extrapolation functions as the original filter.

        :param reference: the value, by which the filter's values are divided before
                          computing the logarithm. Usually, this is one, but for
                          example when converting a filter in dB[SPL] to Pascal
                          the reference must be set to 20e-6.
        :param factor: the factor, with which the logarithm is multiplied. Use
                       20 for root-power quantities (if the bands' values are amplitudes)
                       and 10 for power quantities (if the bands' values are energies
                       or powers).
        """
        return Bands(bands=[{f: reference * 10.0 ** (y / factor) for f, y in b.items()} for b in self.__bands],
                     interpolations=self.__interpolations,
                     extrapolations=self.__extrapolations,
                     labels=self.labels())
