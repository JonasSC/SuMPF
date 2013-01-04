# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2013 Jonas Schulte-Coerne
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
It is recommended to get an averaging instance by calling the factory() method.
Currently there are two implementations of an averaging algorithm available:
  SumAndDivide is the classical approach of summing up all the elements and then
    dividing by their number.
  AverageList was an approach that tried to use less memory while still having
    less errors through floating point calculations. This costs of course more
    computational power.
    Sadly AverageList is not yet fully functional and is less accurate than the
    SumAndDivide algorithm. So use this only, if a low memory is a lot more
    important than accuracy.
"""

from ._average.sumanddivide import SumAndDivide
from ._average.averagelist import AverageList

from ._average.factory import factory

