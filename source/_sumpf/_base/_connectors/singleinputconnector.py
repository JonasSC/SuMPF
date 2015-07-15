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

from .baseinputconnectors import TypedInputConnector


class SingleInputConnector(TypedInputConnector):
    """
    A Connector-class that replaces setter methods, so they can be used to connect different objects.
    """
    def __init__(self, instance, data_type, method, observers):
        """
        @param instance: The instance in which the method is replaced by this connector
        @param data_type: The type of the data that is passed through this connection. This can either be a single type or a tuple of valid types
        @param method: The method that is replaced by this connector
        @param observers: The names of output methods that are affected by calling this object
        """
        TypedInputConnector.__init__(self, instance, data_type, method, observers)
        self.__value_change_announced = False

    def __call__(self, *args, **kwargs):
        """
        By making the object callable, it mimics the replaced method.
        This method also notifies the output method that are affected by this call (observers).
        @param args, kwargs: parameters with which the replaced method has been called
        """
        self._Announce()
        result = self._method(self._instance, *args, **kwargs)
        self.__value_change_announced = False
        self._Report()
        return result

    def NoticeAnnouncement(self, connector):
        """
        This method is called by a connected output when it is about to change.
        It is used to estimate when the observing outputs shall be notified. So
        unnecessary computations in forked connection chains can be avoided.
        @param connector: not used here. Only for compatibility with other connector classes
        """
        self._progress_indicator.Announce(connector)
        if not self.__value_change_announced:
            self._Announce()
            self.__value_change_announced = True

    def NoticeValueChange(self, connector):
        """
        This method is called by a connected output when it has changed
        @param connector: The OutputConnector instance that has changed
        """
        value = connector()
        self._progress_indicator.Report(connector)
        self._method(self._instance, value)
        self.__value_change_announced = False
        self._Report()

    def CheckConnection(self, connector):
        """
        Checks if connecting to the given connector is possible. Raises an error if not.
        This method can be overridden in derived classes to implement more checks. In this case the
        overriding methods should call CheckConnection from its parent-class.
        @param connector: the connector to which the connection shall be checked
        """
        TypedInputConnector.CheckConnection(self, connector)
        # check if single input is already connected
        if self._connections != []:
            raise ValueError("A SingleInputConnector can only take one connection")

