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

"""
This name space contains the audio processing modules. These modules can be
connected with sumpf.connect to form complex processing chains.
"""

from ._modules.generators import *
from ._modules.interpretations import *
from ._modules.io import *
from ._modules.math import *
from ._modules.metadata import *
from ._modules.models import *
from ._modules.normalize import *
from ._modules.channels import *

try:
    from ._modules.plotting import *
except ImportError:
    pass

