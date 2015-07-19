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

import sumpf


class Connector(object):
    """
    Base class for connectors.
    In SuMPF Connectors are objects that replace methods of a class so that they
    can be connected to each other. This way changing data at one end of a
    connection chain will automatically cause the data at the other end of the
    chain to be updated.
    """
    def __init__(self, instance, method):
        self.__doc__ = method.__doc__       # This way the docstring of the decorated method remains the same
        self._instance = instance
        self._method = method
        self._connections = []

    def __call__(self, *args, **kwargs):
        """
        By making the object callable, it mimics the replaced method.
        This is a virtual method which shall be overridden so it calls the
        replaced method in the expected manner.
        @param *args, **kwargs: possible arguments of the replaced method
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def NoticeAnnouncement(self, connector):
        """
        This method is to notify other Connectors in a processing chain, when a
        value is about to change. This way unnecessary computations in forked
        connection chains can be avoided, by waiting with the recalculation of
        a value until all announced value changes have been done before recalculating
        a value that depends on these value changes.
        @param connector: a connector on whose value change this connector's value depends
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def NoticeValueChange(self, connector):
        """
        This method is to notify other Connectors in a processing chain, when a
        value has just changed. This means that the decorated method has to be
        run again.
        @param connector: a connector on whose value change this connector's value depends
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def Connect(self, connector):
        """
        Please do not use this method as it might be changed in future versions.
        Use the connect function instead.
        @param connector: the connector to which this connector shall be connected
        """
        self.CheckConnection(connector)
        self._connections.append(connector)

    def Disconnect(self, connector):
        """
        Please do not use this method as it might be changed in future versions.
        Use the disconnect function instead.
        @param connector: the connector from which this connector shall be disconnected
        """
        self._connections.remove(connector)

    def DisconnectAll(self):
        """
        Please do not use this method as it might be changed in future versions.
        Use the disconnect_all function instead.
        """
        while len(self._connections) > 0:
            sumpf.disconnect(self, self._connections[0])

    def CheckConnection(self, connector):
        """
        Checks if connecting to the given connector is possible. Raises an error
        if not.
        This method can be overridden in derived classes to implement more checks.
        In this case the overriding methods should call CheckConnection from its
        parent-class.
        @param connector: the connector to which the connection shall be checked
        """
        # check if connection already exists
        if connector in self._connections:
            raise ValueError("The connection already exists")

    def GetName(self):
        """
        Returns a short string that roughly describes the method that has been
        replaced by this connector.
        The string has the form CLASSNAME.METHODNAME, where CLASSNAME is the name
        of the class in which the method is declared and METHODNAME is the name
        of the decorated method.
        @retval : a string CLASSNAME.METHODNAME
        """
        return ".".join((self._instance.__class__.__name__, self._method.__name__))



class TypedConnector(object):
    """
    A mixin for connectors that can only be connected to connectors with the same type.
    The type of these connectors can be given as an argument to the respective
    decorator.
    The type can be queried with the GetType method.
    """
    def __init__(self, data_type):
        """
        @param data_type: the type of the data which is passed through this connector
        """
        self.__data_type = data_type

    def GetType(self):
        """
        Returns the type of the data which is passed through this connector
        @retval : the type of this connector's data
        """
        return self.__data_type

