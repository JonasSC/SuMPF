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



class SumDirectly(AverageBase):
    """
    The classical algorithm to calculate an average. All values are summed up directly
    when they are added to the averager. The final result is calculated by dividing
    this sum by the number of added values.

    Advantages of this method:
        - Both adding a value to the averager and calculating the final result
        are relatively simple operations
        - Since only the sum of all elements is stored, the memory consumption
        of this algorithm is low.
    Disadvantages:
        - It uses no "tricks" to reduce errors that are caused by limited floating
        point precision.
    """
    def __init__(self, values=[]):
        """
        All parameters are optional.
        @param values: a list of values of which the average shall be calculated.
        """
        self.__sum = None
        self.__count = 0
        AverageBase.__init__(self, values=values)

    def Add(self, value):
        """
        Method to add a value to the list of values which shall be averaged.
        The value can be either a scalar value or a list.
        @param value: the value that shall be added
        """
        if self.__sum is None:
            self.__sum = value
        else:
            self.__sum = numpy.add(self.__sum, value)
        self.__count += 1

    def _GetAverage(self):
        """
        Calculates the average and returns it.
        @retval : the average all added values
        """
        if self.__sum is None:
            return 0.0
        else:
            return numpy.divide(self.__sum, float(self.__count))

