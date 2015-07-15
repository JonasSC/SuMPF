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



class NormalizeSpectrumToAverage(object):
    """
    Normalizes the channels of a Spectrum instance so that the average of its
    magnitude is 1.
    If the average (with the given order) of the Spectrum's magnitude is 0.0,
    the Spectrum will not be normalized to avoid divisions by zero.

    Note that this works differently compared to the NormalizeSignal module. A
    normalized Spectrum which is then inversely fourier transformed does not
    necessarily result in a normalized Signal.
    """
    def __init__(self, input=None, order=2.0, individual=False):
        """
        All parameters are optional
        @param input: the Spectrum which shall be normalized
        @param order: see SetOrder for details
        @param individual: If True, the channels will be normalized individually. If False the proportion between the channels remains the same
        """
        self.__spectrum = input
        self.__order = order
        self.__individual = individual

    @sumpf.Output(sumpf.Spectrum)
    def GetOutput(self):
        """
        Generates the normalized Spectrum and returns it.
        @retval : the normalized Spectrum
        """
        spectrum = None
        if self.__spectrum is None:
            spectrum = sumpf.Spectrum()
        else:
            try:
                spectrum = sumpf.Spectrum(channels=self.__GetChannels(), resolution=self.__spectrum.GetResolution(), labels=self.__spectrum.GetLabels())
            except ValueError:
                spectrum = sumpf.Spectrum(resolution=self.__spectrum.GetResolution())
        return spectrum

    @sumpf.Input(sumpf.Spectrum, "GetOutput")
    def SetInput(self, spectrum):
        """
        Method for setting the Spectrum which shall be normalized.
        @param spectrum: the Spectrum which shall be normalized
        """
        self.__spectrum = spectrum

    @sumpf.Input(float, "GetOutput")
    def SetOrder(self, order):
        """
        Sets the order of the average that defines the normalization factor.
        The following equation will be used to calculate the normalization factor.
            f :=    the normalization factor
            a :=    the average of all samples
            N :=    the number of samples
            o :=    the order
            xi :=   the sample at place i
            Sum :=  the sum from i=0 to i=N-1

            f = 1/a
            with:
            a = ((1/N) * Sum(xi**o)) ** (1/o)

        The average with order 1 will be the ordinary average.
        The average with order 2 will be the RMS value.

        @param order: the order as a float value
        """
        self.__order = float(order)

    @sumpf.Input(bool, "GetOutput")
    def SetIndividual(self, individual):
        """
        Sets if the channels shall be normalized individually.
        If True the average value of each channel will be 1. The proportion
        between the channels will change.
        If False the average of all channels will be 1. The proportion between
        the channels will remain the same.
        @param individual: the boolean value if the channels shall be normalized individually.
        """
        self.__individual = individual

    def __GetChannels(self):
        """
        Calculates the normalized channels and returns them.
        @retval : the normalized channels as a tuple
        """
        if self.__spectrum is not None:
            result = []
            factor = 1
            if not self.__individual:
                factor = self.__GetFactor(channels=self.__spectrum.GetMagnitude())
            for i in range(len(self.__spectrum.GetChannels())):
                if self.__individual:
                    factor = self.__GetFactor(channels=[self.__spectrum.GetMagnitude()[i]])
                channel = tuple(numpy.multiply(self.__spectrum.GetChannels()[i], factor))
                result.append(channel)
            return result
        else:
            return ()

    def __GetFactor(self, channels):
        """
        Calculates the normalization factor and returns it.
        If the average (with the given order) of the Spectrum's magnitude is 0.0,
        the factor will always be 1.0 to avoid divisions by zero.
        @param channels: the list of channels for which the factor shall be calculated
        @retval : the normalization factor as a float
        """
        averager = sumpf.helper.average.SortedSum()
        for c in channels:
            for s in c:
                averager.Add(s ** self.__order)
        average = averager.GetAverage() ** (1.0 / self.__order)
        if average == 0.0:
            return 1.0
        else:
            return 1.0 / average

