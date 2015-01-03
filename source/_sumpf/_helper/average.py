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

"""
This name space contains some implementations of an averaging algorithm.
Currently there are two implementations of an averaging algorithm available:
  SumDirectly is the classical approach of summing up all the elements and then
    dividing by their number. The summing of the elements is done directly, when
    an element is added, so only one element (the sum) has to be stored in the
    memory.
  SortedSum tries to reduce errors that are caused by limited floating point
    precision by storing all added values in a list and sorting the list before
    adding the values up. This of course uses a lot of memory, to store each added
    value. And sorting the list might not be a cheap operation.
  SumList was an approach to uses less memory while still having less errors through
    floating point calculations when all the values are in the same order of magnitude.
    This approach needs more computational power both during the adding of values
    to the averaging object and for calculating the final result.
"""

from ._average.sortedsum import SortedSum
from ._average.sumdirectly import SumDirectly
from ._average.sumlist import SumList

