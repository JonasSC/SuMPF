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

import inspect
import copy

def walk_module(module):
    """
    This function creates and returns a tree like list of attributes for a given
    module in a similar manner to os.walk.
    The result will be a list of tuples which hold the attributes of the given
    module or one of its submodules. The tuple for the given module will be the
    first element in the list.
    Each tuple will have five elements:
     0. path:       a list of modules that are the path to the current module.
                    The given module will always be the first element in this
                    list while the current module will be the last element.
     1. modules:    a list of all modules which are in the current module
     2. classes:    a list of all classes which are in the current module
     3. functions:  a list of all functions which are in the current module
     4. variables:  a list of all variable names which are in the current module
    @param module: the module for which the list shall be created
    @retval : a tree like list
    """
    def walk(path):
        modules = []
        classes = []
        functions = []
        variables = []
        for i in vars(path[-1]):
            v = vars(path[-1])[i]
            if inspect.ismodule(v) and v.__name__ != "__builtin__":
                modules.append(v)
            elif inspect.isclass(v):
                classes.append(v)
            elif inspect.isfunction(v):
                functions.append(v)
            else:
                variables.append(i)
        result = [(path, modules, classes, functions, variables)]
        for m in modules:
            if m not in path:
                subpath = copy.copy(path)
                subpath.append(m)
                for r in walk(subpath):
                    result.append(r)
        return result
    return walk([module])

