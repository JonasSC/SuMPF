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

from .interface import InterfaceConfig


class ParentConfig(InterfaceConfig):
    """
    A class whose instance(s) can be given to root configurations that do not have
    a parent config instance (like for example the system wide configuration).
    A ParentConfig instance does not store any values. It always raises an error
    when the Get or Set methods are called and it always returns False when the
    Has method is called.
    """
    def Get(self, name):
        """
        Returns the value which is stored in the config under the given name.
        This always returns an error, as a ParentConfig does not store any variables.
        @param name: the name of the variable as a string
        @retval : the value that is stored under the given name
        """
        raise RuntimeError("A ParentConfig instance does not store any values. So the Get method cannot be called")

    def Set(self, name, value):
        """
        Stores a value under the given variable name.
        This always returns an error, as a ParentConfig does not store any variables.
        @param name: the name of the variable as a string
        @param value: the value that shall be stored under that name
        """
        raise RuntimeError("A ParentConfig instance does not store any values. So the Set method cannot be called")

    def Has(self, name):
        """
        Returns if this config has a variable with the given name.
        Returns always False, as a ParentConfig does not store any variables.
        @param name: the name of the variable as a string
        @retval : False
        """
        return False

