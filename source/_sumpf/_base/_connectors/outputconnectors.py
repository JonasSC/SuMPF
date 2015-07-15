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

from .baseconnectors import Connector, TypedConnector
#from . import baseinputconnectors  # doesn't work here because of circular imports. The import is now in OutputConnector.CheckConnection


class OutputConnector(Connector, TypedConnector):
    """
    A Connector-class that replaces getter methods, so they can be used to connect
    different objects.
    """
    def __init__(self, instance, data_type, method):
        """
        @param instance: The instance in which the method is replaced by this connector
        @param data_type: The type of the data that is passed through this connection
        @param method: The method that is replaced by this connector
        """
        Connector.__init__(self, instance, method)
        TypedConnector.__init__(self, data_type)
        self.__value_has_changed = False
        self.__is_deactivated = False
        self.__announcements = set()

    def NoticeAnnouncement(self, connector):
        """
        This method is called by the InputConnectors, which are observed by this
        output, when they are about to change.
        It is used to estimate when the connected inputs shall be notified. So
        unnecessary computations in forked connection chains can be avoided.
        @param connector: the observed input connector
        """
        for c in self._connections:
            c.SetProgressIndicator(connector.GetProgressIndicator())    # propagate progress indicator
            # The announcement of a value change of this connector will be
            # done in the connected input connectors. This way, an output
            # that is not connected to any input will not contribute to the
            # progress estimation.
            c.NoticeAnnouncement(self)
        self.__announcements.add(connector)

    def NoticeValueChange(self, connector):
        """
        This method can be called if the data that can be got through this connector
        has changed.
        @param connector: the observed input connector whose value has just changed
        """
        if connector in self.__announcements:
            self.__announcements.discard(connector)
        if self.__announcements == set():
            if self.__is_deactivated:
                self.__value_has_changed = True
            else:
                for c in self._connections:
                    c.NoticeValueChange(self)

    def CheckConnection(self, connector):
        """
        Checks if connecting to the given connector is possible. Raises an error if not.
        This method can be overridden in derived classes to implement more checks. In this case the
        overriding methods should call CheckConnection from its parent-class.
        @param connector: the connector to which the connection shall be checked
        """
        from . import baseinputconnectors
        Connector.CheckConnection(self, connector)
        # check if connector is an input
        if not isinstance(connector, baseinputconnectors.InputConnector):
            raise TypeError("Connecting an output to a " + type(connector).__name__ + " is not possible, expecting an InputConnector instance")

    def Deactivate(self):
        """
        Deactivates the output. This means that connected inputs will not be
        notified on changes.
        OutputConnectors are active by default.
        """
        self.__is_deactivated = True

    def Activate(self):
        """
        Reactivates the output. This means that connected inputs will be notified
        on changes again.
        OutputConnectors are active by default.
        """
        self.__is_deactivated = False
        if self.__value_has_changed:
            self.__announcements = set()
            for c in self._connections:
                c.NoticeAnnouncement(self)
            for c in self._connections:
                c.NoticeValueChange(self)
            self.__value_has_changed = False

    def IsActive(self):
        """
        Returns if the output is activated or deactivated.
        @retval : True if output is active, False if deactivated
        """
        return not self.__is_deactivated

    def ExpectsInputFrom(self, connector):
        """
        Returns if the output expects a data change from the given input.
        This can be used to estimate if it is necessary to raise an error
        because of incompatible data.
        @param connector: the InputConnector that shall be checked
        """
        return connector in self.__announcements



class NotCachingOutputConnector(OutputConnector):
    """
    An OutputConnector that does not cache its return value. The value will be
    recalculated each time the method is called
    """
    def __call__(self, *args, **kwargs):
        """
        By making the object callable, it mimics the replaced method.
        """
        return self._method(self._instance, *args, **kwargs)



class CachingOutputConnector(OutputConnector):
    """
    An OutputConnector that caches its return value. The value will be recalculated
    only if one of the observed setter methods has been called.
    """
    def __init__(self, instance, data_type, method):
        """
        @param instance: The instance in which the method is replaced by this connector
        @param data_type: The type of the data that is passed through this connection
        @param method: The method that is replaced by this connector
        """
        OutputConnector.__init__(self, instance, data_type, method)
        self.__cached_value = None
        self.__cache_is_valid = False

    def __call__(self, *args, **kwargs):
        """
        By making the object callable, it mimics the replaced method.
        """
        if not self.__cache_is_valid:
            self.__cached_value = self._method(self._instance, *args, **kwargs)
            self.__cache_is_valid = True
        return self.__cached_value

    def NoticeValueChange(self, connector):
        """
        This method can be called if the data that can be got through this connector has changed.
        It also triggers the recalculation of the cached value
        @param connector: the input connector through which changed data has been entered
        """
        self.__cache_is_valid = False
        OutputConnector.NoticeValueChange(self, connector)

