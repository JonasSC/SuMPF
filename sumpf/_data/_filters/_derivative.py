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

"""Contains the implementation of the DerivativeFilter class"""

from ._base import Filter

__all__ = ("DerivativeFilter",)


class DerivativeFilter(Filter):
    """Creates a filter, whose transfer function increases proportional to the frequency.
    This multiplication with the frequency variable ``s`` is equivalent to computing
    a derivative in the time domain (except for a constant scaling factor).
    """

    def __init__(self):
        Filter.__init__(self,
                        transfer_functions=(DerivativeFilter.Polynomial((1.0, 0.0)),),
                        labels=("Derivative",))
