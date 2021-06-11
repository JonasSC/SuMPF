# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2021 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""Contains helper functions for text and string processing"""

__all__ = ("counting_number",)


def counting_number(number):
    """
    Creates a counting number string (e.g. "1st", "2nd", "3rd", "4th" ...) from
    an integer number.
    :param number: an integer number
    :returns: a string
    """
    s = str(number)
    if s.endswith("1") and not s.endswith("11"):
        return f"{s}st"
    elif s.endswith("2") and not s.endswith("12"):
        return f"{s}nd"
    elif s.endswith("3") and not s.endswith("13"):
        return f"{s}rd"
    else:
        return f"{s}th"
