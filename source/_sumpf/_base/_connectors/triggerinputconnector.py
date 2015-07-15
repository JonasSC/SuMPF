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

from .baseinputconnectors import InputConnector


class TriggerInputConnector(InputConnector):
    """
    A Connector-class that replaces setter methods which take no arguments, so they can be used to
    connect different objects.
    """
    def __init__(self, instance, method, observers):
        """
        @param instance: The instance in which the method is replaced by this connector
        @param method: The method that is replaced by this connector
        @param observers: The names of output methods that are affected by calling this object
        """
        InputConnector.__init__(self, instance, method, observers)
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
        if not self.__value_change_announced:
            self._Announce()
            self.__value_change_announced = True

    def NoticeValueChange(self, connector):
        """
        This method is called by a connected output when it has changed
        @param connector: The OutputConnector instance that has changed
        """
        self._method(self._instance)
        self.__value_change_announced = False
        self._Report()

