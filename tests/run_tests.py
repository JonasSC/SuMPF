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

import argparse
import os
import sys
import unittest

# make sure that these tests load SuMPF from the sources and not from any installed version
sys.path.insert(0, os.path.abspath("../source"))

import sumpf
import _common as common

config = {"run_incomplete_tests": False,    # if False, incomplete tests will be skipped
          "write_to_disk": False,           # if False, tests that write to disk will be skipped
          "test_gui": False,                # if False, tests that run a GUI will be skipped
          "run_long_tests": False,          # if False, long running tests will be skipped
          "run_time_variant_tests": False,  # if False, time variant tests or tests with random numbers are skipped. This can be useful, because it is not possible to guarantee that the test passes, even if everything is correct
          "run_interactive_tests": False,   # if False, tests that require input from the user are skipped

          "modify_config": False,           # if True, some SuMPF config values will be changed and a second test run will be made
          "unload_numpy": False,            # if True, the numpy module will be unimported, so it can be tested, how SuMPF performs without it

          "root_dir": "..",
          "source_dirs": [os.path.join("..", "source"), os.path.join("..", "tests"), os.path.join("..", "tools")],
          "source_dir": os.path.join("..", "source"),
          "test_dir": os.path.join("..", "tests")
         }
sumpf.config.create_config(variables=config)

# parse command line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The test suite for SuMPF.",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="optional arguments for the unit tests:\n" + \
                                            "  -v, --verbose         Verbose output\n" + \
                                            "  -q, --quiet           Minimal output\n" + \
                                            "  -f, --failfast        Stop on first failure\n" + \
                                            "  -c, --catch           Catch control-C and display results\n" + \
                                            "  -b, --buffer          Buffer stdout and stderr during test runs")
    parser.add_argument("--incomplete", dest="run_incomplete_tests", action="store_true", default=False, help="Attempt to run tests whose implementation is incomplete or faulty.")
    parser.add_argument("-w, --write_to_disk", dest="write_to_disk", action="store_true", default=False, help="Run tests that write to the hard drive.")
    parser.add_argument("-g, --gui", dest="test_gui", action="store_true", default=False, help="Run tests for the GUI components.")
    parser.add_argument("-l, --long", dest="run_long_tests", action="store_true", default=False, help="Run tests that take a long time to complete.")
    parser.add_argument("-t, --time_variant", dest="run_time_variant_tests", action="store_true", default=False, help="Run tests whose result is non deterministic. These tests might pass and fail in two consecutive runs without any changes to the code.")
    parser.add_argument("-i, --interactive", dest="run_interactive_tests", action="store_true", default=False, help="Run tests that require input from the user.")
    parser.add_argument("-C, --dont_modify_config", dest="modify_config", action="store_false", default=True, help="Do not modify the configuration to avoid that errors are masked by luckily chosen default values.")
    parser.add_argument("-N, --unload_numpy", dest="unload_numpy", action="store_true", default=False, help="Unload the NumPy library to see how SuMPF performs without it.")
    parser.add_argument("-r, --repetitions", dest="repetitions", action="store", type=int, default=1, metavar="N", help="The number of times, the tests are repeated.")
    args, unittest_args = parser.parse_known_args()
    sys.argv[1:] = unittest_args
    sumpf.config.set("run_incomplete_tests", args.run_incomplete_tests)
    sumpf.config.set("write_to_disk", args.write_to_disk)
    sumpf.config.set("test_gui", args.test_gui)
    sumpf.config.set("run_long_tests", args.run_long_tests)
    sumpf.config.set("run_time_variant_tests", args.run_time_variant_tests)
    sumpf.config.set("run_interactive_tests", args.run_interactive_tests)
    sumpf.config.set("modify_config", args.modify_config)
    sumpf.config.set("unload_numpy", args.unload_numpy)

# unload NumPy if requested
if sumpf.config.get("unload_numpy"):
    common.make_lib_unavailable("numpy")
    common.unload_sumpf()
    common.unload_lib("_common")
    import sumpf
    import _common as common
    sumpf.config.create_config(variables=config)

# print a notification when the gui shall be tested, but is not available
if (not hasattr(sumpf, "gui")) and (sumpf.config.get("test_gui") or sumpf.config.get("run_interactive_tests")):
    sumpf.config.set("test_gui", False)
    sumpf.config.set("run_interactive_tests", False)
    print("Tests of the GUI and interactive tests are skipped because of a missing library.")

# import the tests
from base import *
from data import *
from examples import *
from gui import *
from helper import *
from modules import *
from other import *

# define the configuration modifications
def modify_config():
    if sumpf.config.get("modify_config"):
        sumpf.config.set("default_samplingrate", sumpf.config.get("default_samplingrate") + 13.6)
        sumpf.config.set("default_signal_length", sumpf.config.get("default_signal_length") + 7)
        sumpf.config.set("default_frequency", sumpf.config.get("default_frequency") / 1.9)
        sumpf.config.set("caching", not sumpf.config.get("caching"))
modify_config()


# run the tests
if __name__ == "__main__":
    print(("Testing %s" % str(sumpf)))
    for i in range(1, args.repetitions):
        unittest.main(exit=False)
        modify_config()
    unittest.main()

