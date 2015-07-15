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

import threading
import wx
from .mainloopthread import mainloop_thread_object


def bump_mainloop():
    """
    Makes sure that the wx MainLoop is running.
    If the MainLoop has finished running, it will be started again.
    """
    mainloop_thread_object.Bump()


def run_in_mainloop(function, *args, **kwargs):
    """
    Runs a given function in the wx MainLoop.
    Some GUI methods need to be run in the GUI MainLoop to avoid crashes. This
    method ensures that and blocks until the given method has run.
    @param function: the function that shall be run
    @param args: the non-keyword arguments for the function
    @param kwargs: the keyword arguments for the function
    @retval : the return value of the function
    """
    if threading.currentThread().ident == mainloop_thread_object.ident:
        return function(*args, **kwargs)
    else:
        done_event = threading.Event()
        f = FunctionForMainLoop(event=done_event, function=function, args=args, kwargs=kwargs)
        wx.CallAfter(f.Run)
        mainloop_thread_object.Bump()
        done_event.wait()
        return f.GetResult()



class FunctionForMainLoop(object):
    """
    A wrapper for a function that shall be run in the wx MainLoop. It stores the
    arguments for the function call and its return value.
    """
    def __init__(self, event, function, args, kwargs):
        """
        @param event: a threading.Event instance whose set method shall be called when the function has finished running
        @param function: the function that shall be run
        @param args: the non-keyword arguments for the function call
        @param kwargs: the keyword arguments for the function call
        """
        self.__event = event
        self.__function = function
        self.__args = args
        self.__kwargs = kwargs
        self.__result = None

    def Run(self):
        """
        This method is passed to the wx.CallAfter function. It runs the given
        function, stores its return value and calls the event's set method.
        """
        self.__result = self.__function(*self.__args, **self.__kwargs)
        self.__event.set()

    def GetResult(self):
        """
        Returns the return value of the called function.
        @retval : the return value of the called function
        """
        return self.__result

