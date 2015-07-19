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

class ConnectorProxy(object):
    """
    This is a class for proxy objects of connectors. These are returned by the
    Connector decorators, while the methods are replaced by the actual connectors.
    The actual connector only has a weak reference to its instance, while this
    proxy has a hard reference, but mimics the connector in  almost everyother way.
    This makes constructions like
        value = Class().Connector()
    possible. Without the proxy, the instance of the class would be deleted before
    the connector method is called, so that the weak reference of the connector
    would be expired during its call.
    """
    def __init__(self, connector, instance):
        """
        @param connector: the Connector instance, that shall be represented by this proxy
        @param instance: the instance of which the connector replaces a method
        """
        self.__connector = connector
        self.__instance = instance
        self.__doc__ = self.__connector.__doc__

    def __call__(self, *args, **kwargs):
        """
        By making this callable, it mimics the Connector and therefore also the
        decorated method
        """
        return self.__connector(*args, **kwargs)

    def __getattr__(self, name):
        """
        Every attribute access, that is not specific to the ConnectorProxy class
        is deferred to the actual connector instance.
        """
        return getattr(self.__connector, name)

    def GetConnector(self):
        """
        returns the actual connector, that is represented by this proxy.
        @retval : a Connector instance
        """
        return self.__connector

