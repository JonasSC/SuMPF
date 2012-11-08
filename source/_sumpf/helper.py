# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012 Jonas Schulte-Coerne
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

"""
This name space contains some helper functions.
These functions are not the core functionality of SuMPF, but they are useful
inside SuMPF and maybe elsewhere as well.
"""

from ._helper.differentiate import differentiate
from ._helper.normalizepath import normalize_path
from ._helper.walkmodule import walk_module

from ._helper import average
from ._helper import numpydummy

