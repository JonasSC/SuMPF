# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2018 Jonas Schulte-Coerne
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
import sumpf


class GetItem(object):
    """
    A class for getting an item out of a container like a tuple, a list or a dict.
    It is basically a wrapper for the []-operator (__getitem__), so that this
    operation can be built into a signal processing chain.
    """
    def __init__(self, container=(None,), key=0):
        """
        @param container: the container, from which the item shall be retrieved
        @param key: the key or index, under which the desired item is stored in the container
        """
        self.__container = container
        self.__key = key

    @sumpf.Output(None)
    def GetItem(self):
        """
        Returns the selected item from the container.
        """
        return self.__container[self.__key]

    @sumpf.Input((collections.Sequence, collections.Mapping), "GetItem")
    def SetContainer(self, container):
        """
        Sets the container from which the item shall be retrieved.
        @param container: an object, that supports the []-operator
        """
        self.__container = container

    @sumpf.Input(None, "GetItem")
    def SetKey(self, key):
        """
        Sets the key or index by which the item shall be looked up in the container.
        @param key: the key or index, that is available in the given container
        """
        self.__key = key

