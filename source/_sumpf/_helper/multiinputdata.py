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

class MultiInputData(object):
    """
    A container for data that is managed with a MultiInputConnector.
    It manages the handling of the ids and the order of the added data sets.
    The data can be obtained as a list.
    """
    def __init__(self):
        self.__ids = []
        self.__data = []

    def Add(self, data):
        """
        Adds a data set to the container.
        @param data: the data set that shall be added
        @retval : the id under which the data is stored
        """
        data_id = 0
        while data_id in self.__ids:
            data_id += 1
        self.__ids.append(data_id)
        self.__data.append(data)
        return data_id

    def Remove(self, data_id):
        """
        Removes a data set from the container.
        @param data_id: the id of the data which shall be removed
        """
        index = self.__ids.index(data_id)
        del self.__ids[index]
        del self.__data[index]

    def Replace(self, data_id, data):
        """
        Replaces a data set in the container.
        This is different to removing a data set and then adding the new data, as
        a replacing the data will put the new data at the same position as the old
        data, while removing and adding will put the new data at the end of the
        data list.
        @param data_id: the id of the data that shall be replaced
        @param data: the new data
        """
        index = self.__ids.index(data_id)
        self.__data[index] = data

    def GetData(self):
        """
        Returns the data in the container as a list.
        @retval : a list of data sets from the container
        """
        return self.__data

    def Clear(self):
        """
        Removes all input data from the container.
        """
        self.__ids = []
        self.__data = []

