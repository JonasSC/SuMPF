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

import math

def counting_number(number):
    """
    Creates a counting number string (e.g. "1st", "2nd", "3rd", "4th" ...) from
    an integer number.
    @param number: an integer number
    @retval : a string
    """
    stringnumber = str(number)
    if stringnumber.endswith("1") and not stringnumber.endswith("11"):
        return "%sst" % stringnumber
    elif stringnumber.endswith("2") and not stringnumber.endswith("12"):
        return "%snd" % stringnumber
    elif stringnumber.endswith("3") and not stringnumber.endswith("13"):
        return "%srd" % stringnumber
    else:
        return "%sth" % stringnumber


def leading_zeros(number, maximum):
    """
    This function creates a string from an integer number, that has as many digits
    as the given maximum number. If the given integer has less digits than the
    maximum number, zeros will be prepended to the string.
    @param number: the integer number that shall be converted to a string
    @param maximum: the integer number to whose number of digits the string shall be extended
    @retval : a string from the given integer with the same number of digits as the given maximum
    """
    width = int(math.ceil(math.log(maximum, 10)))
    return str(number).zfill(width)

