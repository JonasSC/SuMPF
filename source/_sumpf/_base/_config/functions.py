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

from .config import Config
from . import objects

def get(name):
    """
    Returns the value which is stored in the top level config under the given name.
    @param name: the name of the variable as a string
    @retval : the value that is stored under the given name
    """
    return objects.config_stack[-1].Get(name)

def set(name, value):
    """
    Stores a value under the given variable name inside the top level config.
    @param name: the name of the variable as a string
    @param value: the value that shall be stored under that name
    """
    objects.config_stack[-1].Set(name, value)

def create_config(variables, path=None):
    """
    Creates a new config and uses it as top level config. Returns the created instance.
    The last top level config will be used as parent for the newly created one.
    @param variables: a dictionary that maps string variable names to their default values in the config
    @param path: a path to a file in which the config is stored. If path is None, the config will not be saved to a file
    @retval : the newly created Config instance
    """
    newconfig = Config(variables=variables, parent=objects.config_stack[-1], path=path)
    objects.config_stack.append(newconfig)
    return newconfig

def get_sumpf_system_config():
    """
    Returns the system wide configuration for sumpf.
    You should not use this in other programs. Instead create a new config for that
    program using the create_config function.
    @retval : the Config instance fot the system wide config for sumpf
    """
    return objects.system

def get_sumpf_user_config():
    """
    Returns the user configuration for sumpf.
    You should not use this in other programs. Instead create a new config for that
    program using the create_config function.
    @retval : the Config instance fot the system wide config for sumpf
    """
    return objects.user

