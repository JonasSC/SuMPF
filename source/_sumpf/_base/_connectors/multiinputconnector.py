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

from .baseinputconnectors import InputConnector, TypedInputConnector


class MultiInputConnectorBase(TypedInputConnector):
    """
    A base class for Input connectors that can handle connections from multiple
    output connectors. This could be the appropriate connector for add-methods.
    Requires an appropriate remove-method that reverts an add-method call.
    """
    def __init__(self, instance, data_type, method, remove_method, observers):
        """
        @param instance: the instance in which the method is replaced by this connector
        @param data_type: the type of the data that is passed through this connection. This can either be a single type or a tuple of valid types
        @param method: the method that is replaced by this connector
        @param remove_method: the name of the remove method
        @param observers: the names of output methods that are affected by calling this object
        """
        TypedInputConnector.__init__(self, instance, data_type, method, observers)
        method_remove = getattr(instance, remove_method)
        if isinstance(method_remove, MultiInputConnectorAssociate):
            self._remove_method = method_remove
        else:
            self._remove_method = MultiInputConnectorAssociate(instance=instance, method=method_remove, observers=observers)
            setattr(instance, remove_method, self._remove_method)
        self.__connections = {}
        self.__announcements = set()
        self.__self_announcements = 0

    def __call__(self, *args, **kwargs):
        """
        By making the object callable, it mimics the replaced method.
        This method also notifies the output method that are affected by this
        call (observers).
        @param value: the value with which the replaced method has been called
        @retval : the id returned by the replaced method
        """
        self._Announce()
        result = self._method(self._instance, *args, **kwargs)
        if self.__self_announcements == 0:
            self._Report()
        else:
            self.__self_announcements -= 1
        return result

    def NoticeAnnouncement(self, connector):
        """
        This method is called by a connected output when it is about to change.
        It is used to estimate when the observing outputs shall be notified. So
        unnecessary computations in forked connection chains can be avoided.
        @param connector: the connected output connector
        """
        if connector is self:
            self.__self_announcements += 1
        elif connector not in self.__announcements:
            self._progress_indicator.Announce(connector)
            self.__announcements.add(connector)
            TypedInputConnector._Announce(self)

    def NoticeValueChange(self, connector):
        """
        This method is called by a connected output when it has changed.
        @param connector: The OutputConnector instance that has changed
        """
        value = connector()
        self._progress_indicator.Report(connector)
        if self.__connections[connector] is not None:
            self.__connections[connector] = self._ReplaceData(data_id=self.__connections[connector], data=value)
        else:
            self.__connections[connector] = self._method(self._instance, value)
        self.__announcements.discard(connector)
        if self.__announcements == set() and self.__self_announcements == 0:
            self._Report()

    def Connect(self, connector):
        """
        Please do not use this method as it might be changed in future versions.
        Use the connect function instead.
        @param connector: the connector whose output shall be added to this connectror's input
        """
        TypedInputConnector.Connect(self, connector)
        self.__connections[connector] = None

    def Disconnect(self, connector):
        """
        Please do not use this method as it might be changed in future versions.
        Use the disconnect function instead.
        @param connector: the connector whose output shall be removed from this connectror's input
        """
        self._Announce()
        if self.__connections[connector] is not None:
            self._remove_method.CallMethod(self.__connections[connector])
            del self.__connections[connector]
        TypedInputConnector.Disconnect(self, connector)
        self._Report()

    def GetNumberOfExpectedInputs(self):
        """
        Returns the number of input connections that are about to change.
        This can be used to estimate if an error should be raised because of
        incompatible data.
        @retval : the integer number of inputs that will change
        """
        return len(self.__announcements)

    def _ReplaceData(self, data_id, data):
        """
        This method shall be overridden with an algorithm for replacing the data
        from a connected output, whose value has changed.
        @param data_id: the id under which the old data from the connector is stored
        @param data: the new data
        @retval : the data id under which the new data is stored
        """
        raise NotImplementedError("This method should have been overridden in a derived class")



class NonReplacingMultiInputConnector(MultiInputConnectorBase):
    """
    A class for Input connectors that can handle connections from multiple output
    connectors. This could be the appropriate connector for add-methods.
    Requires an appropriate remove-method that reverts an add-method call.
    When the value of a connected output changes, this connector will call the
    remove-method to remove the old data, and then the add-method, which was
    replaced by this connector, to add the new data.
    """
    def _ReplaceData(self, data_id, data):
        """
        This method replaces the data from a connected output, whose value has changed.
        @param data_id: the id under which the old data from the connector is stored
        @param data: the new data
        @retval : the data id under which the new data is stored
        """
        self._remove_method.CallMethod(data_id)
        return self._method(self._instance, data)



class ReplacingMultiInputConnector(MultiInputConnectorBase):
    """
    A class for Input connectors that can handle connections from multiple output
    connectors. This could be the appropriate connector for add-methods.
    Requires an appropriate remove-method that reverts an add-method call and a
    replace-method that replaces existing data.
    When the value of a connected output changes, this connector will call the
    replace-method to update the data.
    """
    def __init__(self, instance, data_type, method, remove_method, replace_method, observers):
        """
        @param instance: the instance in which the method is replaced by this connector
        @param data_type: the type of the data that is passed through this connection. This can either be a single type or a tuple of valid types
        @param method: the method that is replaced by this connector
        @param remove_method: the name of the remove method
        @param replace_method: the name of the replace method
        @param observers: the names of output methods that are affected by calling this object
        """
        MultiInputConnectorBase.__init__(self, instance=instance, data_type=data_type, method=method, remove_method=remove_method, observers=observers)
        method_replace = getattr(instance, replace_method)
        if isinstance(method_replace, MultiInputConnectorAssociate):
            self.__replace_method = method_replace
        else:
            self.__replace_method = MultiInputConnectorAssociate(instance=instance, method=method_replace, observers=observers)
            setattr(instance, replace_method, self.__replace_method)

    def _ReplaceData(self, data_id, data):
        """
        This method replaces the data from a connected output, whose value has changed.
        @param data_id: the id under which the old data from the connector is stored
        @param data: the new data
        @retval : the data id under which the new data is stored (in this case the given data_id)
        """
        self.__replace_method.CallMethod(data_id, data)
        return data_id



class MultiInputConnectorAssociate(InputConnector):
    """
    A class for remove or replace methods that are needed by MultiInputConnectors.
    These methods will be replaced by an instance of this class.
    This class basically does the same thing as the replaced method, but it also
    notifies the OutputConnectors which are observing the MultiInputConnector to
    keep the data synchronized.
    Connecting to an instance of this class is not possible.
    """
    def __call__(self, *args, **kwargs):
        """
        @param data_id: the id of the data that shall be handled by the remove or replace method
        @retval : the return value of the remove method
        """
        self._AnnounceToObservers()
        result = self.CallMethod(*args, **kwargs)
        self._ReportToObservers()
        return result

    def CallMethod(self, *args, **kwargs):
        """
        Calls the remove or replace method without notifying any other connectors
        in the processing chain. This method is meant to be called by MultiInputConnector
        instances, when those instances handle the notification in the processing
        chain.
        @param data_id: the id of the data that shall be handled by the remove method
        @retval : the return value of the remove method
        """
        return self._method(*args, **kwargs)

    def Connect(self, connector):
        """
        Inhibits connections to instances of MultiInputConnectorAssociate by raising an error.
        @param connector: is not used
        """
        raise RuntimeError("Connecting to a remove or replace method is not possible")

