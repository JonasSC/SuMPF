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



class SumList(AverageBase):
    """
    A class that calculates the average through a list in which the sums of the
    previously added values are stored.
    If the list is empty, a new value will simply be added to the list.
    If a new value shall be written to a cell that already contains a value, the
    sum of these two values is calculated and written to the next cell, while the
    current cell is reset to None.
    The final average is calculated by summing up all the values in the list and
    divide them by the number of added values.

    An Example:
        avg = SumList()
            # initialize the instance with an empty list
            # the list is now: []
        avg.Add(1)
            # the list is empty, so append the added value to the end of the list
            # the list is now: [1]
        avg.Add(2)
            # the first element is not None, so sum up the first element and the added value
            # the second value does not exist, so append the sum to the end of the list
            # the list is now: [None, 3]
        avg.Add(3)
            # the first element is None, so replace that with the added value
            # the list is now: [3, 3]
        avg.Add(4)
            # the first element is not None, so sum up the first element and the added value
            # the second element is not None, so add up the second element and the sum
            # the third value does not exist, so append the final sum to the end of the list
            # the list is now: [None, None, 10]
        avg.Add(5)
            # the first element is None, so replace that with the added value
            # the list is now: [5, None, 10]
        a = avg.GetAverage()
            # the not-None elements are 5 and 10, so the sum of all added values is 15
            # the not-None elements are in position 0 and 2, so the number of added values is 2**0 + 2**2 = 1 + 4 = 5
            # the average is the sum of all added values divided by their number
            # the return value a is 15 / 5 = 3

    Advantages of this method:
        - Instead of storing the added values, only some averages are stored, so
        The memory usage has only the complexity of O(log2(n)).
        - If the added values are in the same order of magnitude, this algorithm
        will sum up those values in a way, that the summands have about the same
        order of magnitude as well. This way, errors due to limited floating point
        are reduced.
        - No sorting is necessary to achieve acceptable precision. So this algorithm
        also works well with unsortable values like lists or complex numbers.
    Disadvantages:
        - Adding a value to the list is more complicated compared to other
        averaging algorithms.
        - The summing of the added values is not optimal, if the added values
        have different orders of magnitude. In this case, the SortedSum-Algorithm
        is better in reducing the errors of limited floating point precision
        (but only if the values are sortable).
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
        if len(self.__values) == 0:
            self.__values.append(value)
        else:
            for i in range(len(self.__values)):
                if self.__values[i] is None:
                    self.__values[i] = value
                    break
                else:
                    value = numpy.add(self.__values[i], value)
                    self.__values[i] = None
                    if len(self.__values) == i + 1:
                        self.__values.append(value)

    def _GetAverage(self):
        """
        Calculates the average and returns it.
        @retval : the average all added values
        """
        if len(self.__values) == 0:
            return 0.0
        else:
            i = 0
            while self.__values[i] is None:
                i += 1
            n = 2.0 ** i
            s = self.__values[i]
            for j in range(i + 1, len(self.__values)):
                if self.__values[j] is not None:
                    n += 2.0 ** j
                    s = numpy.add(s, self.__values[j])
            return numpy.divide(s, n)

