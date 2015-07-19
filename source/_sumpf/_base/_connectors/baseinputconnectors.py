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
from . import outputconnectors
from .connectorproxy import ConnectorProxy
from ._progressindicators.progressindicator_nop import nop_progress_indicator


class InputConnector(Connector):
    """
    An abstract Connector-class that replaces input methods, so they can be used
    to connect different objects.
    """
    def __init__(self, instance, method, observers):
        """
        @param instance: The instance in which the method is replaced by this connector
        @param method: The method that is replaced by this connector
        @param observers: The names of output methods that are affected by calling this object
        """
        Connector.__init__(self, instance, method)
        self.__observers = []
        for o in observers:
            method = getattr(self._instance, o)
            if isinstance(method, ConnectorProxy):
                self.__observers.append(method.GetConnector())
            else:
                self.__observers.append(method)
        self._progress_indicator = nop_progress_indicator

    def _Announce(self):
        """
        Protected method that announces to both the observing outputs and the
        progress indicator, that this input is about to receive new data.
        """
        self._progress_indicator.Announce(self)
        self._AnnounceToObservers()

    def _AnnounceToObservers(self):
        """
        Protected method that announces only to the observing outputs, that this
        input is about to receive new data. The progress indicator is not notified.
        """
        for o in self.__observers:
            o.NoticeAnnouncement(self)

    def _Report(self):
        """
        Protected method that reports to both the observing outputs and the
        progress indicator, that this input has received new data and that the
        outputs need to recalculate their value.
        """
        self._progress_indicator.Report(self)
        self._progress_indicator = nop_progress_indicator
        self._ReportToObservers()

    def _ReportToObservers(self):
        """
        Protected method that reports only to the observing outputs, that this
        input has received new data and that the outputs need to recalculate their
        value. The progress indicator is not notified.
        """
        for o in self.__observers:
            o.NoticeValueChange(self)

    def CheckConnection(self, connector):
        """
        Checks if connecting to the given connector is possible. Raises an error if not.
        This method can be overridden in derived classes to implement more checks. In this case the
        overriding methods should call CheckConnection from its parent-class.
        @param connector: the connector to which the connection shall be checked
        """
        Connector.CheckConnection(self, connector)
        # check for infinite loops
        # Checks if this object has the given OutputConnector as an observer. A connection between
        # this and the OutputConnector would result in an infinite loop.
        # Please note that inifinite loops through multiple connections can not be detected (yet).
        for o in self.__observers:
            if connector is o:
                raise ValueError("The output would be connected to an input that triggers the output again. An infinite loop would result from that")
        # check if connector is an output
        if not isinstance(connector, outputconnectors.OutputConnector):
            raise TypeError("Connecting an input to a " + type(connector).__name__ + " is not possible, expecting an OutputConnector instance")

    def GetObservers(self):
        """
        This method returns the list of names of getter methods of the instance,
        that are affected, when this connector's setter method is called.
        @retval : a list of string method names
        """
        return self.__observers

    def SetProgressIndicator(self, indicator):
        """
        Sets a progress indicator, with which it is possible to track the
        progress of the calculation in the processing chain.
        The set progress indicator will be automatically replaced with a indicator
        that does nothing, after the calculation has finished.
        @param indicator: a ProgressIndicator instance
        """
        self._progress_indicator = indicator

    def GetProgressIndicator(self):
        """
        Returns the current progress indicator that is used to track the progress
        of the calculation in the processing chain.
        @retval : a ProgressIndicator instance
        """
        return self._progress_indicator



class TypedInputConnector(InputConnector, TypedConnector):
    """
    A base class for InputConnectors that can only be connected to outputs with
    the same type.
    """
    def __init__(self, instance, data_type, method, observers):
        """
        @param instance: The instance in which the method is replaced by this connector
        @param data_type: The type of the data that is passed through this connection. This can also be a tuple of valid types
        @param method: The method that is replaced by this connector
        @param observers: The names of output methods that are affected by calling this object
        """
        InputConnector.__init__(self, instance, method, observers)
        TypedConnector.__init__(self, data_type)

    def CheckConnection(self, connector):
        """
        Checks if connecting to the given connector is possible. Raises an error
        if not.
        This method can be overridden in derived classes to implement more checks.
        In this case the overriding methods should call CheckConnection from its
        parent class.
        @param connector: the connector to which the connection shall be checked
        """
        InputConnector.CheckConnection(self, connector)
        # Check for incompatible data types
        if isinstance(self.GetType(), tuple):
            if connector.GetType() not in self.GetType():
                raise TypeError("The input expects a different data type than the output delivers")
        else:
            if not issubclass(connector.GetType(), self.GetType()):
                raise TypeError("The input expects a different data type than the output delivers")

