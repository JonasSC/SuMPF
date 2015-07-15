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

import collections
import copy


class AverageBase(object):
    """
    Abstract base class for averaging classes.
    """
    def __init__(self, values=[]):
        """
        All parameters are optional.
        @param values: a list of values of which the average shall be calculated.
        """
        for v in values:
            self.Add(v)

    def Add(self, value):
        """
        Method to add a value to the list of values which shall be averaged.
        The value can be either a scalar value or a list.
        @param value: the value that shall be added
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def GetAverage(self):
        """
        Calculates the average and returns it.
        Returns 0 if no values have been added.
        Returns a float if float values have been added.
        Returns a list if list values have been added.
        @retval : the average all added values
        """
        result = self._GetAverage()
        if isinstance(result, collections.Iterable):
            return list(result)
        else:
            return result

    def _GetAverage(self):
        """
        Virtual base method for calculating the average and returning it.
        It is only called if self._values != [] and the return value is casted
        to a list if necessary, so the overriding implementations do not need
        to care about this.
        @retval : the average all added values
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

