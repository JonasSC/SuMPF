# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2013 Jonas Schulte-Coerne
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

from .baseconnectors import Connector
from .baseinputconnectors import InputConnector
from .outputconnectors import OutputConnector
from .triggerinputconnector import TriggerInputConnector

def connect(a, b):
	"""
	Connects two methods that have been decorated with either Input or Output.
	@param a, b: Should be one Input and one Output. The order is not important
	"""
	a.Connect(b)
	try:
		b.Connect(a)
	except BaseException as e:
		a.Disconnect(b)			# if connection fails, go back to a legal state
		raise e
	input = a
	output = b
	if not isinstance(input, InputConnector):
		input = b
		output = a
	if not isinstance(input, TriggerInputConnector):
		if output.IsActive():
			input.NoticeValueChange(output)

def disconnect(a, b):
	"""
	Disconnects two methods that have been decorated with either Input or Output.
	@param a, b: Should be one Input and one Output. The order is not important
	"""
	a.Disconnect(b)
	b.Disconnect(a)

def disconnect_all(obj):
	"""
	disconnects everything from the given object. The object can be either a
	Connector instance or of any other type that has Connectors as attributes.
	@param obj: the object from which everything shall be disconnected
	"""
	if isinstance(obj, Connector):
		obj.DisconnectAll()
	else:
		for a in list(vars(obj).values()):
			if isinstance(a, Connector):
				a.DisconnectAll()

def deactivate_output(obj):
	"""
	Deactivates the notification of inputs that are connected to an instance's
	outputs.
	@param obj: An instance with output connectors or an output connector
	"""
	if isinstance(obj, OutputConnector):
		obj.Deactivate()
	else:
		for a in list(vars(obj).values()):
			if isinstance(a, OutputConnector):
				a.Deactivate()

def activate_output(obj):
	"""
	(Re)Activates the notification of inputs that are connected to an instance's
	outputs.
	@param obj: An instance with output connectors or an output connector
	"""
	if isinstance(obj, OutputConnector):
		obj.Activate()
	else:
		for a in list(vars(obj).values()):
			if isinstance(a, OutputConnector):
				a.Activate()

def destroy_connectors(obj):
	"""
	Destroys all connectors of an object, so the garbage collector has no
	problems deleting the object.
	@param obj: An instance with connectors
	"""
	disconnect_all(obj)
	attributes = vars(obj)
	for a in attributes:
		if isinstance(attributes[a], Connector):
			setattr(obj, a, None)

