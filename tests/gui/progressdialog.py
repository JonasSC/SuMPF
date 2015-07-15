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

import time
import unittest
import sumpf


class ProgressTester(object):
    def __init__(self):
        self.value = 0.0

    @sumpf.Input(float, "Output")
    def Input(self, value):
        self.value = value
        time.sleep(self.value)

    @sumpf.Output(float)
    def Output(self):
        time.sleep(self.value)
        return self.value



@unittest.skipUnless(sumpf.config.get("test_gui"), "The graphical user interface is not being tested")
class TestProgressDialog(unittest.TestCase):
    """
    A TestCase for the ProgressDialog classes.
    As the Gauge is a part of the ProgressDialog, it is tested as well.
    """
    def test_function(self):
        """
        Runs a simple use case for the progress dialog.
        """
        tester1 = ProgressTester()
        tester2 = ProgressTester()
        tester3 = ProgressTester()
        tester4 = ProgressTester()
        tester5 = ProgressTester()
        sumpf.connect(tester1.Output, tester2.Input)
        sumpf.connect(tester2.Output, tester3.Input)
        sumpf.connect(tester3.Output, tester4.Input)
        sumpf.connect(tester4.Output, tester5.Input)
        indicator = sumpf.progressindicators.ProgressIndicator_All(method=tester1.Input, message="Test")
        dialog = sumpf.gui.ProgressDialog(message="Not Seen", title="Testing the progress dialog")
        sumpf.connect(indicator.GetProgressAsTuple, dialog.SetProgress)
        tester1.Input(0.1)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        dlg = sumpf.gui.ProgressDialog(message="Test")
        self.assertEqual(dlg.SetProgress.GetType(), tuple)
        self.assertEqual(dlg.SetMessage.GetType(), str)

