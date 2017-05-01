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


class Add(object):
    """
    A class for adding two objects.
    The objects can be of an arbitrary type, but they must be addable.
    The type of the result is defined by the input objects.
    """
    def __init__(self, value1=1, value2=1):
        """
        @param value1: the first value for the addition
        @param value2: the second value for the addition
        """
        self.__value1 = value1
        self.__value2 = value2

    @sumpf.Output(None)
    def GetResult(self):
        """
        Returns the result of the addition.
        @retval : the type of the result is defined by the input values
        """
        return self.__value1 + self.__value2

    @sumpf.Input(None, "GetResult")
    def SetValue1(self, value):
        """
        @param value: the first value for the addition
        """
        self.__value1 = value

    @sumpf.Input(None, "GetResult")
    def SetValue2(self, value):
        """
        @param value: the second value for the addition
        """
        self.__value2 = value



class Subtract(object):
    """
    A class for adding two objects.
    The objects can be of an arbitrary type, but they must be addable.
    The type of the result is defined by the input objects.
    The result of the subtraction will be "value1 - value2".
    """
    def __init__(self, value1=1, value2=1):
        """
        @param value1: the first value for the subtraction
        @param value2: the value that shall be subtracted
        """
        self.__value1 = value1
        self.__value2 = value2

    @sumpf.Output(None)
    def GetResult(self):
        """
        Returns the result of the subtraction.
        @retval : the type of the result is defined by the input values
        """
        return self.__value1 - self.__value2

    @sumpf.Input(None, "GetResult")
    def SetValue1(self, value):
        """
        @param value: the first value for the subtraction
        """
        self.__value1 = value

    @sumpf.Input(None, "GetResult")
    def SetValue2(self, value):
        """
        @param value: the value that shall be subtracted
        """
        self.__value2 = value



class Multiply(object):
    """
    A class for adding two objects.
    The objects can be of an arbitrary type, but they must be addable.
    The type of the result is defined by the input objects.
    """
    def __init__(self, value1=1, value2=1):
        """
        @param value1: the first value for the multiplication
        @param value2: the second value for the multiplication
        """
        self.__value1 = value1
        self.__value2 = value2

    @sumpf.Output(None)
    def GetResult(self):
        """
        Returns the result of the multiplication.
        @retval : the type of the result is defined by the input values
        """
        return self.__value1 * self.__value2

    @sumpf.Input(None, "GetResult")
    def SetValue1(self, value):
        """
        @param value: the first value for the multiplication
        """
        self.__value1 = value

    @sumpf.Input(None, "GetResult")
    def SetValue2(self, value):
        """
        @param value: the second value for the multiplication
        """
        self.__value2 = value



class Divide(object):
    """
    A class for dividing two objects.
    The objects can be of an arbitrary type, but they must be dividable.
    The type of the result is defined by the input objects.
    The result of the division will be "value1 / value2"
    """
    def __init__(self, value1=1, value2=1):
        """
        @param value1: the numerator for the division
        @param value2: the denominator for the division
        """
        self.__value1 = value1
        self.__value2 = value2

    @sumpf.Output(None)
    def GetResult(self):
        """
        Returns the result of the division
        @retval : the type of the result is defined by the input values
        """
        return self.__value1 / self.__value2

    @sumpf.Input(None, "GetResult")
    def SetValue1(self, value):
        """
        @param value: the numerator for the division
        """
        self.__value1 = value

    @sumpf.Input(None, "GetResult")
    def SetValue2(self, value):
        """
        @param value: the denominator for the division
        """
        self.__value2 = value



class Power(object):
    """
    A class for computing the power of two objects.
    The objects can be of an arbitrary type, but the power must be computable.
    The type of the result is defined by the input objects.
    The result of the power will be "value1 ** value2"
    """
    def __init__(self, value1=1, value2=1):
        """
        @param value1: the base of the power
        @param value2: the exponent of the power
        """
        self.__value1 = value1
        self.__value2 = value2

    @sumpf.Output(None)
    def GetResult(self):
        """
        Returns the power
        @retval : the type of the result is defined by the input values
        """
        return self.__value1 ** self.__value2

    @sumpf.Input(None, "GetResult")
    def SetValue1(self, value):
        """
        @param value: the base of the power
        """
        self.__value1 = value

    @sumpf.Input(None, "GetResult")
    def SetValue2(self, value):
        """
        @param value: the exponent of the power
        """
        self.__value2 = value

