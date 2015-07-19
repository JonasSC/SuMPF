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

import gc

import sumpf


def call_delete_method():
    """
    Checks if the instance has a delete method and calls it if it is so.
    """
    for obj in gc.garbage:
        if hasattr(obj, "Delete"):
            getattr(obj, "Delete")()

def destroy_connector_references():
    """
    A garbage collector function that helps to delete objects with connectors.
    Normally this is not needed, but when the object has a destructor method, the
    garbage collector does not know in which order it shall delete the object and
    the connector. This garbage collector function breaks this dependency cycle.
    """
    for obj in gc.garbage:
        sumpf.destroy_connectors(obj)


destroyer_functions = [call_delete_method, destroy_connector_references]

