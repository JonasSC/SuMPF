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

import weakref
from .connectorproxy import ConnectorProxy


class ConnectorDecorator(object):
    """
    An abstract base class for the decoration of methods so they can be used as Connectors.
    To understand how this decorator works, consider this example:

        class ExampleClass(object):
            @decorator(argument)
            def method(self):
                pass

        is equivalent to:

        def method(self):
            pass

        class ExampleClass(object):
            method = decorator(argument)(method)
        #                        |          |
        #                    __init__    __call__

    When the decorated method is called the first time, the __get__ method is called. This method
    initializes a Connector-object that behaves exactly like the decorated method and adds the
    connection functionality. The decorated method is replaced by this object and the object is
    returned.
    After the replacement the connector-object is called directly without the decorator-detour.
    """
    def __init__(self):
        self._method = None     # Will be set in __call__

    def __call__(self, method):
        self._method = method
        return self

    def __get__(self, instance, instance_type):
        """
        Makes this class a non-data descriptor for the decorated method.
        Initializes the Connector-object and replaces the decorated method with it.
        @param instance: the instance of which a method shall be replaced
        @param instance_type: the type of the instance
        """
        connector = self._GetConnector(weakref.proxy(instance))
        setattr(instance, self._method.__name__, connector)
        return ConnectorProxy(connector=connector, instance=instance)

    def _GetConnector(self, instance):
        """
        An abstract method in which the derived classes can initialize the correct Connector-object.
        """
        raise NotImplementedError("This method should have been overridden in a derived class")



class TypedDecorator(object):
    """
    An addition to a ConnectorDecorator for Connectors that are aware of the data type that is
    passed through them.
    """
    def __init__(self, data_type):
        """
        @param data_type: the type of the data that is passed through this connection
        """
        self._data_type = data_type

    def GetType(self):
        """
        This method returns the type of the Connector-method that is decorated
        with this decorator.
        With this, the type of a Connector can be determined from a class and not only
        from an instance of that class.
        The decoration of methods still behaves a bit odd. When having a class,
        the determination of one of their method's type does not work the intuitive
        way:
            CLASS.METHOD.GetType()
        This will raise an error that None does not have the attribute METHOD.
        Instead, the following workaround has to be used:
            vars(CLASS)["METHOD"].GetType()
        @retval : the type of the data that is passed through this connection
        """
        return self._data_type



class ObservedDecorator(object):
    """
    An addition to a ConnectorDecorator for InputConnectors that notify their instances'
    OutputConnectors when an incoming value changes their outputs
    """
    def __init__(self, observers):
        """
        @param observers: the names of output methods that are affected by calling this setter
        """
        if isinstance(observers, str):
            self._observers = [observers]
        else:
            self._observers = observers

