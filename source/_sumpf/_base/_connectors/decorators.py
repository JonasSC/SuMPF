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
from .basedecorators import ConnectorDecorator, TypedDecorator, ObservedDecorator
from .singleinputconnector import SingleInputConnector
from .triggerinputconnector import TriggerInputConnector
from .multiinputconnector import NonReplacingMultiInputConnector, ReplacingMultiInputConnector
from .outputconnectors import CachingOutputConnector, NotCachingOutputConnector


class Input(ConnectorDecorator, TypedDecorator, ObservedDecorator):
    """
    A decorator that marks a method as an input for single connections.
    These connections can be used to automatically update a processing chain
    when a value has changed.
    The decorated method must take exactly one argument.
    """
    def __init__(self, data_type, observers=[]):
        """
        @param data_type: the type of the data that is passed through this connection
        @param observers: the names of output methods that are affected by calling this setter
        """
        ConnectorDecorator.__init__(self)
        TypedDecorator.__init__(self, data_type=data_type)
        ObservedDecorator.__init__(self, observers=observers)

    def _GetConnector(self, instance):
        return SingleInputConnector(instance=instance,
                                    data_type=self._data_type,
                                    method=self._method,
                                    observers=self._observers)



class Trigger(ConnectorDecorator, ObservedDecorator):
    """
    A decorator that marks a method as a trigger input.
    The decorated method must be callable without arguments.
    Triggers are triggered by a value change in a connected Output. They are
    however not triggered by creating this connection.
    """
    def __init__(self, observers=[]):
        """
        @param observers: the names of output methods that are affected by calling this setter
        """
        ConnectorDecorator.__init__(self)
        ObservedDecorator.__init__(self, observers=observers)

    def _GetConnector(self, instance):
        return TriggerInputConnector(instance=instance,
                                     method=self._method,
                                     observers=self._observers)



class MultiInput(ConnectorDecorator, TypedDecorator, ObservedDecorator):
    """
    A decorator that marks a method as an input for multiple connections.
    These connections can be used to automatically update a processing chain
    when a value has changed.
    The decorated method must take exactly one argument and return a unique id.
    For every MultiInput-method a remove-method has to be provided. This method
    has to take the id, which has been returned by the decorated method and remove
    the data, that has been added by the method call which has produced that id.
    A replace-method can be provided optionally. This method is called, when the
    value of a connected output has changed, rather than removing the old data and
    adding the new. A replace-method has to take the id under which the old data
    is stored as first parameter and the new data as second parameter. It must
    store the new data under the same id as the old data.
    """
    def __init__(self, data_type, remove_method, observers=[], replace_method=None):
        """
        @param data_type: the type of the data that is passed through this connection
        @param remove_method: the name of the remove method
        @param observers: the names of output methods that are affected by calling this setter
        @param replace_method: an optional name of a method that will be used, to replace data, when the value of a connected output has changed
        """
        ConnectorDecorator.__init__(self)
        TypedDecorator.__init__(self, data_type=data_type)
        ObservedDecorator.__init__(self, observers=observers)
        self.__remove_method = remove_method
        self.__replace_method = replace_method

    def _GetConnector(self, instance):
        if self.__replace_method is not None:
            return ReplacingMultiInputConnector(instance=instance,
                                                data_type=self._data_type,
                                                method=self._method,
                                                remove_method=self.__remove_method,
                                                replace_method=self.__replace_method,
                                                observers=self._observers)
        else:
            return NonReplacingMultiInputConnector(instance=instance,
                                                   data_type=self._data_type,
                                                   method=self._method,
                                                   remove_method=self.__remove_method,
                                                   observers=self._observers)



class Output(ConnectorDecorator, TypedDecorator):
    """
    A decorator that marks a method as an output connector.
    These connections can be used to automatically update a processing chain
    when a value has changed.
    The decorated method must not take any arguments.
    This decorator can also enable caching, in which case the return value is only recalculated when
    the respective setter methods have been called.
    Please note that caching might lead to wrong return values if not all setter methods notify the
    output properly. It is also problematic if the getter changes the state of its object.
    """
    def __init__(self, data_type, caching=None):
        """
        @param data_type: the type of the data that is passed through this connection
        @param caching: if True caching will be enabled, if false caching will be disabled, if None the use of caching will depend on the config
        """
        ConnectorDecorator.__init__(self)
        TypedDecorator.__init__(self, data_type=data_type)
        self.__caching = caching

    def _GetConnector(self, instance):
        if self.__caching or \
           self.__caching is None and sumpf.config.get("caching"):
            return CachingOutputConnector(instance=instance,
                                          data_type=self._data_type,
                                          method=self._method)
        else:
            return NotCachingOutputConnector(instance=instance,
                                             data_type=self._data_type,
                                             method=self._method)

