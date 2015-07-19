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

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy



class AverageChannelData(object):
    """
    A base class for calculating the average of ChannelData instances.
    """
    def __init__(self):
        self.__channels = []
        self.__index = 0
        self.__number = 1
        self._lastdataset = None    # used in the derived classes

    def _AddDataSet(self, dataset):
        """
        Method that can be used from derived classes to add data to the set.
        @param dataset: a data set over which shall also be averaged
        """
        ds_channels = dataset.GetChannels()
        if self._lastdataset is not None:
            if len(dataset) != len(self._lastdataset):
                raise ValueError("The given data set has a different length than the other data sets")
            if len(ds_channels) != len(self.__channels):
                raise ValueError("The given data set has a different number of channels than the other data sets")
            for i in range(len(ds_channels)):
                self.__channels[i].Add(ds_channels[i])
        else:
            for c in ds_channels:
                self.__channels.append(sumpf.helper.average.SumList(values=[c]))
        self._lastdataset = dataset

    @sumpf.Trigger()
    def Clear(self):
        """
        Clears all data so next time the averaging process will start with
        completely new data.
        """
        self.__channels = []
        self.__index = 0
        self._lastdataset = None

    @sumpf.Input(int)
    def SetNumber(self, number):
        """
        Sets the number of over which the average shall be taken.
        This is only necessary when the average is taken through connections.
        @param number: the integer number of how many data instances shall be taken for the average
        """
        self.__number = number

    @sumpf.Output(int)
    def TriggerDataCreation(self):
        """
        An output method that can be connected to the triggers that create
        new data for the averaging process.
        @retval : The index in the "to average"-list of the data set which shall be created.
        """
        return self.__index

    @sumpf.Input(int, "TriggerDataCreation")
    def __TriggerTrigger(self, index):
        """
        An input method that sets the current index and triggers the DataCreationTrigger.
        @param index: the number of the dataset which is currently being taken.
        """
        self.__index = index

    def _Start(self):
        """
        Method that can be used from derived classes to start the averaging process.
        """
        self.Clear()
        self.__TriggerTrigger(0)
        sumpf.activate_output(self.TriggerDataCreation)
        for i in range(1, self.__number):
            self.__TriggerTrigger(i)
        sumpf.deactivate_output(self.TriggerDataCreation)

    def _GetChannels(self):
        """
        Calculates the averaged data set and returns its channels.
        @retval : the averaged channels as a tuple
        """
        if len(self.__channels) > 0:
            result = []
            for a in self.__channels:
                channel = tuple(a.GetAverage())
                result.append(channel)
            return result
        else:
            return ()

    def _GetLabels(self):
        """
        Generates a label for each output channel and returns them as a tuple.
        @retval : a tuple of string labels
        """
        labels = []
        for i in range(len(self._lastdataset.GetChannels())):
            labels.append("Average " + str(i + 1))
        return labels



class AverageSignals(AverageChannelData):
    """
    Calculates the average of multiple Signals.
    The usage between the ordinary Set/Get-method-way and the way with
    connections is quite different, so an example for each way is given here.
    Say, you have a recording object "rec" which has a "Start"-method that
    starts the recording process and a "GetSignal"-method that returns the
    recorded Signal. You want to record three Signals and calculate the average
    of them:
    The ordinary way would look like this:
        # record Signals
        rec.Start()
        signal1 = rec.GetSignal()
        rec.Start()
        signal2 = rec.GetSignal()
        rec.Start()
        signal3 = rec.GetSignal()
        # initiate AverageSignals instance
        avg = sumpf.AverageSignals()
        avg.AddInput(signal1)
        avg.AddInput(signal2)
        avg.AddInput(signal3)
        # calculate average
        result = avg.GetOutput()
    The way with connections would look like this:
        avg = sumpf.AverageSignals()
        # set up the connections
        sumpf.connect(rec.GetSignal, avg.AddInput)
        sumpf.connect(avg.TriggerDataCreation, rec.Start)
        # calculate average
        avg.SetNumber(3)
        avg.Start()
        result = avg.GetOutput()
    """
    def __init__(self, signals=[]):
        """
        @param signals: optional list of Signals that shall be averaged
        """
        AverageChannelData.__init__(self)
        for s in signals:
            self.__AddInput(s)

    @sumpf.Input(sumpf.Signal)
    def AddInput(self, signal):
        """
        Adds a Signal to the set of Signals over which shall be averaged.
        @param signal: a Signal over which shall also be averaged
        """
        self.__AddInput(signal)

    @sumpf.Trigger("GetOutput")
    def Start(self):
        """
        Starts the data creation process.
        """
        self._Start()

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Generates the averaged Signal and returns it.
        @retval : the averaged output Signal
        """
        signal = None
        if self._lastdataset is None:
            signal = sumpf.Signal()
        else:
            try:
                signal = sumpf.Signal(channels=self._GetChannels(), samplingrate=self._lastdataset.GetSamplingRate(), labels=self._GetLabels())
            except ValueError:
                signal = sumpf.Signal(samplingrate=self._lastdataset.GetSamplingRate())
        return signal

    def __AddInput(self, signal):
        """
        A private helper method to avoid, that the connector AddInput is called
        in the constructor.
        @param signal: a Signal over which shall also be averaged
        """
        if self._lastdataset is not None:
            if signal.GetSamplingRate() != self._lastdataset.GetSamplingRate():
                raise ValueError("The given Signal has a different sampling rate than the other Signals")
        self._AddDataSet(signal)



class AverageSpectrums(AverageChannelData):
    """
    Calculates the average of multiple Spectrums.
    See AverageSignals for usage details and examples.
    """
    def __init__(self, spectrums=[]):
        """
        @param spectrums: optional list of Spectrums that shall be averaged
        """
        AverageChannelData.__init__(self)
        for s in spectrums:
            self.__AddInput(s)

    @sumpf.Input(sumpf.Spectrum)
    def AddInput(self, spectrum):
        """
        Adds a Spectrum to the set of Spectrums over which shall be averaged.
        @param spectrum: a Spectrum over which shall also be averaged
        """
        self.__AddInput(spectrum)

    @sumpf.Trigger("GetOutput")
    def Start(self):
        """
        Starts the data creation process.
        """
        self._Start()

    @sumpf.Output(sumpf.Spectrum)
    def GetOutput(self):
        """
        Generates the averaged Spectrum and returns it.
        @retval : the averaged output Spectrum
        """
        spectrum = None
        if self._lastdataset is None:
            spectrum = sumpf.Spectrum()
        else:
            try:
                spectrum = sumpf.Spectrum(channels=self._GetChannels(), resolution=self._lastdataset.GetResolution(), labels=self._GetLabels())
            except ValueError:
                spectrum = sumpf.Spectrum(resolution=self._lastdataset.GetResolution())
        return spectrum

    def __AddInput(self, spectrum):
        """
        A private helper method to avoid, that the connector AddInput is called
        in the constructor.
        @param spectrum: a Spectrum over which shall also be averaged
        """
        if self._lastdataset is not None:
            if spectrum.GetResolution() != self._lastdataset.GetResolution():
                raise ValueError("The given Spectrum has a different resolution than the other Spectrums")
        self._AddDataSet(spectrum)

