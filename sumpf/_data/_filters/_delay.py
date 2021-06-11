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

"""Contains the implementation of the DelayFilter class"""

from ._base import Filter

__all__ = ("DelayFilter",)


class DelayFilter(Filter):
    """Creates a filter with a magnitude of 1.0 and a constant group delay."""

    def __init__(self, delay):
        """
        :param delay: the constant group delay in seconds
        """
        Filter.__init__(self,
                        transfer_functions=(DelayFilter.Exp(-delay),),
                        labels=("Delay",))
