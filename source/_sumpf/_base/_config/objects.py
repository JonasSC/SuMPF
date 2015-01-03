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

import sumpf

from .parent import ParentConfig
from .config import Config

defaults = {"systemconfig_path" : sumpf.helper.normalize_path("/etc/sumpf/config"),
            "userconfig_path" : sumpf.helper.normalize_path("~/.sumpf/config"),
            "default_samplingrate" : 48000.0,
            "default_signal_length" : 2 ** 16,
            "default_frequency" : 1000.0,
            "caching" : True,
            "use_cython" : True}

parent = ParentConfig()
system = Config(variables=defaults, parent=parent, path=defaults["systemconfig_path"])
user = Config(variables={}, parent=system, path=system.Get("userconfig_path"))
run = Config(variables={}, parent=user, path=None)

config_stack = [parent, system, user, run]

