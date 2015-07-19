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
from ..decorators import Input, Output
from ..baseconnectors import Connector
from ..connectorproxy import ConnectorProxy


class ProgressIndicator(object):
    """
    Base class for progress indicators.
    These progress indicators can be used to track the progress of a calculation
    in a processing chain. It counts the number of involved methods and reports
    the progress each time one of these methods has finished running.

    Derived classes have to implement the _Filter method that is used to select
    which methods shall be taken into account for tracking the progress. This is
    useful, if for example all setter methods just set some state variables, while
    the getter methods do the expensive calculations. In this case the setter
    methods should be filtered out and the progress should be calculated from the
    finished getter methods, to have a better estimate of the processing progress.
    """
    def __init__(self, method=None, message=None):
        """
        @param method: a method that starts the calculation of which the progress shall be tracked. This method must have been decorated to become a Connector.
        @param message: the message that shall be passed by this ProgressIndicator, when none of the observed methods has finished yet
        """
        self.__announcements = set()
        self.__max_length = 0
        if method is not None:
            method.SetProgressIndicator(self)
        self.__message = message

    def AddMethod(self, method):
        """
        Adds a method that starts a calculation, whose progress shall be tracked
        by this ProgressIndicator.
        @param method: a method that starts the calculation of which the progress shall be tracked. This method must have been decorated to become a Connector.
        """
        method.SetProgressIndicator(self)

    def Destroy(self):
        """
        Destroys this ProgressIndicator instance, so it can be easily garbage
        collected.
        """
        sumpf.destroy_connectors(self)

    def _Filter(self, connector):
        """
        This method has to be implemented in derived classes.
        It shall return True, if the given connector shall be taken into account
        for calculating the progress and False otherwise.
        @param connector: the connector that shall be checked.
        @retval : True if the connector shall be counted, False otherwise.
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def Announce(self, connector):
        """
        This method is called from a Connector, when it announces that it's value
        will change during the current calculation. This way, the number of
        calculation steps is counted.
        @param connector: the connector whose value is about to change.
        """
        c = connector
        if isinstance(connector, ConnectorProxy):
            c = connector.GetConnector()
        if self._Filter(c):
            self.__announcements.add(c)
            self.__max_length = max(len(self.__announcements), self.__max_length)

    @Input(Connector, ["GetProgressAsTuple", "GetProgressAsFloat", "GetProgressAsPercentage"])
    def Report(self, connector):
        """
        This method is called form a Connector, when it has finished changing.
        Calling this method automatically informs objects, that are connected to
        the GetProgress... methods about the updated progress.
        @param connector: the connector whose value has just changed.
        """
        if self._Filter(connector):
            try:
                self.__announcements.remove(connector)
                if self.__message is not None:
                    self.__message = "%s has just finished" % connector.GetName()
            except KeyError:
                pass

    @Output(tuple)
    def GetProgressAsTuple(self):
        """
        Returns the progress as a tuple (max, finished, message).
        max is the number of methods that will run in total, while finished is the
        number of methods that have finished running. message is either None or
        a message that can be displayed in a progress dialog.
        @retval : a tuple (max, finished, message)
        """
        return self.__max_length, self.__max_length - len(self.__announcements), self.__message

    @Output(float)
    def GetProgressAsFloat(self):
        """
        Returns the progress as a floating point number between 0.0 and 1.0.
        0.0 means that the calculation is at the very beginning, while 1.0 says
        that the calculation has finished.
        @retval : the progress as a floating point number between 0.0 and 1.0.
        """
        if self.__max_length == 0:
            return 0.0
        else:
            return 1.0 - float(len(self.__announcements)) / float(self.__max_length)

    @Output(int)
    def GetProgressAsPercentage(self):
        """
        Returns the progress as an integer number between 0 and 100. This can
        be interpreted as the percentage, that says how much of the calculation
        has been done so far.
        @retval : the progress as an integer between 0 and 100, representing a percentage.
        """
        return int(round(100.0 * self.GetProgressAsFloat()))

