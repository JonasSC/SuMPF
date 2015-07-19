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

from .baseconnectors import Connector
from .baseinputconnectors import InputConnector
from .outputconnectors import OutputConnector
from .triggerinputconnector import TriggerInputConnector
from .connectorproxy import ConnectorProxy

def connect(a, b):
    """
    Connects two methods that have been decorated with either Input or Output.
    @param a, b: Should be one Input and one Output. The order is not important
    """
    inp = a
    if isinstance(a, ConnectorProxy):
        inp = a.GetConnector()
    outp = b
    if isinstance(b, ConnectorProxy):
        outp = b.GetConnector()
    if not isinstance(inp, InputConnector):
        inp, outp = outp, inp
    inp.Connect(outp)
    try:
        outp.Connect(inp)
    except BaseException as e:
        inp.Disconnect(outp)         # if connection fails, go back to a legal state
        raise e
    if not isinstance(inp, TriggerInputConnector):
        if outp.IsActive():
            inp.NoticeAnnouncement(outp)
            inp.NoticeValueChange(outp)

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
    if isinstance(obj, (Connector, ConnectorProxy)):
        obj.DisconnectAll()
    else:
        for a in list(vars(obj).values()):
            if isinstance(a, (Connector, ConnectorProxy)):
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
            c = a
            if isinstance(a, ConnectorProxy):
                c = a.GetConnector()
            if isinstance(c, OutputConnector):
                c.Deactivate()

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
            c = a
            if isinstance(a, ConnectorProxy):
                c = a.GetConnector()
            if isinstance(c, OutputConnector):
                c.Activate()

def destroy_connectors(obj):
    """
    Destroys all connectors of an object, so the garbage collector has no
    problems deleting the object.
    @param obj: An instance with connectors
    """
    disconnect_all(obj)
    attributes = vars(obj)
    for a in attributes:
        if isinstance(attributes[a], (Connector, ConnectorProxy)):
            setattr(obj, a, None)

def set_multiple_values(pairs, progress_indicator=None):
    """
    Calls multiple setter methods with the respective input parameter.
    This is useful when changing multiple values in a processing chain of objects
    that are connected through SuMPF's connectors. If the values were set by calling
    the setter methods individually, each call would trigger a recalculation in
    the processing chain. By combining the calls of the setter methods with this
    function, the unnecessary recalculations are avoided.
    The methods will be executed in the order in which they are found in the pairs
    parameter list.
    @param pairs: a list of tuples (SETTER_METHOD, VALUE), where SETTER_METHOD is the method that shall be called with VALUE as parameter
    @param progress_indicator: an optional parameter to set a ProgressIndicator that tracks the progress of the calculations in the processing chain
    """
    # set progress indicator
    if progress_indicator is not None:
        for p in pairs:
            progress_indicator.AddMethod(p[0])
    # announce
    for p in pairs:
        p[0].NoticeAnnouncement(p[0])
    # set values
    for p in pairs:
        if len(p) == 2:
            p[0](p[1])
        else:
            p[0]()

