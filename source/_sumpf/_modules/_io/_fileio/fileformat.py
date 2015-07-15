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


class FileFormat(object):
    """
    Abstract base class for describing file formats.
    Subclasses of this have to provide the correct file ending attribute and
    methods to load and save.
    """
    ending = None
    read_only = False

    def __init__(self):
        """
        This constructor inhibits instances of this class.
        """
        raise RuntimeError("This class may not be instantiated")

    @classmethod
    def Exists(cls, filename):
        """
        Tests the existence of a file with the given filename.
        The filename has to consist of the path and the name of the file, but
        without the file ending as this is appended automatically by this method.
        @param filename: a string value of a path and filename without file ending
        @retval : True if the file exists, False otherwise
        """
        return os.path.exists("%s.%s" % (filename, cls.ending))

    @classmethod
    def Load(cls, filename):
        """
        Virtual method whose overrides shall load a data set from a file and return it.
        @param filename: a string value of a path and filename without file ending
        @retval : the loaded data set
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    @classmethod
    def Save(cls, filename, data):
        """
        Virtual method whose overrides shall save a data set to a file.
        @param filename: a string value of a path and filename without file ending
        @param data : the data set which is to save
        """
        if cls.read_only:
            raise RuntimeError("This file format can only be read, not written")
        else:
            raise NotImplementedError("This method should have been overridden in a derived class")

