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
from . import objects


def start_mainloop():
	"""
	Starts the wx MainLoop.
	"""
	objects.start_mainloop_lock.acquire()
	if not is_mainloop_running():
		objects.mainloop_thread = threading.Thread(target=objects.app.MainLoop)
		objects.mainloop_thread.start()
	objects.start_mainloop_lock.release()

def is_mainloop_running():
	"""
	Returns if the wx Mainloop is running.
	@retval : True, if the wx Mainloop is running, False otherwise
	"""
	return objects.app.IsMainLoopRunning()

def join_mainloop():
	"""
	Blocks until the mainloop has finished.
	Starts the mainloop if necessary.
	"""
	if not is_mainloop_running():
		start_mainloop()
	objects.mainloop_thread.join()

def run_in_mainloop(function, *args, **kwargs):
	"""
	Some GUI methods need to be run in the GUI MainLoop. This method ensures that
	and blocks until these methods have run.
	@param function: the function that shall be run
	@param args: the non-keyword arguments for the function
	@param kwargs: the keyword arguments for the function
	"""
	if not is_mainloop_running():
		start_mainloop()
	if objects.mainloop_thread.ident == threading.currentThread().ident:
		function(*args, **kwargs)
	else:
		wait_for_mainloop_lock = threading.Lock()
		wait_for_mainloop_lock.acquire()
		def run():
			function(*args, **kwargs)
			wait_for_mainloop_lock.release()
		wx.CallAfter(run)
		start_mainloop()
		wait_for_mainloop_lock.acquire()
		wait_for_mainloop_lock.release()

