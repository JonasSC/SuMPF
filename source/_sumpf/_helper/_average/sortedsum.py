# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2015 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from .base import AverageBase

try:
    import numpy
except ImportError:
    # This is a dirty import that has to be made cleaner one day
    # Do not remove the comment line below, because it is needed by a unit test
    # sumpf.helper.numpydummy
    import _sumpf._helper.numpydummy as numpy



class SortedSum(AverageBase):
    """
    DO NOT USE THIS ALGORITHM
    Somehow the SumDirectly algorithm seems to be more precise than this one,
    although the sorting of the values promises to reduce errors due to limited
    floating point precision.
    Maybe this is because Python can optimize simple algorithms like SumDirectly
    by itself, so it performs better.
    Since this algorithm is less precise than the SumDirectly algorithm, there
    is nothing left that justifies the massively larger memory consumption of this
    algorithm.
    At least the SumList algorithm seems to be more precise than the SumDirectly.

    A class that calculates the average through the simple algorithm of summing
    all values up and then dividing that sum through the number of values.
    To reduce the problem with limited floating point precision, the values are
    sorted before summing them up. This of course makes it necessary to store
    each added value in a list, which can use up a lot of memory, when an average
    of many values shall be calculated.
    This algorithm has no advantage over the SumDirectly-algorithm, when the
    added values are not (really) sortable (e.g. lists or complex numbers).

    Advantages of this method:
        - Adding a value is the relatively simple task of appending the value to
        the list. So the averaging process does not interfere with the data
        creation process.
        - If the added values have a different order of magnitude, the sorting
        before summing them up seems to be a good way to reduce floating point
        precision errors
    Disadvantages:
        - Storing all the values uses a lot of space.
        - The sorting is a relatively complex procedure, which increases the
        effort to calculate the average.
        - If the sum of the values gets large compared to the values, these
        values might become under represented because of the limited float
        precision.
        - Sorting does not necessarily help when averaging lists. On some other
        values, like complex numbers, it is even impossible.
    """
    def __init__(self, values=[]):
        """
        All parameters are optional.
        @param values: a list of values of which the average shall be calculated.
        """
        self.__values = []
        AverageBase.__init__(self, values=values)


    def Add(self, value):
        """
        Method to add a value to the list of values which shall be averaged.
        The value can be either a scalar value or a list.
        @param value: the value that shall be added
        """
        self.__values.append(value)

    def _GetAverage(self):
        """
        Calculates the average and returns it.
        @retval : the average all added values
        """
        if len(self.__values) == 0:
            return 0.0
        else:
            try:    # Try to sort the list to reduce errors due to limited floating point precision
                self.__values.sort()
            except TypeError:
                pass
            summed = self.__values[0]
            for v in self.__values[1:]:
                summed = numpy.add(summed, v)
            result = numpy.divide(summed, float(len(self.__values)))
            return result

