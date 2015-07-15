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

try:    # for python3 compatibility
    import ConfigParser as configparser
except ImportError:
    import configparser

import os

from .interface import InterfaceConfig

SECTION = "main"


class Config(InterfaceConfig):
    """
    A class whose instances contain configurations.
    Each configuration variable is stored under a string name. You can get or set
    this variable by passing the respective name to the Get or Set method.

    Each Config instance has a path to a file where it stores its variables.
    If the given path is None, the config will change, but it will not be stored
    into a file. So next time, the program is started, the config will be reset
    to its defaults.
    The given file needs not exist. If the file does not exist on initialization
    of the instance, all variables are assumed to have the default value. If the
    file does not exist on setting a variable, the file will be created.
    So make sure to have the required write permissions, if you want to set a
    variable's value.
    If the config file has a variable name, that is not in the instance's
    dictionary, an error is raised.

    A Config instance has two ways of looking up the value of a variable.
    At first it looks into its own variable dictionary. The dictionary with the
    default values has been passed to the instance in the constructor. After that
    the values may have been changed by loading a config file.
    If the variable name has not been found in the dictionary, the config tries
    to get the variable's value from its parent config.
    Parent configs are Config instances aswell. They are used to configure the
    default values of a program.

    When the value of a variable is set, the given value will be casted to the
    type of the previous value of the variable. This way the types of the default
    values define the types of the respective config variables.

    An example for the use of parent configs:
    You write a program that uses SuMPF as a framework. Both SuMPF and your
    program have the following configurations:
        - Hard coded default values in the source code
        - A system wide configuration that can be edited by the system administrator
        - A user config that contains the configuration of the respective user.
    Then the stack of configurations would look like this:
        The SuMPF system config has a parent that raises an error each time its
        Get or Set method is called. This way an error is raised as expected when
        a not existing variable is attempted to be set or gotten.
        The variables dictionary that is passed in the constructor contains the
        hard coded defaults for SuMPF.
        The path will most likely be some file in the /etc-directory.

        The SuMPF user config has the SuMPF system config as a parent. So variables
        that have not been specified in the user config will be looked up in the
        system config.
        The variables dictionary will be empty, as the user config takes its default
        values from the system config.
        The path will be some file in the user's home directory.

        The system wide configuration of the program has the SuMPF user config
        as parent config. This way the SuMPF part of the program behaves like
        the user has specified.
        The variables dictionary contains all variables for the program and their
        respective hard coded defauts. If the program needs some SuMPF variables
        to be set to a specific value, these variables can also be in this
        dictionary.
        The path will be again somewhere in a global configuration directory like
        /etc.

        The user config of the program will have the system config as parent. It
        will have an empty dict as variables dictionary and a path to a config
        file somewhere in the user's home directory.

    It is not recommended to instantiate this class directly. The function
    sumpf.config.create_config(...) takes care of the instantiation and setting
    the correct parent. It also takes care that the instance will be used as the
    global configuration.
    """
    def __init__(self, variables, parent, path=None):
        """
        @param variables: a dictionary that maps string variable names to their default values in the config
        @param parent: the parent configuration to which shall be looked when a variable name cannot be found in this config
        @param path: a path to a file in which the config is stored. If path is None, the config will not be saved to a file
        """
        self.__variables = variables
        self.__parent = parent
        self.__path = path
        if self.__path is not None:
            self.__parser = configparser.ConfigParser()
            self.__parser.optionxform = self.__FormatName
            if os.path.exists(self.__path):
                self.Load(self.__path)

    def Get(self, name):
        """
        Returns the value which is stored in the config under the given name.
        @param name: the name of the variable as a string
        @retval : the value that is stored under the given name
        """
        name = self.__FormatName(name)
        if name in self.__variables:
            return self.__variables[name]
        else:
            return self.__parent.Get(name)

    def Set(self, name, value):
        """
        Stores a value under the given variable name.
        The given value will be casted to the type of the previous value of the
        variable.
        @param name: the name of the variable as a string
        @param value: the value that shall be stored under that name
        """
        name = self.__FormatName(name)
        if self.Has(name):
            t = type(self.Get(name))
            self.__variables[name] = t(value)
            self.__Save()
        else:
            raise IndexError("A variable with the name " + name + " does not exist in this config")

    def Has(self, name):
        """
        Returns if this config has a variable with the given name.
        @param name: the name of the variable as a string
        @retval : True, if a variable with that name exists; False otherwise
        """
        name = self.__FormatName(name)
        if name in self.__variables:
            return True
        else:
            return self.__parent.Has(name)

    def Delete(self, name):
        """
        Deletes a variable from this config, so the Get-method returns the
        respective value from the parent config.
        It also deletes the variable from the config file.
        @param name: the name of the variable as a string
        """
        name = self.__FormatName(name)
        if self.__parent.Has(name):
            if name in self.__variables:
                del self.__variables[name]
                self.__Save()
        else:
            raise ValueError("The variable with the name " + name + " does not exist in this config's parent, so it cannot be deleted")

    def Load(self, path):
        """
        Loads the config from the file at path to this config.
        This method does not change the path of the config to the given path.
        Instead it saves all changes to the file at the config path.
        @param path: a path to a file from which the config shall be loaded
        """
        self.__parser.read(path)
        for name in self.__parser.options(SECTION):
            oldvalue = self.Get(name)
            newvalue = oldvalue
            if isinstance(oldvalue, bool):
                newvalue = self.__parser.getboolean(SECTION, name)
            elif isinstance(oldvalue, int):
                newvalue = self.__parser.getint(SECTION, name)
            elif isinstance(oldvalue, float):
                newvalue = self.__parser.getfloat(SECTION, name)
            elif isinstance(oldvalue, str):
                newvalue = self.__parser.get(SECTION, name)
            else:
                raise ValueError("The value of the config option " + name + " has an incompatible type: " + str(type(oldvalue)))
            self.__variables[name] = newvalue

    def __Save(self):
        """
        Saves the current state of the variables-dictionary to the config file.
        """
        if self.__path is not None:
            if not self.__parser.has_section(SECTION):
                self.__parser.add_section(SECTION)
            for name in self.__variables:
                value = self.__variables[name]
                self.__parser.set(SECTION, name, str(value))
            if not os.path.exists(os.path.split(self.__path)[0]):
                os.makedirs(os.path.split(self.__path)[0])
            with open(self.__path, 'w') as configfile:
                self.__parser.write(configfile)

    def __FormatName(self, name):
        return name.replace(" ", "_")

