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

class InterfaceConfig(object):
    """
    An interface for classes that contain a configuration.
    It defines all methods that a config has to have without implementing them.
    """
    def Get(self, name):
        """
        Returns the value which is stored in the config under the given name.
        @param name: the name of the variable as a string
        @retval : the value that is stored under the given name
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def Set(self, name, value):
        """
        Stores a value under the given variable name.
        @param name: the name of the variable as a string
        @param value: the value that shall be stored under that name
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def Has(self, name):
        """
        Returns if this config has a variable with the given name.
        @param name: the name of the variable as a string
        @retval : True, if a variable with that name exists; False otherwise
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

