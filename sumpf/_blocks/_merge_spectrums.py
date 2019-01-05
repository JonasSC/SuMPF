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

"""Contains the MergeSpectrums class"""

import connectors
import numpy
import sumpf
import sumpf._internal as sumpf_internal

__all__ = ("MergeSpectrums",)


class MergeSpectrums:
    """Merges multiple spectrums into one.
    The resulting spectrums will have the resolution of the first spectrum. If the
    merged spectrums differ in length, the missing samples will be filled with
    zeros.

    The methods of this class are enhanced with the functionality of the *Connectors*
    package, so that instances of this class can be connected in a processing network.
    """
    modes = sumpf_internal.MergeMode

    def __init__(self, spectrums=(), mode=sumpf_internal.MergeMode.FIRST_DATASET_FIRST):
        """
        :param spectrums: a sequence of :class:`~sumpf.Spectrum` instances
        :param mode: a value from the :attr:`~sumpf.MergeSpectrums.modes` enumeration
        """
        self.__spectrums = connectors.MultiInputData()
        for s in spectrums:
            self.__spectrums.add(s)
        self.__mode = mode

    @connectors.Output()
    def output(self):
        """Computes the merged spectrum and returns it.

        :returns: a :class:`~sumpf.Spectrum` instance
        """
        if len(self.__spectrums) == 0:            # pylint: disable=len-as-condition
            return sumpf.Spectrum()
        elif len(self.__spectrums) == 1:
            return next(iter(self.__spectrums.values()))    # simply return the first and only spectrum
        else:
            # find the number of channels and the merged spectrum's length
            number_of_channels = sum(len(s) for s in self.__spectrums.values())
            length = max(s.length() for s in self.__spectrums.values())
            channels = sumpf_internal.allocate_array(shape=(number_of_channels, length), dtype=numpy.complex128)
            labels = [""] * number_of_channels
            # fill in the data
            if self.__mode == MergeSpectrums.modes.FIRST_DATASET_FIRST:
                self.__first_dataset_first(channels, length, labels)
            elif self.__mode == MergeSpectrums.modes.FIRST_CHANNELS_FIRST:
                self.__first_channels_first(channels, labels)
            else:
                raise ValueError("invalid mode: {}".format(self.__mode))
            # create and return the result
            return sumpf.Spectrum(channels=channels,
                                  resolution=next(iter(self.__spectrums.values())).resolution(),
                                  labels=labels)

    @connectors.MultiInput("output")
    def add(self, spectrum):
        """Adds a spectrum to the end of the sequence of spectrum, which shall be
        merged. This method returns an ID, which can be passed to the :meth:`~sumpf.MergeSpectrums.remove`
        and :meth:`~sumpf.MergeSpectrums.replace` methods in order to remove or
        replace this spectrum.

        :param spectrum: a :class:`~sumpf.Spectrum` instance
        :returns: a unique identifier
        """
        return self.__spectrums.add(spectrum)

    @add.remove
    def remove(self, spectrum_id):
        """Removes a spectrum, that is specified by the given ID, from the sequence
        of spectrums, which shall be merged.

        :param spectrum_id: the unique identifier, under which the referred spectrum is stored
        """
        del self.__spectrums[spectrum_id]

    @add.replace
    def replace(self, spectrum_id, spectrum):
        """Replaces a spectrum, that is specified by the given ID, with another one.

        :param spectrum_id: the unique identifier, under which the referred spectrum is stored
        :param spectrum: the new :class:`~sumpf.Spectrum` instance
        """
        self.__spectrums[spectrum_id] = spectrum

    @connectors.Input("output")
    def set_mode(self, mode):
        """Sets the mode by which the channels of the merged spectrum are ordered.

        :param mode: a value from the :attr:`~sumpf.MergeSpectrums.modes` enumeration
        """
        self.__mode = mode

    def __first_dataset_first(self, channels, length, labels):
        """Implementation of the `FIRST_DATASET_FIRST` merging strategy."""
        c = 0
        for spectrum in self.__spectrums.values():
            stop = spectrum.length()
            next_c = c + len(spectrum)
            channels[c:next_c, 0:stop] = spectrum.channels()
            if stop < length:
                channels[c:next_c, stop:] = 0.0
            labels[c:c + len(spectrum.labels())] = spectrum.labels()
            c = next_c

    def __first_channels_first(self, channels, labels):
        """Implementation of the `FIRST_CHANNELS_FIRST` merging strategy."""
        number_of_channels, length = channels.shape
        c = 0   # the channel index in the merged spectrum
        d = 0   # the channel index in the input spectrums
        while c < number_of_channels:
            for spectrum in self.__spectrums.values():
                if d < len(spectrum):
                    stop = spectrum.length()
                    channels[c, 0:stop] = spectrum.channels()[d]
                    if stop < length:
                        channels[c, stop:] = 0.0
                    labels[c] = spectrum.labels()[d]
                    c += 1
            d += 1
