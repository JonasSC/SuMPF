# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012 Jonas Schulte-Coerne
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


class MultiInputConnector(TypedInputConnector):
	"""
	A Connector-class that replaces add-methods, so they can be used to connect different objects.
	Requires an appropriate remove-method that reverts an add-method call.
	"""
	def __init__(self, instance, data_type, method, remove_method, observers):
		"""
		@param instance: The instance in which the method is replaced by this connector
		@param data_type: The type of the data that is passed through this connection. This can either be a single type or a tuple of valid types
		@param method: The method that is replaced by this connector
		@param remove_method: The name of the remove method
		@param observers: The names of output methods that are affected by calling this object
		"""
		TypedInputConnector.__init__(self, instance, data_type, method, observers)
		self.__remove_method = RemoveMethod(instance, getattr(instance, remove_method), observers)
		setattr(instance, remove_method, self.__remove_method)
		self.__connection_ids = []
		self.__connections_without_id = []
		self.__announcements = set()

	def __call__(self, *args, **kwargs):
		"""
		By making the object callable, it mimics the replaced method.
		This method also notifies the output method that are affected by this call (observers).
		@param value: the value with which the replaced method has been called
		@retval : the id returned by the replaced method
		"""
		self._Announce()
		result = self._method(self._instance, *args, **kwargs)
		self._Report()
		return result

	def NoticeAnnouncement(self, connector):
		"""
		This method is called by a connected output when it is about to change.
		It is used to estimate when the observing outputs shall be notified. So
		unnecessary computations in forked connection chains can be avoided.
		@param connector: the connected output connector
		"""
		if connector not in self.__announcements:
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
		self.__UpdateId(connector, new_id=None)
		self.__connections_without_id.append(connector)
		new_id = self._method(self._instance, value)
		self.__UpdateId(connector, new_id)
		self.__announcements.discard(connector)
		if self.__announcements == set():
			self._Report()

	def Connect(self, connector):
		"""
		Please do not use this method as it might be changed in future versions.
		Use the connect function instead.
		@param connector: the connector whose output shall be added to this connectror's input
		"""
		TypedInputConnector.Connect(self, connector)
		self.__connection_ids.append(None)
		self.__connections_without_id.append(connector)

	def Disconnect(self, connector):
		"""
		Please do not use this method as it might be changed in future versions.
		Use the disconnect function instead.
		@param connector: the connector whose output shall be removed from this connectror's input
		"""
		self.__UpdateId(connector, new_id=None)
		self.__connection_ids.pop(self._connections.index(connector))
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

	def __UpdateId(self, connector, new_id):
		"""
		Updates the id for the given connector and removes the data stored under
		the old id.
		@param connector: the OutputConnector whose id shall be updated
		@param new_id: the id under which the updated data can be accessed
		"""
		if connector not in self.__connections_without_id:
			remove_id = self.__connection_ids[self._connections.index(connector)]
			self.__remove_method.CallMethod(remove_id)
		else:
			self.__connections_without_id.remove(connector)
		self.__connection_ids[self._connections.index(connector)] = new_id



class RemoveMethod(InputConnector):
	"""
	A class for remove methods needed by MultiInputConnectors.
	These methods will be replaced by an instance of this class.
	This class basically does the same thing as the remove method, but it also
	notifies the OutputConnectors which are observing the MultiInputConnector to
	keep the data synchronized.
	Connecting to an instance of this class is not possible.
	"""
	def __call__(self, *args, **kwargs):
		"""
		@param data_id: the id of the data that shall be handled by the remove method
		@retval : the return value of the remove method
		"""
		self._AnnounceToObservers()
		result = self.CallMethod(*args, **kwargs)
		self._ReportToObservers()
		return result

	def CallMethod(self, *args, **kwargs):
		"""
		Calls the remove method without notifying any other connectors in the
		processing chain. This method is meant to be called by MultiInputConnector
		instances, when those instances handle the notification in the processing
		chain.
		@param data_id: the id of the data that shall be handled by the remove method
		@retval : the return value of the remove method
		"""
		return self._method(*args, **kwargs)

	def Connect(self, connector):
		"""
		Inhibits connections to instances of RemoveMethod by raising an error.
		@param connector: is not used
		"""
		raise RuntimeError("Connecting to a remove method is not possible")

