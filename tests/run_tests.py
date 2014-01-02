# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2014 Jonas Schulte-Coerne
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

import os
import sys
import unittest

# make sure that these tests load SuMPF from the sources and not from any installed version
sys.path.insert(0, os.path.abspath("../source"))

import sumpf
import _common as common

config = {"run_incomplete_tests": False, 	# if False, incomplete tests will be skipped
          "write_to_disk": False, 			# if False, tests that write to disk will be skipped
          "test_gui": False, 				# if False, tests that run a GUI will be skipped
          "run_long_tests": False, 			# if False, long running tests will be skipped
          "run_time_variant_tests": False, 	# if False, time variant tests or tests with random numbers are skipped. This can be useful, because it is not possible to guarantee that the test passes, even if everything is correct
          "run_interactive_tests": False, 	# if False, tests that require input from the user are skipped

          "modify_config": True, 			# if True, some SuMPF config values will be changed and a second test run will be made
          "unload_numpy": False, 			# if True, the numpy module will be unimported, so it can be tested, how SuMPF performs without it

          "root_dir": "..",
          "source_dirs": [os.path.join("..", "source"), os.path.join("..", "tests"), os.path.join("..", "tools")],
          "source_dir": os.path.join("..", "source"),
          "test_dir": os.path.join("..", "tests")
         }

sumpf.config.create_config(variables=config)

if sumpf.config.get("unload_numpy"):
	common.make_lib_unavailable("numpy")
	common.unload_sumpf()
	common.unload_lib("_common")
	import sumpf
	import _common as common
	sumpf.config.create_config(variables=config)

if (not hasattr(sumpf, "gui")) and (sumpf.config.get("test_gui") or sumpf.config.get("run_interactive_tests")):
	sumpf.config.set("test_gui", False)
	sumpf.config.set("run_interactive_tests", False)
	print("Tests of the GUI and interactive tests are skipped because of a missing library.")

from base import *
from data import *
from examples import *
from gui import *
from helper import *
from modules import *
from other import *

if __name__ == "__main__":
	print(("Testing %s" % str(sumpf)))
	unittest.main(exit=False)
	if sumpf.config.get("modify_config"):
		sumpf.config.set("default_samplingrate", sumpf.config.get("default_samplingrate") + 13.6)
		sumpf.config.set("default_signal_length", sumpf.config.get("default_signal_length") + 7)
		sumpf.config.set("default_frequency", sumpf.config.get("default_frequency") / 3.0)
		sumpf.config.set("caching", not sumpf.config.get("caching"))
		unittest.main()

