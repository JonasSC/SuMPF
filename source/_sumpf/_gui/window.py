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

import threading
import wx
from .functions import run_in_mainloop, start_mainloop, is_mainloop_running


class Window(wx.Frame):
	"""
	A wx Frame with some modifications for SuMPF.
	- The Show-Method is automatically executed in the wx mainloop
	- A Join-Method that blocks until the Window has been closed
	- An observer for the Close event
	"""
	def __init__(self, *args, **kwargs):
		wx.Frame.__init__(self, *args, **kwargs)
		self.__frame_is_shown_lock = threading.Lock()
		self.__on_close_observers = []

	def Show(self):
		"""
		Override for wx.Frame.Show for thread safety and to enable the Join
		capability.
		"""
		if not self.__frame_is_shown_lock.locked():
			self.__frame_is_shown_lock.acquire()
			run_in_mainloop(wx.Frame.Show, self)
			self.Bind(wx.EVT_CLOSE, self.__OnClose)

	def Close(self):
		"""
		Closes the window.
		"""
		run_in_mainloop(wx.Frame.Close, self)
		self.Join()

	def Join(self):
		"""
		Blocks as long as the window is shown.
		"""
		start_mainloop()
		self.__frame_is_shown_lock.acquire()
		self.__frame_is_shown_lock.release()
		wx.YieldIfNeeded()
		while not isinstance(self, wx._core._wxPyDeadObject):
			wx.YieldIfNeeded()

	def AddObserverOnClose(self, function, *args, **kwargs):
		"""
		Can be used to add an observer function that will be called when the
		window is closed.
		@param function: the function that shall be called
		@param args, kwargs: the arguments with which the function will be called
		"""
		self.__on_close_observers.append((function, args, kwargs))

	def RemoveObserverOnClose(self, function):
		"""
		Removes a function from the list of observers that will be called when
		the window is closed.
		@param function: the function that shall no longer be called
		"""
		to_remove = []
		for i in range(len(self.__on_close_observers)):
			if self.__on_close_observers[i][0] == function:
				to_remove.append(i)
		to_remove.reverse()
		for i in to_remove:
			self.__on_close_observers.pop(i)

	def __OnClose(self, event):
		"""
		Event handler for when the frame is closed.
		It will destroy the frame and unlock the lock for the Join method.
		@param event: the wx event that has been created by closing the frame
		"""
		while self.__on_close_observers != []:
			function, args, kwargs = self.__on_close_observers.pop(0)
			function(*args, **kwargs)
		self.Destroy()
		if self.__frame_is_shown_lock.locked():
			self.__frame_is_shown_lock.release()

