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

import gc
import unittest

import sumpf
import _common as common

from .exampleclasses import SetMultipleValuesTestClass, ProgressTester


class TestProgressIndicators(unittest.TestCase):
    """
    A TestCase for the ProgressIndicator classes.
    """
    def test_ProgressIndicator_All(self):
        tester1 = ProgressTester(progress=(6, 0, None), testcase=self)
        tester2 = ProgressTester(progress=(6, 1, None), testcase=self)              # tester1.Input done
        sumpf.connect(tester1.CachingOutput, tester2.Trigger)
        tester3 = ProgressTester(progress=(6, 3, None), testcase=self)              # tester2.Trigger & tester2.Output done
        sumpf.connect(tester2.NonCachingOutput, tester3.MultiInput)
        tester4 = ProgressTester(progress=(6, 5, None), testcase=self)              # tester3.MultiInput & tester3.Output done
        sumpf.connect(tester3.CachingOutput, tester4.InputNoObserver)
        progress_indicator = sumpf.progressindicators.ProgressIndicator_All(method=tester1.Input)
        tester1.SetProgressIndicator(progress_indicator)
        tester2.SetProgressIndicator(progress_indicator)
        tester3.SetProgressIndicator(progress_indicator)
        tester4.SetProgressIndicator(progress_indicator)
        tester1.Input(1337)
        self.assertEqual(progress_indicator.GetProgressAsTuple(), (6, 6, None))     # tester4.InputNoObserver done
        self.assertEqual(progress_indicator.GetProgressAsFloat(), 1.0)
        self.assertEqual(progress_indicator.GetProgressAsPercentage(), 100)
        tester1.SetProgress((6, 6, None))
        tester2.SetProgress((6, 6, None))
        tester3.SetProgress((6, 6, None))
        tester1.Input(4711)
        progress_indicator.Destroy()
        del tester1
        del tester2
        del tester3
        del tester4
        gc.collect()
        self.assertEqual(gc.garbage, [])

    def test_ProgressIndicator_Outputs(self):
        tester1 = ProgressTester(progress=(2, 0, None), testcase=self, count_inputs=False)
        tester2 = ProgressTester(progress=(2, 0, None), testcase=self, count_inputs=False)
        sumpf.connect(tester1.CachingOutput, tester2.Trigger)
        tester3 = ProgressTester(progress=(2, 1, None), testcase=self, count_inputs=False)      # tester2.Output done
        sumpf.connect(tester2.NonCachingOutput, tester3.MultiInput)
        tester4 = ProgressTester(progress=(2, 2, None), testcase=self, count_inputs=False)      # tester3.Output done
        sumpf.connect(tester3.CachingOutput, tester4.InputNoObserver)
        progress_indicator = sumpf.progressindicators.ProgressIndicator_Outputs(method=tester1.Input)
        tester1.SetProgressIndicator(progress_indicator)
        tester2.SetProgressIndicator(progress_indicator)
        tester3.SetProgressIndicator(progress_indicator)
        tester4.SetProgressIndicator(progress_indicator)
        tester1.Input(1337)
        self.assertEqual(progress_indicator.GetProgressAsTuple(), (2, 2, None))
        self.assertEqual(progress_indicator.GetProgressAsFloat(), 1.0)
        self.assertEqual(progress_indicator.GetProgressAsPercentage(), 100)
        tester1.SetProgress((2, 2, None))
        tester2.SetProgress((2, 2, None))
        tester3.SetProgress((2, 2, None))
        tester1.Input(4711)
        progress_indicator.Destroy()
        del tester1
        del tester2
        del tester3
        del tester4
        gc.collect()
        self.assertEqual(gc.garbage, [])

    def test_ProgressIndicator_OutputsAndNonObservedInputs(self):
        tester1 = ProgressTester(progress=(3, 0, None), testcase=self, count_inputs=False, count_nonobserved_inputs=True)
        tester2 = ProgressTester(progress=(3, 0, None), testcase=self, count_inputs=False, count_nonobserved_inputs=True)
        sumpf.connect(tester1.CachingOutput, tester2.Trigger)
        tester3 = ProgressTester(progress=(3, 1, None), testcase=self, count_inputs=False, count_nonobserved_inputs=True)   # tester2.Output done
        sumpf.connect(tester2.NonCachingOutput, tester3.MultiInput)
        tester4 = ProgressTester(progress=(3, 2, None), testcase=self, count_inputs=False, count_nonobserved_inputs=True)   # tester3.Output done
        sumpf.connect(tester3.CachingOutput, tester4.InputNoObserver)
        progress_indicator = sumpf.progressindicators.ProgressIndicator_OutputsAndNonObservedInputs(method=tester1.Input)
        tester1.SetProgressIndicator(progress_indicator)
        tester2.SetProgressIndicator(progress_indicator)
        tester3.SetProgressIndicator(progress_indicator)
        tester4.SetProgressIndicator(progress_indicator)
        tester1.Input(1337)
        self.assertEqual(progress_indicator.GetProgressAsTuple(), (3, 3, None))                                             # tester4.InputNoObserver done
        self.assertEqual(progress_indicator.GetProgressAsFloat(), 1.0)
        self.assertEqual(progress_indicator.GetProgressAsPercentage(), 100)
        tester1.SetProgress((3, 3, None))
        tester2.SetProgress((3, 3, None))
        tester3.SetProgress((3, 3, None))
        tester1.Input(4711)
        progress_indicator.Destroy()
        del tester1
        del tester2
        del tester3
        del tester4
        gc.collect()
        self.assertEqual(gc.garbage, [])

    def test_setting_to_different_connectors(self):
        for m in ["Input", "Trigger", "MultiInput"]:
            tester1 = ProgressTester(progress=(3, 0, None), testcase=self)
            tester2 = ProgressTester(progress=(3, 2, None), testcase=self)
            sumpf.connect(tester1.CachingOutput, tester2.Input)
            progress_indicator = sumpf.progressindicators.ProgressIndicator_All(method=getattr(tester1, m))
            tester1.SetProgressIndicator(progress_indicator)
            tester2.SetProgressIndicator(progress_indicator)
            getattr(tester1, m)(1337)

    def test_message(self):
        tester1 = ProgressTester(progress=(1, 0, "Test"), testcase=self, count_inputs=False)
        tester2 = ProgressTester(progress=(1, 1, "ProgressTester.NonCachingOutput has just finished"), testcase=self, count_inputs=False)
        sumpf.connect(tester1.NonCachingOutput, tester2.Input)
        progress_indicator = sumpf.progressindicators.ProgressIndicator_Outputs(method=tester1.Input, message="Test")
        tester1.SetProgressIndicator(progress_indicator)
        tester2.SetProgressIndicator(progress_indicator)
        tester1.Input(1337)

    def test_set_multiple_values(self):
        """
        Tests the set_multiple_values function when a progress_indicator is given.
        Most assertions will be don in the SetMultipleValuesTestClass and
        ProgressTester classes.
        """
        # test with single Inputs
        testobject = SetMultipleValuesTestClass(testcase=self)
        progress_tester = ProgressTester(progress=(5, 4, "SetMultipleValuesTestClass.GetState has just finished"), testcase=self, count_inputs=False)
        sumpf.connect(testobject.GetState, progress_tester.Input)
        testobject.Start()
        progress_indicator = sumpf.progressindicators.ProgressIndicator_All(message="smv")
        testobject.SetProgressIndicator(progress_indicator)
        progress_tester.SetProgressIndicator(progress_indicator)
        sumpf.set_multiple_values(pairs=[(testobject.SetValue1, 37.9),
                                         (testobject.SetValue2, "Broccoli"),
                                         (testobject.TriggerValue3,)],
                                  progress_indicator=progress_indicator)
        # test with a MultiInput
        sumpf.set_multiple_values(pairs=[(testobject.AddValue4, 1),
                                         (testobject.AddValue4, 2),
                                         (testobject.AddValue4, 3)],
                                  progress_indicator=progress_indicator)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        tester = ProgressTester(progress=(1, 0, None), testcase=self)
        for p in [sumpf.progressindicators.ProgressIndicator_All,
                  sumpf.progressindicators.ProgressIndicator_Outputs,
                  sumpf.progressindicators.ProgressIndicator_OutputsAndNonObservedInputs]:
            pi = p(method=tester.InputNoObserver)
            self.assertEqual(pi.Report.GetType(), sumpf.internal.Connector)
            common.test_connection_observers(testcase=self,
                                             inputs=[pi.Report],
                                             noinputs=[],
                                             output=pi.GetProgressAsTuple)
            common.test_connection_observers(testcase=self,
                                             inputs=[pi.Report],
                                             noinputs=[],
                                             output=pi.GetProgressAsFloat)
            common.test_connection_observers(testcase=self,
                                             inputs=[pi.Report],
                                             noinputs=[],
                                             output=pi.GetProgressAsPercentage)

