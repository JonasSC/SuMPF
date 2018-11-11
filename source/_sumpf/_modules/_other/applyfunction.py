# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2018 Jonas Schulte-Coerne
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

import collections
import sumpf


class ApplyFunction(object):
    """
    A class for applying a function to an input object. This can for example be
    useful, when it is necessary to cast the object to a specific type.
    Depending on SuMPF's settings, the output of the GetResult method might be
    cached. So if calling the function has side effects, the function might not
    be called as often as desired.
    """
    def __init__(self, obj=None, function=str):
        """
        @param object: the input object, that shall be passed to the function
        @param function: a callable object, that shall process the input object
        """
        self.__object = obj
        self.__function = function

    @sumpf.Output(None)
    def GetResult(self):
        """
        Runs the function and returns its result.
        """
        return self.__function(self.__object)

    @sumpf.Input(None, "GetResult")
    def SetObject(self, obj):
        """
        Sets the object, that shall be passed to the function.
        """
        self.__object = obj

    @sumpf.Input(collections.Callable, "GetResult")
    def SetFunction(self, function):
        """
        Sets the function, that is used to process the input object
        @param key: a callable object
        """
        self.__function = function

