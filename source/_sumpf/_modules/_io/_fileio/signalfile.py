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
from .channeldatafile import ChannelDataFile
from .signalformats import FileFormat, signalformats


class SignalFile(ChannelDataFile):
    """
    A module for saving a Signal to a file and/or loading a Signal from it.

    If NumPy is available, this class can read and write Signals in NumPy's
    npz-format.
    If scikits.audiolab is available, this class supports wav, aif and flac as
    well.
    If oct2py is available, this class can read (but not write) itaAudio-files
    that have been created with the ITA-Toolbox from the Institute of Technical
    Acoustics, RWTH Aachen University.

    Instances of this class might overwrite files without further questions.
    Generally the instance will always write to the given file name when the
    given Signal is not empty. Otherwise it will attempt to load the given file.
    """
    def __init__(self, filename=None, signal=None, format=None):
        """
        If the filename is not None, the file exists and the initial Signal is
        empty, the Signal will be automatically be loaded from the file.
        If the filename is not None and the initial Signal is not empty, the
        initial Signal will be saved to the file, even if the file exists
        already.
        @param filename: None or a string value of a path and filename preferably without the file ending
        @param signal: the Signal instance that shall be stored in the file
        @param format: a subclass of FileFormat that specifies the desired format of the file
        """
        if format is None:
            format = signalformats[0]
        if signal is None:
            signal = sumpf.Signal()
        ChannelDataFile.__init__(self, filename=filename, data=signal, format=format)

    @staticmethod
    def GetFormats():
        """
        Returns a list of all available file formats.
        @retval : a list of FileFormat classes
        """
        return signalformats

    @sumpf.Output(sumpf.Signal)
    def GetSignal(self):
        """
        Loads a Signal from the file and returns it.
        @retval : the loaded Signal
        """
        self._Load()
        return self._data

    @sumpf.Output(float)
    def GetSamplingRate(self):
        """
        Returns the sampling rate of the Signal that has been loaded or will be saved.
        @retval : the sampling rate as a float
        """
        return self._data.GetSamplingRate()

    @sumpf.Input(sumpf.Signal, ["GetSignal", "GetLength", "GetSamplingRate"])
    def SetSignal(self, signal):
        """
        Saves the Signal to the file.
        @param signal: the Signal that shall be saved
        """
        self._data = signal
        self._Save()

    @sumpf.Input(str, ["GetSignal", "GetLength", "GetSamplingRate"])
    def SetFilename(self, filename):
        """
        Override of ChannelDataFile.SetFilename to decorate it with @sumpf.Input.

        Sets the filename under which the data shall be saved or from which the
        data shall be loaded.
        The filename shall contain the path and the name of the file, but not
        the file ending.
        If the file specified by the filename and the format exists and the
        current data set is empty, the file will be loaded. Otherwise the
        current data will be saved to that file.
        @param filename: None or a string value of a path and filename preferably without the file ending
        """
        ChannelDataFile.SetFilename(self, filename)

    @sumpf.Input(FileFormat, ["GetSignal", "GetLength", "GetSamplingRate"])
    def SetFormat(self, format):
        """
        Override of ChannelDataFile.SetFormat to decorate it with @sumpf.Input.

        Sets the format under which the data is or shall be stored on the disk.
        If the file specified by the filename and the format exists and the
        current data set is empty, the file will be loaded. Otherwise the
        current data will be saved to that file.
        @param format: a subclass of FileFormat that specifies the desired format of the file
        """
        ChannelDataFile.SetFormat(self, format)


for c in signalformats:
    setattr(SignalFile, c.__name__, c)

