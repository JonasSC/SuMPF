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

import os
import re
import sys

def lib_available(libname, dont_import=False):
    """
    Tests if a library can be imported as a module.
    @param libname: the name of the module
    @param dont_import: if True, a different test for availability is used, that does not import the module, if it is available. This test might fail to find a module that actually is available.
    """
    if dont_import:
        if sys.version_info.major == 2: # Python2
            import imp
            try:
                imp.find_module(libname)
                return True
            except ImportError:
                return False
        else:                           # Python3 (and maybe later)
            import importlib.util
            return importlib.util.find_spec(libname) is not None
    else:
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
    # remove the module from the path, so it cannot be found during importing
    regex = re.compile("^" + libname + "\W*")
    paths_to_remove = []
    for p in sys.path:
        folder = p.rstrip(os.sep).split(os.sep)[-1]
        if regex.match(folder):
            paths_to_remove.append(p)
    for p in paths_to_remove:
        sys.path.remove(p)
    # if the module has been imported already, look up the file and remove that from the path
    if libname in sys.modules:
        if hasattr(sys.modules[libname], "__file__"):
            path = sys.modules[libname].__file__
            while path != "":
                if path in sys.path:
                    sys.path.remove(path)
                path = os.sep.join(path.split(os.sep)[0:-1])
    # add a new path that will lead to an import with the same name, which will raise an ImportError
    unavailable_lib_path = os.path.abspath(os.path.join("_common", "unavailable_libs", libname))
    if os.path.exists(unavailable_lib_path):
        sys.path.insert(0, os.path.abspath(unavailable_lib_path))

