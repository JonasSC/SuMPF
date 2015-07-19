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

import sumpf


class ChannelDataFile(object):
    """
    Base class for file handling modules.
    Provides methods for saving and loading a file from a given filename and
    with a given format.
    """
    def __init__(self, filename, data, format):
        """
        If the filename is not None, the file exists and the initial data set is
        empty, the data set will be automatically be loaded from the file.
        If the filename is not None and the initial data set is not empty, the
        initial data set will be saved to the file, even if the file exists
        already.
        @param filename: None or a string value of a path and filename preferably without the file ending
        @param data: the ChannelData instance that shall be stored in the file
        @param format: a subclass of FileFormat that specifies the desired format of the file
        """
        self._data = data
        self.__format = format
        if filename is None:
            self._filename = None
        else:
            self.__SetFilename(filename)

    @staticmethod
    def GetFormats():
        """
        Returns a list of all available file formats.
        @retval : a list of FileFormat classes
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    @sumpf.Output(int)
    def GetLength(self):
        """
        Returns the length of the data set that has been loaded or will be saved.
        @retval : the length as an integer number of samples
        """
        return len(self._data)

    def SetFilename(self, filename):
        """
        Sets the filename under which the data shall be saved or from which the
        data shall be loaded.
        The filename shall contain the path and the name of the file, but not
        the file ending.
        If the file specified by the filename and the format exists and the
        current data set is empty, the file will be loaded. Otherwise the
        current data will be saved to that file.
        @param filename: None or a string value of a path and filename preferably without the file ending
        """
        self.__SetFilename(filename)

    def SetFormat(self, format):
        """
        Sets the format under which the data is or shall be stored on the disk.
        If the file specified by the filename and the format exists and the
        current data set is empty, the file will be loaded. Otherwise the
        current data will be saved to that file.
        @param format: a subclass of FileFormat that specifies the desired format of the file
        """
        self.__format = format
        if self._filename is not None:
            if self.__format.Exists(self._filename):
                if self._data.IsEmpty() or self.__format.read_only:
                    self._Load()
                else:
                    self._Save()
            elif not self.__format.read_only:
                self._Save()

    def _Load(self):
        """
        Causes the current data set to be loaded from the file, if the file exists.
        """
        if self._filename is not None:
            if self.__format.Exists(self._filename):
                self._data = self.__format.Load(self._filename)

    def _Save(self):
        """
        Causes the current data set to be saved to the file, if a filename has
        been specified.
        """
        if self._filename is not None:
            self.__format.Save(self._filename, self._data)

    def __SetFilename(self, filename):
        """
        A private helper method to avoid, that the connector SetFilename is called
        in the constructor.
        @param filename: None or a string value of a path and filename preferably without the file ending
        """
        filename = sumpf.helper.normalize_path(filename)
        delim = "." + self.__format.ending
        split = filename.split(delim)
        if len(split) <= 1:
            self._filename = filename
        else:
            self._filename = delim.join(split[0:-1])
        if self.__format.Exists(self._filename):
            if self._data.IsEmpty() or self.__format.read_only:
                self._Load()
            else:
                self._Save()
        elif not self.__format.read_only:
            self._Save()

