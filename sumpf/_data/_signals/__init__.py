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

"""Contains the container classes for signals"""

from ._signal import *

from ._constant import *
from ._energy_decay import *
from ._fade import *
from ._noise import *
from ._sweep import *
from ._waves import *
from ._windows import *

try:
    from ._mls import *
except ImportError:
    pass
try:
    from ._windows_scipy import *
except ImportError:
    pass
