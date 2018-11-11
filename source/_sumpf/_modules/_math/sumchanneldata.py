# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2018 Jonas Schulte-Coerne
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

import functools
import sumpf


class SumSignals(object):
    """
    A module for summing up multiple Signals.
    There are different strategies to sum up Signals which have a different length.
    They are documented in the documentation of "SetLengthConflictStrategy" method.
    The input Signals must have the same sampling rate and the same number of channels.
    """
    # Flags for the handling of length conflicts. See the SetLengthConflictStrategy method for documentation
    RAISE_ERROR = 1
    FILL_WITH_ZEROS = 2
    CROP = 3

    def __init__(self, signals=(), on_length_conflict=RAISE_ERROR):
        """
        @param signals: a list of Signals that shall be summed up. As the constructor can not return the data ids for these Signals, they can only be removed from the summation with the Clear method.
        @param on_length_conflict: one of the flags of the SumSignals class for length conflict resolution (e.g. RAISE_ERROR)
        """
        self.__data = sumpf.helper.MultiInputData()
        for s in signals:
            self.__data.Add(s)
        self.__on_length_conflict = on_length_conflict

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Computes the sum of all input Signals and returns it.
        @retval : the sum of all input Signals or an empty Signal, if no input Signals were given
        """
        data = self.__data.GetData()
        if len(data) == 0:
            return sumpf.Signal()
        elif self.__on_length_conflict == SumSignals.RAISE_ERROR:
            def add(a, b):
                if len(a.GetChannels()) == len(b.GetChannels()):
                    return a + b
                else:
                    raise ValueError("The Signals must have the same number of channels")
            return functools.reduce(add, data)
        elif self.__on_length_conflict == SumSignals.FILL_WITH_ZEROS:
            def add(a, b):
                if len(a.GetChannels()) == len(b.GetChannels()):
                    if len(a) < len(b):
                        zeros = (0.0,) * (len(b) - len(a))
                        new_channels = tuple(c + zeros for c in a.GetChannels())
                        a = sumpf.Signal(channels=new_channels, samplingrate=a.GetSamplingRate(), labels=a.GetLabels())
                    elif len(b) < len(a):
                        zeros = (0.0,) * (len(a) - len(b))
                        new_channels = tuple(c + zeros for c in b.GetChannels())
                        b = sumpf.Signal(channels=new_channels, samplingrate=b.GetSamplingRate(), labels=b.GetLabels())
                    return a + b
                else:
                    raise ValueError("The Signals must have the same number of channels")
            return functools.reduce(add, data)
        elif self.__on_length_conflict == SumSignals.CROP:
            def add(a, b):
                if len(a.GetChannels()) == len(b.GetChannels()):
                    if len(a) < len(b):
                        b = b[0:len(a)]
                    elif len(b) < len(a):
                        a = a[0:len(b)]
                    return a + b
                else:
                    raise ValueError("The Signals must have the same number of channels")
            return functools.reduce(add, data)

    @sumpf.MultiInput(data_type=sumpf.Signal, remove_method="RemoveInput", observers=("GetOutput",))
    def AddInput(self, signal):
        """
        Adds a Signal to the summation.
        @param signal: a Signal that shall be added to the sum
        @retval : an id under which the Signal is stored
        """
        return self.__data.Add(signal)

    def RemoveInput(self, data_id):
        """
        Removes a Signal from the summation.
        @param data_id: the id under which the Signal is stored, that shall be removed
        """
        self.__data.Remove(data_id)

    @sumpf.Trigger("GetOutput")
    def Clear(self):
        """
        Removes all Signals sets from the summation.
        """
        self.__data.Clear()

    @sumpf.Input(type(RAISE_ERROR), "GetOutput")
    def SetLengthConflictStrategy(self, strategy):
        """
        Sets the behavior for when the added Signals do not have the same length.
        The following flags are available:
        RAISE_ERROR for raising a RuntimeError during the summation, if Signals
            with different lengths have been added.
        FILL_WITH_ZEROS for solving the conflict by filling the too short Signals
            with zeros until all Signals have the same length.
        CROP for cropping the length of all added Signals to the length of the
            shortest Signal.
        @param strategy: one of the SumSignals class's flags for length conflict resolution
        """
        self.__on_length_conflict = strategy



class SumSpectrums(object):
    """
    A module for summing up multiple Spectrums.
    There are different strategies to sum up Spectrums which have a different length.
    They are documented in the documentation of "SetLengthConflictStrategy" method.
    The input Spectrums must have the same resolution and the same number of channels.
    """
    # Flags for the handling of length conflicts. See the SetLengthConflictStrategy method for documentation
    RAISE_ERROR = 1
    FILL_WITH_ZEROS = 2
    CROP = 3

    def __init__(self, spectrums=(), on_length_conflict=RAISE_ERROR):
        """
        @param spectrums: a list of Spectrums that shall be summed up. As the constructor can not return the data ids for these Spectrums, they can only be removed from the summation with the Clear method.
        @param on_length_conflict: one of the flags of the SumSpectrums class for length conflict resolution (e.g. RAISE_ERROR)
        """
        self.__data = sumpf.helper.MultiInputData()
        for s in spectrums:
            self.__data.Add(s)
        self.__on_length_conflict = on_length_conflict

    @sumpf.Output(sumpf.Spectrum)
    def GetOutput(self):
        """
        Computes the sum of all input Spectrums and returns it.
        @retval : the sum of all input Spectrums or an empty Spectrum, if no input Spectrums were given
        """
        data = self.__data.GetData()
        if len(data) == 0:
            return sumpf.Spectrum()
        elif self.__on_length_conflict == SumSpectrums.RAISE_ERROR:
            def add(a, b):
                if len(a.GetChannels()) == len(b.GetChannels()):
                    return a + b
                else:
                    raise ValueError("The Spectrums must have the same number of channels")
            return functools.reduce(add, data)
        elif self.__on_length_conflict == SumSpectrums.FILL_WITH_ZEROS:
            def add(a, b):
                if len(a.GetChannels()) == len(b.GetChannels()):
                    if len(a) < len(b):
                        zeros = (0.0,) * (len(b) - len(a))
                        new_channels = tuple(c + zeros for c in a.GetChannels())
                        a = sumpf.Spectrum(channels=new_channels, resolution=a.GetResolution(), labels=a.GetLabels())
                    elif len(b) < len(a):
                        zeros = (0.0,) * (len(a) - len(b))
                        new_channels = tuple(c + zeros for c in b.GetChannels())
                        b = sumpf.Spectrum(channels=new_channels, resolution=b.GetResolution(), labels=b.GetLabels())
                    return a + b
                else:
                    raise ValueError("The Spectrums must have the same number of channels")
            return functools.reduce(add, data)
        elif self.__on_length_conflict == SumSignals.CROP:
            def add(a, b):
                if len(a.GetChannels()) == len(b.GetChannels()):
                    if len(a) < len(b):
                        new_channels = tuple(c[0:len(a)] for c in b.GetChannels())
                        b = sumpf.Spectrum(channels=new_channels, resolution=b.GetResolution(), labels=b.GetLabels())
                    elif len(b) < len(a):
                        new_channels = tuple(c[0:len(b)] for c in a.GetChannels())
                        a = sumpf.Spectrum(channels=new_channels, resolution=a.GetResolution(), labels=a.GetLabels())
                    return a + b
                else:
                    raise ValueError("The Spectrums must have the same number of channels")
            return functools.reduce(add, data)

    @sumpf.MultiInput(data_type=sumpf.Spectrum, remove_method="RemoveInput", observers=("GetOutput",))
    def AddInput(self, spectrum):
        """
        Adds a Spectrum to the summation.
        @param spectrum: a Spectrum that shall be added to the sum
        @retval : an id under which the Spectrum is stored
        """
        return self.__data.Add(spectrum)

    def RemoveInput(self, data_id):
        """
        Removes a Spectrum from the summation.
        @param data_id: the id under which the Spectrum is stored, that shall be removed
        """
        self.__data.Remove(data_id)

    @sumpf.Trigger("GetOutput")
    def Clear(self):
        """
        Removes all Spectrums sets from the summation.
        """
        self.__data.Clear()

    @sumpf.Input(type(RAISE_ERROR), "GetOutput")
    def SetLengthConflictStrategy(self, strategy):
        """
        Sets the behavior for when the added Spectrums do not have the same length.
        The following flags are available:
        RAISE_ERROR for raising a RuntimeError during the summation, if Spectrums
            with different lengths have been added.
        FILL_WITH_ZEROS for solving the conflict by filling the too short Spectrums
            with zeros until all Spectrums have the same length.
        CROP for cropping the length of all added Spectrums to the length of the
            shortest Spectruml.
        @param strategy: one of the SumSpectrums class's flags for length conflict resolution
        """
        self.__on_length_conflict = strategy

