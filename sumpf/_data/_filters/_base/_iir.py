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

"""Contains base classes for IIR filters"""

from ._filter import Filter


class IIRFilter(Filter):
    """Base class for single channel IIR filters"""

    def __init__(self, transfer_function, label, order):
        """
        :param transfer_function: the transfer function as a Term instance
        :param label: a string label for the channel
        :param order: the filter order as an integer
        """
        Filter.__init__(self, transfer_functions=(transfer_function,), labels=(label,))
        # store the parameters
        self.__order = order

    def order(self):
        """Returns the filter order.

        :returns: an integer
        """
        return self.__order


class RolloffFilter(IIRFilter):
    """Base class for lowpass or highpass filters"""

    def __init__(self, transfer_function, label, cutoff_frequency, order, highpass):
        """
        :param transfer_function: the transfer function as a Term instance
        :param label: a string label for the channel
        :param cutoff_frequency: the cutoff_frequency in Hz
        :param order: the filter order as an integer
        :param highpass: a boolean, that is True, if the filter is a highpass
        """
        IIRFilter.__init__(self, transfer_function=transfer_function, label=label, order=order)
        self.__cutoff_frequency = cutoff_frequency
        self.__is_highpass = highpass

    def cutoff_frequency(self):
        """Returns the cutoff frequency of the filter in Hz.

        :returns: a float
        """
        return self.__cutoff_frequency

    def is_highpass(self):
        """Returns if the filter is a highpass filter.

        :returns: True, if the filter is a highpass filter, False otherwise
        """
        return self.__is_highpass
