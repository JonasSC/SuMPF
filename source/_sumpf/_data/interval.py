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

import collections


class SampleInterval(object):
    """
    A class for unifying the definition of sample intervals throughout SuMPF.
    It is not necessary to specify intervals as SampleInterval instances, when using
    SuMPF's signal processing classes. They can be given as tuples or single values
    and will be cast to a SampleInterval internally. Examples for this are given
    at the end of this docstring.

    The start index of the interval defines the index of the first sample, which
    is inside the interval, while the stop index points at the first sample after
    the interval. This behavior is equal to the indexing, that is used for slicing.
    Indices, that exceed the scope of the data set by producing a negative start
    index or a stop index, which is greater than the data set's length, are not
    forbidden, but depending on the application of the interval, they might cause
    errors.

    An interval's boundaries can be specified as integers or floats. Integers are
    interpreted as static sample indices, which are independent of the data set's
    length. Floats define the interval's boundaries relative to the data set's length,
    where 0.0 indexes the first sample and 1.0 the sample at the index of the
    length of the data set, which is the index, that would come after the last sample's
    index (compare: a=[1,2,3]; a[len(a)]).
    Similar to Python's indexing, positive interval boundaries are interpreted as
    being relative to the beginning of the data set, while negative ones are considered
    as offsets from the end of the data set.
    An interval definition can be abbreviated by giving only a single number. When
    an interval is created from a positive number, the interval will span from the
    start of the data set to the index, that is defined by this number. With a negative
    number, the interval will span from this negative index until the end of the
    data set.

    Examples:
      # it is not necessary to pass SampleInterval instances. Tuples or even numbers will do
      sumpf.modules.WindowGenerator(fall_interval=(768, 1024))
      # defining static boundaries
      tuple(range(10))[sumpf.SampleInterval(2, 6).GetSlice(10)]        # (2, 3, 4, 5)
      tuple(range(10))[sumpf.SampleInterval(-6, -2).GetSlice(10)]      # (4, 5, 6, 7)
      # defining relative boundaries
      tuple(range(10))[sumpf.SampleInterval(0.2, 0.6).GetSlice(10)]    # (2, 3, 4, 5)
      tuple(range(10))[sumpf.SampleInterval(-0.6, -0.2).GetSlice(10)]  # (4, 5, 6, 7)
      # abbreviations
      tuple(range(10))[sumpf.SampleInterval(3).GetSlice(10)]           # (0, 1, 2)
      tuple(range(10))[sumpf.SampleInterval(-0.3).GetSlice(10)]        # (7, 8, 9)
      # integers and floats can be mixed
      tuple(range(10))[sumpf.SampleInterval(7, 1.0).GetSlice(10)]      # (7, 8, 9) from index 7 till the end
      # the boundaries can also be passed as an Iterable
      tuple(range(10))[sumpf.SampleInterval((2, 6)).GetSlice(10)]      # (2, 3, 4, 5)
    """
    @staticmethod
    def factory(start=0, stop=None):
        """
        a static factory method, that creates a new SampleInterval method from the
        given parameters, if the parameters are not a SampleInterval instance already.
        Parameters are the boundaries of the interval. If the definition of the
        interval is abbreviated to just one number or the boundaries are defined
        by an integer, both boundaries are derrived from the start parameter, while
        the stop parameter is left being None.
        @param start: an integer, a float, an Iterable or a SampleInterval instance
        @param stop: optional, an integer or a float
        @retval : a SampleInterval instance
        """
        if isinstance(start, SampleInterval):
            return start
        else:
            return SampleInterval(start, stop)

    def __init__(self, start=0, stop=None):
        """
        Parameters are the boundaries of the interval. If the definition of the
        interval is abbreviated to just one number or the boundaries are defined
        by an integer, both boundaries are derrived from the start parameter, while
        the stop parameter is left being None.
        @param start: an integer, a float, an Iterable
        @param stop: optional, an integer or a float
        """
        if isinstance(start, collections.Iterable):
            self.__start, self.__stop = map(self.__Preprocess, start)
        elif stop is None:
            if start >= 0:
                self.__start = 0
                self.__stop = self.__Preprocess(start)
            else:
                self.__start = self.__Preprocess(start)
                self.__stop = 1.0
        else:
            self.__start = self.__Preprocess(start)
            self.__stop = self.__Preprocess(stop)

    def __eq__(self, other):
        """
        This method is called when two SampleIntervals are compared with ==. It returns
        True, when both intervals are equal and False otherwise.
        Due to the limited precision of floating point numbers, testing for equality
        might fail, even when the intervals are equal in practice:
          SampleInterval(0.0, 1.0) == SampleInterval(-1.0, 1.0)    # works everytime
          SampleInterval(0.3, 0.68) == SampleInterval(-0.7, -0.32) # might return False, although the intervals are equal
        @param other: the SampleInterval to which this interval shall be compared
        @retval : True, if the intervals are equal, False otherwise
        """
        start, stop = other._GetStartStop()
        if self.__start != start:
            return False
        elif self.__stop != stop:
            return False
        return True

    def __ne__(self, other):
        """
        This method is called when two SampleIntervals are compared with !=. It returns
        False, when both intervals are equal and True otherwise.
        See the __eq__ method for information on floating point issues.
        @param other: the SampleInterval to which this interval shall be compared
        @retval : True, if the intervals are not equal, False otherwise
        """
        return not self == other

    def GetIndices(self, length):
        """
        Returns the start and stop index of the interval as a tuple of integers.
        @param length: the length of the data set to which the interval shall be applied
        @retval : a tuple of two integers
        """
        return (self.__GetIndex(self.__start, length), self.__GetIndex(self.__stop, length))

    def GetSlice(self, length):
        """
        Returns a slice object, that can be passed to the __getitem__ method of
        the data set:
          d = [0, 1, 2, 3, 4, 5]
          s = sumpf.SampleInterval(2, 4)
          d[s.GetSlice(len(d))]            # [2, 3, 4]
        @param length: the length of the data set to which the interval shall be applied
        @retval : a tuple of two integers
        """
        return slice(*self.GetIndices(length))

    def IsExcessive(self, length):
        """
        Returns True, if the interval exceeds the limits of the data set by either
        producing a negative start index or by producing a stop index, that is
        greater than the length of the data set.
        @param length: the length of the data set to which the interval shall be applied
        @retval : True if the interval exceeds the limits of the data set, False otherwise
        """
        for i in self.GetIndices(length):
            if not (0 <= i <= length):
                return True
        return False

    def IsReversed(self, length):
        """
        Returns True, if the stop index of the interval is smaller than the start index.
        @param length: the length of the data set to which the interval shall be applied
        @retval : True if the interval boundaries are reversed, False otherwise
        """
        indices = self.GetIndices(length)
        if indices[1] < indices[0]:
            return True
        else:
            return False

    def _GetStartStop(self):
        """
        For internal use only.
        Returns the internal representation of the interval
        """
        return self.__start, self.__stop

    def __Preprocess(self, value):
        """
        Preprocesses an interval boundary.
        Normalizes negative float boundaries to its equivalent positive value.
        """
        if isinstance(value, float):
            if value < 0.0:
                return value + 1.0
        return value

    def __GetIndex(self, value, length):
        """
        Computes an index from the given boundary value and the given data set's length.
        """
        if isinstance(value, float):    # convert a float to an integer
            return int(round(value * length))
        elif value < 0:                 # wrap negative integers around
            return value + length
        return value                    # value is a positive integer that can be returned unmodified

