# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2016 Jonas Schulte-Coerne
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
from . import signalformats
from . import spectrumformats


class SaveSignal(object):
    """
    A class for saving a Signal to a file.

    If NumPy is available, this class can write Signals in NumPy's npz-format.
    If PySoundFile or scikits.audiolab is available, this class supports wav,
    aiff, flac and ogg as well.
    If oct2py is available, it it possible to write Signals to Matlab .mat files.
    The structure of these files is described in the documentation of the class
        sumpf.modules.SaveSignal.MATLAB
    """
    AUTO = signalformats.AUTO
    TEXT = signalformats.TEXT
    if signalformats.numpy_available:
        NUMPY_NPZ = signalformats.NUMPY_NPZ
    if signalformats.audiolab_available or signalformats.soundfile_available:
        AIFF_FLOAT = signalformats.AIFF_FLOAT
        AIFF_INT = signalformats.AIFF_INT
        FLAC = signalformats.FLAC
        WAV_DOUBLE = signalformats.WAV_DOUBLE
        WAV_FLOAT = signalformats.WAV_FLOAT
        WAV_INT = signalformats.WAV_INT
    if signalformats.audiolab_available:
        OGG_VORBIS = signalformats.OGG_VORBIS
    if signalformats.oct2py_available:
        MATLAB = signalformats.MATLAB

    def __init__(self, filename=None, signal=None, file_format=signalformats.AUTO):
        """
        @param filename: the filename of the file, in which the Signal shall be stored
        @param signal: the Signal, that shall be stored
        @param file_format: the file format, in which the signal shall be stored or None to select the default format
        """
        self.__filename = filename
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
        if file_format is None:
            self.__file_format = signalformats.signalformats[0]
        else:
            self.__file_format = file_format
        self.__Save()

    @staticmethod
    def GetFormats():
        """
        A static method, that returns a list of all available file formats, in
        which Signals can be stored.
        @retval : a list of FileFormat classes
        """
        return [f for f in signalformats.signalformats if not f.read_only]

    @sumpf.Input(sumpf.Signal)
    def SetSignal(self, signal):
        """
        Sets the Signal, that shall be stored.
        @param signal: a Signal instance
        """
        self.__signal = signal
        self.__Save()

    @sumpf.Input(str)
    def SetFilename(self, filename):
        """
        Sets the filename of the file, in which the Signal shall be stored
        @param filename: the filename as a string
        """
        self.__filename = filename
        self.__Save()

    @sumpf.Input(signalformats.FileFormat)
    def SetFormat(self, file_format):
        """
        Sets the format in which the Signal shall be stored on the disk.
        @param file_format: a subclass of FileFormat that specifies the desired format of the file
        """
        self.__file_format = file_format
        self.__Save()

    def __Save(self):
        if self.__filename is not None:
            self.__file_format.Save(filename=self.__filename, data=self.__signal)



class SaveSpectrum(object):
    """
    A class for saving a Spectrum to a file.

    If NumPy is available, this class can write Signals in NumPy's npz-format.
    If oct2py is available, it it possible to write Signals to Matlab .mat files.
    The structure of these files is described in the documentation of the class
        sumpf.modules.SaveSignal.MATLAB
    """
    AUTO = spectrumformats.AUTO
    TEXT_I = spectrumformats.TEXT_I
    TEXT_J = spectrumformats.TEXT_J
    if spectrumformats.numpy_available:
        NUMPY_NPZ = spectrumformats.NUMPY_NPZ
    if spectrumformats.oct2py_available:
        MATLAB = spectrumformats.MATLAB

    def __init__(self, filename=None, spectrum=None, file_format=spectrumformats.AUTO):
        """
        @param filename: the filename of the file, in which the Spectrum shall be stored
        @param spectrum: the Spectrum, that shall be stored
        @param file_format: the file format, in which the spectrum shall be stored or None to select the default format
        """
        self.__filename = filename
        if spectrum is None:
            self.__spectrum = sumpf.Spectrum()
        else:
            self.__spectrum = spectrum
        if file_format is None:
            self.__file_format = spectrumformats.spectrumformats[0]
        else:
            self.__file_format = file_format
        self.__Save()

    @staticmethod
    def GetFormats():
        """
        A static method, that returns a list of all available file formats, in
        which Spectrums can be stored.
        @retval : a list of FileFormat classes
        """
        return [f for f in spectrumformats.spectrumformats if not f.read_only]

    @sumpf.Input(sumpf.Spectrum)
    def SetSpectrum(self, spectrum):
        """
        Sets the Spectrum, that shall be stored.
        @param spectrum: a Spectrum instance
        """
        self.__spectrum = spectrum
        self.__Save()

    @sumpf.Input(str)
    def SetFilename(self, filename):
        """
        Sets the filename of the file, in which the Spectrum shall be stored
        @param filename: the filename as a string
        """
        self.__filename = filename
        self.__Save()

    @sumpf.Input(signalformats.FileFormat)
    def SetFormat(self, file_format):
        """
        Sets the format in which the Spectrum shall be stored on the disk.
        @param file_format: a subclass of FileFormat that specifies the desired format of the file
        """
        self.__file_format = file_format
        self.__Save()

    def __Save(self):
        if self.__filename is not None:
            self.__file_format.Save(filename=self.__filename, data=self.__spectrum)

