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

import os
import re
import sys

def lib_available(libname):
	try:
		__import__(libname)
		return True
	except ImportError:
		return False

def unload_lib(libname):
	to_remove = []
	for m in sys.modules:
		if m.startswith(libname):
			to_remove.append(m)
	for m in to_remove:
		del sys.modules[m]
	for r in to_remove:
		for m in list(sys.modules.values()):
			if hasattr(m, r):
				delattr(m, r)

def unload_sumpf():
	unload_lib("sumpf")
	unload_lib("_sumpf")

def make_lib_unavailable(libname):
	unload_lib(libname)
	__make_lib_unavailable(libname)
	return not lib_available(libname)

def __make_lib_unavailable(libname):
	regex = re.compile("^" + libname + "\W*")
	for p in sys.path:
		folder = p.rstrip(os.sep).split(os.sep)[-1]
		if regex.match(folder):
			sys.path.remove(p)
	if libname in sys.modules:
		if hasattr(sys.modules[libname], "__file__"):
			path = sys.modules[libname].__file__
			while path != "":
				if path in sys.path:
					sys.path.remove(path)
				path = os.sep.join(path.split(os.sep)[0:-1])

