# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2017 Jonas Schulte-Coerne
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



class TextFormat(FileFormat):
    """
    Base class for saving and loading text files.
    """
    @staticmethod
    def _GetProperties(filename):
        """
        Reads the given file and returns the following properties:
         - the labels
         - the number of channels in the file
         - the number of samples in the file
         - the minimum value of the first column of the file (e.g. the minimum frequency for spectrums or the minimum time for signals)
         - the maximum value of the first column of the file (e.g. the maximum frequency for spectrums or the maximum time for signals)
        @retval : a tuple (labels, number of channels, number of samples, minimum of first column, maximum of first column)
        """
        with open(filename) as f:
            labels = ()
            number_of_channels = 0
            number_of_samples = 0
            minimum_x = None
            maximum_x = 0.0
            for l in f:
                line = l.strip()
                if line == "":
                    continue
                elif line.startswith("# LABELS:"):
                    labels = ":".join(line.split(":")[1:]).strip().split("\t")
                elif not line.startswith("#"):
                    number_of_samples += 1
                    data = line.split("#")[0].strip().split("\t")
                    number_of_channels = max(number_of_channels, len(data) - 1)
                    x = float(data[0])
                    if minimum_x is None:
                        minimum_x = x
                    else:
                        minimum_x = min(minimum_x, x)
                    maximum_x = max(maximum_x, x)
            return labels, number_of_channels, number_of_samples, minimum_x, maximum_x

