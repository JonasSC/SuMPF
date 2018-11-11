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

import sumpf


class CreateSampleInterval(object):
    """
    A class for creating a SampleInterval instance tuple out of two numbers.
    The numbers can be integer sample indices or float fractions of the data set's
    length. See the SampleInterval class for further information.
    """
    def __init__(self, start=0, stop=1.0, negative_start=False, negative_stop=False):
        """
        @param start: the integer or float start value for the interval (the first value inside the interval)
        @param stop: the integer or float end value for the interval (the first value outside/after the interval)
        @param negative_start: True, if the "start"-parameter shall be multiplied with -1, False otherwise
        @param negative_stop: True, if the "stop"-parameter shall be multiplied with -1, False otherwise
        """
        self.__start = start
        self.__stop = stop
        self.__negative_start = negative_start
        self.__negative_stop = negative_stop

    @sumpf.Output(sumpf.SampleInterval)
    def GetInterval(self):
        """
        Returns the interval.
        @retval : a SampleInterval instance
        """
        start = self.__start
        stop = self.__stop
        if start is None:
            start = 0
        if stop is None:
            stop = 1.0
        if self.__negative_start:
            start *= -1
        if self.__negative_stop:
            stop *= -1
        return sumpf.SampleInterval(start, stop)

    @sumpf.Input((int, float), "GetInterval")
    def SetStart(self, value):
        """
        Sets the start value for the interval.
        @param value: the integer or float start value for the interval (the first value inside the interval)
        """
        self.__start = value

    @sumpf.Input((int, float), "GetInterval")
    def SetStop(self, value):
        """
        Sets the stop value for the interval.
        @param value: the integer or float end value for the interval (the first value outside/after the interval)
        """
        self.__stop = value

    @sumpf.Input(bool, "GetInterval")
    def SetNegativeStart(self, negative):
        """
        Specifies, if the start value shall be multiplied with -1.
        This can be useful to interpret the interval borders relative to the end
        of the sequence, rather than relative to the beginning.
        @param negative_start: True, if the "start"-parameter shall be multiplied with -1, False otherwise
        """
        self.__negative_start = negative

    @sumpf.Input(bool, "GetInterval")
    def SetNegativeStop(self, negative):
        """
        Specifies, if the stop value shall be multiplied with -1.
        This can be useful to interpret the interval borders relative to the end
        of the sequence, rather than relative to the beginning.
        @param negative_stop: True, if the "stop"-parameter shall be multiplied with -1, False otherwise
        """
        self.__negative_stop = negative

