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

import sys
import sumpf

if sys.version_info.major == 2:
    import types
    NoneType = types.NoneType
else:
    NoneType = type(None)



class CreateInterval(object):
    """
    A class for creating an interval tuple out of two numbers
    This can be useful in processing chains, where an interval has to be created
    from given signal lengths, or to generate a frequency range.
    To be able to specify an interval at the end of a sequence, the class offers
    flags to multiply the given numbers with -1. This creates an interval, that
    is interpreted similarly to a slice of a tuple or a list with negative indices
    (e.g. (1,2,3,4)[-2:-1]). It is also possible to set the stop value to None,
    if the last value of a sequence shall be inside the interval (this behavior
    is similar to (1,2,3,4)[2:] or the equivalent (1,2,3,4)[2:None]).
    """
    def __init__(self, start=0, stop=-1, negative_start=False, negative_stop=False):
        """
        @param start: the integer or float start value for the interval (usually the first value inside the interval)
        @param stop: the integer or float end value for the interval (usually the first value outside/after the interval) or None, if the last item of a sequence shall be inside the interval
        @param negative_start: True, if the "start"-parameter shall be multiplied with -1, False otherwise
        @param negative_stop: True, if the "stop"-parameter shall be multiplied with -1, False otherwise
        """
        self.__start = start
        self.__stop = stop
        self.__negative_start = negative_start
        self.__negative_stop = negative_stop

    @sumpf.Output(tuple)
    def GetInterval(self):
        """
        Returns the interval tuple.
        @retval : a tuple (start, stop), where start and stop are the given values
        """
        start = self.__start
        stop = self.__stop
        if self.__negative_start:
            start *= -1
        if stop is not None and self.__negative_stop:
            stop *= -1
        return (start, stop)

    @sumpf.Input((int, float), "GetInterval")
    def SetStart(self, value):
        """
        Sets the start value for the interval.
        @param value: the integer or float start value for the interval (usually the first value inside the interval)
        """
        self.__start = value

    @sumpf.Input((int, float, NoneType), "GetInterval")
    def SetStop(self, value):
        """
        Sets the stop value for the interval.
        @param value: the integer or float end value for the interval (usually the first value outside/after the interval) or None, if the last item of a sequence shall be inside the interval
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

