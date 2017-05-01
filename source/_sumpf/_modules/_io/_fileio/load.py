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

import os
import sumpf
from . import signalformats, spectrumformats
try:
    import watchdog.events
    import watchdog.observers
    watchdog_available = True
except ImportError:
    watchdog_available = False
else:
    class FileEventHandler(watchdog.events.FileSystemEventHandler):
        def __init__(self, filename, callback):
            watchdog.events.FileSystemEventHandler.__init__(self)
            self.__filename = os.path.abspath(filename)
            self.__callback = callback

        def on_any_event(self, event):
            if os.path.abspath(event.src_path) == self.__filename:
                self.__callback()



class LoadChannelData(object):
    """
    Base class for the loader classes for Signals and Spectrums.
    """
    def __init__(self, filename, monitor_file, loader, output_method_name):
        """
        @param filename: the filename of the file, from which the data set shall be loaded
        @param monitor: True to enable monitoring the file for changes, False to disable it
        @param loader: an object with a Load(filename) method, which can be used to load the files (e.g. signalformats.AUTO or spectrumformats.AUTO)
        @param output_method_name: the name of the output method, through which the loaded data set can be retrieved
        """
        self.__filename = filename
        self.__monitor_file = monitor_file
        self.__loader = loader
        self.__output_method_name = output_method_name
        self.__output_method = None
        self.__data = None
        self.__reload = True
        self.__mtime = 0
        self.__observer = None
        if self.__monitor_file:
            self.__StartFileObserver()

    def __del__(self):
        self.__StopFileObserver()

    def _GetData(self):
        """
        Method for loading a data set from the file.
        @retval : the loaded data set
        """
        if self.__reload:
            if not os.path.isfile(self.__filename):
                self.__data = None
                self.__mtime = 0
            else:
                self.__Reload()
        elif self.__monitor_file:
            if os.path.isfile(self.__filename):
                if self.__mtime != os.path.getmtime(self.__filename):
                    self.__OnFileChange()
                    if self.__reload:   # only reload, if a connection has not triggered reloading already
                        self.__Reload()
            else:
                self.__data = None
                self.__mtime = 0
        return self.__data

    @sumpf.Output(bool)
    def GetSuccess(self):
        """
        Returns whether the file has been loaded successfully or if an empty data
        set is generated and returned by the getter method.
        @retval : True, if the file has been loaded successfully; False otherwise
        """
        return self._GetData() is not None

    def SetFilename(self, filename):
        """
        Sets the filename from which the data set shall be loaded.
        This method must be overridden in derrived classes in order to decorate
        it as an Input.
        @param filename: the filename as a string
        """
        self.__filename = filename
        self.__reload = True
        self.__StopFileObserver()
        if self.__monitor_file:
            self.__StartFileObserver()

    @sumpf.Input(bool)
    def SetMonitorFile(self, monitor):
        """
        Enables or disables monitoring the given file for changes.
        @param monitor: True to enable the monitoring, False to disable it
        """
        if self.__monitor_file != monitor:
            if monitor:
                self.__monitor_file = True
                self.__StartFileObserver()
            else:
                self.__monitor_file = False
                self.__StopFileObserver()

    def __Reload(self):
        self.__data = self.__loader.Load(self.__filename)
        if self.__data is not None:
            self.__mtime = os.path.getmtime(self.__filename)
            self.__reload = False

    def __OnFileChange(self):
        method = getattr(self, self.__output_method_name)
        self.SetMonitorFile # avoid, that a ConnectorProxy is passed in the announcement
        method.NoticeAnnouncement(self.SetMonitorFile)
        self.__reload = True
        method.NoticeValueChange(self.SetMonitorFile)

    def __StartFileObserver(self):
        if watchdog_available:
            self.__observer = watchdog.observers.Observer()
            event_handler = FileEventHandler(filename=self.__filename, callback=self.__OnFileChange)
            path = os.path.split(sumpf.helper.normalize_path(self.__filename))[0]
            self.__observer.schedule(event_handler=event_handler, path=path, recursive=False)
            self.__observer.start()

    def __StopFileObserver(self):
        if self.__observer is not None:
            self.__observer.stop()
            self.__observer.join()
            self.__observer = None



class LoadSignal(LoadChannelData):
    """
    A class for loading a Signal from a file.
    If the loading fails (e.g. because the file is missing or it is not a supported
    audio file), an empty Signal is returned by the GetSignal method. The GetSuccess
    method can be used to check, whether the returned Signal has actually been
    loaded from a file.

    If NumPy is available, this class can read Signals in NumPy's npz-format.
    If PySoundFile or scikits.audiolab is available, this class supports wav,
    aiff, flac and ogg as well.
    If oct2py is available, this class can read itaAudio-files that have been
    created with the ITA-Toolbox from the Institute of Technical Acoustics, RWTH
    Aachen University. Also with oct2py, it it possible to read Signals from .mat
    files, which have been created with Matlab and that have a very specific structure.
    This structure is described in the documentation of the class
        sumpf.modules.SaveSignal.MATLAB

    If watchdog is installed, this class also supports monitoring the given file
    for changes. This causes the loaded data to be updated automatically, when
    the file has changed.
    """
    def __init__(self, filename="", monitor_file=False):
        """
        @param filename: the filename of the file, from which the Signal shall be loaded
        @param monitor: True to enable monitoring the file for changes, False to disable it
        """
        LoadChannelData.__init__(self,
                                 filename=filename,
                                 monitor_file=monitor_file,
                                 loader=signalformats.AUTO,
                                 output_method_name="GetSignal")

    @sumpf.Output(sumpf.Signal, caching=False)
    def GetSignal(self):
        """
        Returns the loaded Signal, reloads it if necessary.
        @retval : the loaded Signal
        """
        loaded = self._GetData()
        if loaded is None:
            return sumpf.Signal()
        else:
            return loaded

    @sumpf.Input(str, ("GetSignal", "GetSuccess"))
    def SetFilename(self, filename):
        """
        Sets the filename from which the Signal shall be loaded.
        @param filename: the filename as a string
        """
        LoadChannelData.SetFilename(self, filename)



class LoadSpectrum(LoadChannelData):
    """
    A class for loading a Spectrum from a file.
    If the loading fails (e.g. because the file is missing or it is not a supported
    audio file), an empty Spectrum is returned by the GetSignal method. The GetSuccess
    method can be used to check, whether the returned Spectrum has actually been
    loaded from a file.

    If NumPy is available, this class can read Spectrums in NumPy's npz-format.
    If oct2py is available, this class can read itaAudio-files that have been
    created with the ITA-Toolbox from the Institute of Technical Acoustics, RWTH
    Aachen University. Also with oct2py, it it possible to read Signals from .mat
    files, which have been created with Matlab and that have a very specific structure.
    This structure is described in the documentation of the class
        sumpf.modules.SaveSpectrum.MATLAB

    If watchdog is installed, this class also supports monitoring the given file
    for changes. This causes the loaded data to be updated automatically, when
    the file has changed.
    """
    def __init__(self, filename="", monitor_file=False):
        """
        @param filename: the filename of the file, from which the Spectrum shall be loaded
        @param monitor: True to enable monitoring the file for changes, False to disable it
        """
        LoadChannelData.__init__(self,
                                 filename=filename,
                                 monitor_file=monitor_file,
                                 loader=spectrumformats.AUTO,
                                 output_method_name="GetSpectrum")

    @sumpf.Output(sumpf.Spectrum, caching=False)
    def GetSpectrum(self):
        """
        Returns the loaded Signal, reloads it if necessary.
        @retval : the loaded Signal
        """
        loaded = self._GetData()
        if loaded is None:
            return sumpf.Spectrum()
        else:
            return loaded

    @sumpf.Input(str, ("GetSpectrum", "GetSuccess"))
    def SetFilename(self, filename):
        """
        Sets the filename from which the Spectrum shall be loaded.
        @param filename: the filename as a string
        """
        LoadChannelData.SetFilename(self, filename)

