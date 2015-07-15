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

import wx
import threading

class MainLoopThread(threading.Thread):
    """
    The object of this class handles the wx MainLoop and the wx App that is needed
    for SuMPF's GUI. It provides a way to restart the MainLoop, when it has finished
    running and makes sure that the MainLoop always runs in the same thread to avoid
    errors.
    Since there can be only one wx App, there can also be only one object of
    this class per running SuMPF instance. This classes instance cannot be accessed
    directly through SuMPF's GUI. Instead the functions sumpf.gui.bump_mainloop
    and sumpf.gui.run_in_mainloop are provided.
    This thread is a daemon thread, so it is stopped automatically when all non-daemon
    threads have finished running.
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.__app = wx.App()
        self.__bump_event = threading.Event()
        self.start()

    def run(self):
        """
        This method will be run, when the thread is started. It runs the wx MainLoop
        After the MainLoop has run, it waits for a call of Bump() to restart the
        MainLoop.
        This thread is a daemon thread, so it is stopped automatically when all
        non-daemon threads have finished running.
        """
        while True:
            self.__bump_event.clear()
            self.__app.MainLoop()
            self.__bump_event.wait()

    def Bump(self):
        """
        Makes sure that the wx MainLoop is running by either restarting immediately
        (if it has finished) it, or (if it is still running) by making it restart
        after its next finish.
        """
        self.__bump_event.set()

mainloop_thread_object = MainLoopThread()

