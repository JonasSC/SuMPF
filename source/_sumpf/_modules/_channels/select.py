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


class SelectChannelData(object):
    """
    Module for selecting one out of two ChannelData instances.
    """
    def __init__(self, input1, input2, selection):
        """
        @param input1: the first input data set
        @param input2: the second input data set
        @param selection: either 1 or 2 for selecting the first or second data set
        """
        self.__input1 = input1
        self.__input2 = input2
        if selection in [1, 2]:
            self.__selection = selection
        else:
            raise ValueError("The given selection is not valid")

    def GetOutput(self):
        """
        Returns the selected data set.
        @retval : the selected data set
        """
        if self.__selection == 1:
            return self.__input1
        elif self.__selection == 2:
            return self.__input2
        else:
            raise ValueError("The given selection is not valid")

    def SetInput1(self, input):
        """
        Sets the first input data set.
        @param input: the first input data set
        """
        self.__input1 = input

    def SetInput2(self, input):
        """
        Sets the second input data set.
        @param input: the second input data set
        """
        self.__input2 = input

    @sumpf.Input(int, "GetOutput")
    def SetSelection(self, selection):
        """
        Sets the selection which data set shall be returned by GetOutput.
        @param selection: either 1 or 2 for selecting the first or second data set
        """
        if selection in [1, 2]:
            self.__selection = selection
        else:
            raise ValueError("The given selection is not valid")



class SelectSignal(SelectChannelData):
    """
    Module for selecting one out of two Signals.
    This can be used like an AB-Box to bypass a part of the processing chain
    without making and breaking any connections.
    """
    def __init__(self, input1=None, input2=None, selection=1):
        """
        @param input1: the first input Signal
        @param input2: the second input Signal
        @param selection: either 1 or 2 for selecting the first or second Signal
        """
        if input1 is None:
            input1 = sumpf.Signal()
        if input2 is None:
            input2 = sumpf.Signal()
        SelectChannelData.__init__(self, input1, input2, selection=selection)

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        """
        Returns the selected Signal.
        Override of SelectChannelData.GetOutput to add the sumpf.Output decorator.
        @retval : the selected Signal
        """
        return SelectChannelData.GetOutput(self)

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput1(self, input):
        """
        Sets the first input Signal.
        Override of SelectChannelData.SetInput1 to add the sumpf.Input decorator.
        @param input: the first input Signal
        """
        SelectChannelData.SetInput1(self, input)

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput2(self, input):
        """
        Sets the second input Signal.
        Override of SelectChannelData.SetInput2 to add the sumpf.Input decorator.
        @param input: the second input Signal
        """
        SelectChannelData.SetInput2(self, input)



class SelectSpectrum(SelectChannelData):
    """
    Module for selecting one out of two Spectrums.
    This can be used like an AB-Box to bypass a part of the processing chain
    without making and breaking any connections.
    """
    def __init__(self, input1=None, input2=None, selection=1):
        """
        @param input1: the first input Spectrum
        @param input2: the second input Spectrum
        @param selection: either 1 or 2 for selecting the first or second Spectrum
        """
        if input1 is None:
            input1 = sumpf.Spectrum()
        if input2 is None:
            input2 = sumpf.Spectrum()
        SelectChannelData.__init__(self, input1, input2, selection=selection)

    @sumpf.Output(sumpf.Spectrum)
    def GetOutput(self):
        """
        Returns the selected Spectrum.
        Override of SelectChannelData.GetOutput to add the sumpf.Output decorator.
        @retval : the selected Spectrum
        """
        return SelectChannelData.GetOutput(self)

    @sumpf.Input(sumpf.Spectrum, "GetOutput")
    def SetInput1(self, input):
        """
        Sets the first input Spectrum.
        Override of SelectChannelData.SetInput1 to add the sumpf.Input decorator.
        @param input: the first input Spectrum
        """
        SelectChannelData.SetInput1(self, input)

    @sumpf.Input(sumpf.Spectrum, "GetOutput")
    def SetInput2(self, input):
        """
        Sets the second input Spectrum.
        Override of SelectChannelData.SetInput2 to add the sumpf.Input decorator.
        @param input: the second input Spectrum
        """
        SelectChannelData.SetInput2(self, input)

