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

"""Contains the base container class for sampled data (e.g. signals and spectrums)"""

import numpy
import sumpf._internal as sumpf_internal


class SampledData:
    """Base class for data containers with channels of sampled data and labels."""

    def __init__(self, channels, labels):
        """
        :param channels: a two-dimensional :func:`numpy.array`
        :param labels: a sequence of string labels for the channels
        """
        self._channels = channels
        self._labels = sumpf_internal.sanitize_labels(labels=labels, number=len(channels))
        self._length = channels.shape[-1]   # the number of samples per channel

    ###########################################
    # overloaded operators (non math-related) #
    ###########################################

    def __len__(self):
        """Operator overload for retrieving the number of channels with the built-in function :func:`len`.

        :returns: an integer
        """
        return len(self._channels)

    def __eq__(self, other):
        """Operator overload for comparing this signal to another object with ``==``"""
        if self.shape() != other.shape():
            return False
        elif (self._channels != other.channels()).any():
            return False
        elif self._labels != other.labels():
            return False
        return True

    def __ne__(self, other):
        """Operator overload for comparing this object to another object with ``!=``"""
        return not self == other

    def __hash__(self):
        """Operator overload for computing the hash of this object with :func:`hash`"""
        return hash((self._channels.shape,
                     tuple(self._channels.flat),
                     self._labels))

    ####################################
    # overloaded binary math operators #
    ####################################

    def _algebra_function(self, other, function, other_pivot, label):
        """Abstract helper function that shall implement the broadcasting of data
        sets with different shapes when using the overloaded math operators.

        :param other: the object "on the other side of the operator"
        :param function: a function, that implements the computation for arrays (e.g. numpy.add)
        :param other_pivot: a default value, that is used as first operand for samples, where
                            only the other object has data (e.g. when the two data sets don't
                            overlap due to different lengths). If ``other_pivot`` is ``None``,
                            the data from the other object is copied.
        :param label: the string label for the computed channels
        :returns: an instance of the derived class, in which this method has been overridden
        """
        raise NotImplementedError("This method should have been implemented in a derived class.")

    def _algebra_function_right(self, other, function, other_pivot, label):
        """Protected helper function for overloading the right hand side operators.

        :param other: the object "on the left side of the operator"
        :param function: a function, that implements the computation for arrays (e.g. numpy.add)
        :param other_pivot: a default value, that is used as first operand for samples, where
                            only the other object has data (e.g. when the two data sets don't
                            overlap due to different lengths). If ``other_pivot`` is ``None``,
                            the data from the other object is copied.
        :param label: the string label for the computed channels
        :returns: an instance of the derived class, in which this method has been overridden
        """
        raise NotImplementedError("This method should have been implemented in a derived class.")

    def __add__(self, other):
        """Operator overload for adding this to another data set, an array or number."""
        return self._algebra_function(other=other, function=numpy.add, other_pivot=None, label="Sum")

    def __radd__(self, other):
        """Right hand side operator overload for adding this to an array or number."""
        return self._algebra_function_right(other=other, function=numpy.add, other_pivot=None, label="Sum")

    def __sub__(self, other):
        """Operator overload for subtracting another data set, an array or number from this."""
        return self._algebra_function(other=other, function=numpy.subtract, other_pivot=0.0, label="Difference")

    def __rsub__(self, other):
        """Right hand side operator overload for subtracting this from an array or number."""
        return self._algebra_function_right(other=other, function=numpy.subtract, other_pivot=0.0, label="Difference")

    def __mul__(self, other):
        """Operator overload for multiplying this with another data set, an array or number."""
        return self._algebra_function(other=other, function=numpy.multiply, other_pivot=None, label="Product")

    def __rmul__(self, other):
        """Right hand side operator overload for multiplying this with an array or number."""
        return self._algebra_function_right(other=other, function=numpy.multiply, other_pivot=None, label="Product")

    def __truediv__(self, other):
        """Operator overload for dividing this by another data set, an array or number."""
        return self._algebra_function(other=other, function=numpy.true_divide, other_pivot=1.0, label="Quotient")

    def __rtruediv__(self, other):
        """Right hand side operator overload for dividing an array or number by this."""
        return self._algebra_function_right(other=other, function=numpy.true_divide, other_pivot=1.0, label="Quotient")

    def __pow__(self, other):
        """Operator overload for computing the power of this to another data set, an array or number."""
        return self._algebra_function(other=other, function=numpy.power, other_pivot=None, label="Power")

    def __rpow__(self, other):
        """Operator overload for computing the power of an array or number to this."""
        return self._algebra_function_right(other=other, function=numpy.power, other_pivot=None, label="Power")

    #######################################################
    # parameters, that have been set with the constructor #
    #######################################################

    def channels(self):
        """Returns the channel data.

        :returns: a :func:`numpy.array`
        """
        return self._channels

    def labels(self):
        """Returns the labels for the channels.

        :returns: a sequence of strings
        """
        return self._labels

    ######################
    # derived parameters #
    ######################

    def length(self):
        """Returns the number of samples per channel.

        :returns: an integer
        """
        return self._length

    def shape(self):
        """Returns the shape of the channels array.

        :returns: a tuple of integers (number of channels, number of samples)
        """
        return self._channels.shape
